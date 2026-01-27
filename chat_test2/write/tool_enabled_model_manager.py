"""支持工具调用的模型管理器"""

import json
import os
import re
import time
import requests
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
import logging

from json_repair import repair_json

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """工具调用"""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolMessage:
    """工具消息"""
    role: str = "tool"
    content: str = ""
    tool_call_id: str = ""


@dataclass
class ModelConfig:
    """模型配置"""
    api_key: str = "sk-pdxifqjftnthcnfonzjerkeyiquovxfiupwovvxzhanzdujo"
    model_name: str = "deepseek-ai/DeepSeek-V3.2"
    api_url: str = "https://api.siliconflow.cn/v1/chat/completions"
    temperature: float = 0.7
    max_tokens: int = 12000
    top_p: float = 0.9
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1
    timeout: int = 30000


class SimpleModelCaller:
    """简单的模型调用器，避免循环依赖"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
    
    def call_with_template(self, template_name: str, template_data: Dict[str, Any], 
                          **kwargs) -> str:
        """调用模型处理模板"""
        
        # 导入prompt_manager（延迟导入避免循环依赖）
        from .prompt_manager import PromptManager
        
        # 获取模板
        prompt_manager = PromptManager()
        prompt = prompt_manager.get_prompt(template_name, template_data)
        
        if not prompt:
            logger.error(f"未找到模板: {template_name}")
            return f"错误：未找到模板 {template_name}"
        
        # 获取系统提示词
        system_prompt = prompt_manager.get_system_prompt(template_name)
        
        # 构建请求
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # 调用模型API
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p)
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.config.api_url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"模型调用失败: {e}")
            return f"模型调用失败: {str(e)}"


class Tool:
    """工具基类"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> str:
        """执行工具"""
        raise NotImplementedError("子类必须实现execute方法")


class CreateCharacterTool(Tool):
    """创建人物工具"""
    
    def __init__(self, character_model_manager=None):
        super().__init__(
            name="create_character",
            description="创建新的人物角色，包括基本信息、性格特征、背景故事等",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "人物姓名"},
                    "role": {"type": "string", "description": "人物角色（主角/配角/反派等）"},
                    "basic_info": {"type": "object", "description": "基本信息（年龄、性别、外貌等）"},
                    "personality": {"type": "object", "description": "性格特征"},
                    "background": {"type": "string", "description": "背景故事"},
                    "story_requirements": {"type": "string", "description": "故事需求"}
                },
                "required": ["name", "role"]
            }
        )
        self.character_dir = "characters"
        os.makedirs(self.character_dir, exist_ok=True)
        
        # 使用传入的模型管理器或创建简单的模型调用器
        self.character_model_manager = character_model_manager or SimpleModelCaller()
    
    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            name = arguments.get("name", "")
            role = arguments.get("role", "配角")
            basic_info = arguments.get("basic_info", {})
            personality = arguments.get("personality", {})
            background = arguments.get("background", "")
            story_requirements = arguments.get("story_requirements", "")
            
            # 构建人物创建模板数据
            template_data = {
                "name": name,
                "role": role,
                "basic_info": basic_info,
                "personality": personality,
                "background": background,
                "story_requirements": story_requirements
            }
            
            # 调用专门的人物创建模型
            logger.info(f"调用专门的人物创建模型来创建角色: {name}")
            
            # 使用character_creation模板调用模型
            character_result = self.character_model_manager.call_with_template(
                template_name="character_creation",
                template_data=template_data,
                temperature=0.8,
                max_tokens=4000
            )
            
            # 解析模型返回的人物数据
            try:
                # 尝试从模型回复中提取JSON格式的人物数据
                character_data = self._extract_character_data(character_result, name, role)
            except Exception as e:
                logger.warning(f"人物数据解析失败，使用基础信息: {e}")
                # 如果解析失败，使用基础信息创建人物
                character_data = self._create_basic_character_data(name, role, basic_info, personality, background, story_requirements)
            
            # 保存人物数据
            character_file = os.path.join(self.character_dir, f"{name}.json")
            with open(character_file, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"人物创建成功: {name}, 文件路径: {character_file}")
            
            return json.dumps({
                "success": True,
                "character_name": name,
                "file_path": character_file,
                "character_data": character_data,
                "model_response": character_result
            })
            
        except Exception as e:
            logger.error(f"创建人物失败: {str(e)}")
            return json.dumps({"error": f"创建人物失败: {str(e)}"})
    
    def _extract_character_data(self, model_response: str, name: str, role: str) -> Dict[str, Any]:
        """从模型回复中提取人物数据"""
        try:
            # 尝试直接解析JSON
            if "{" in model_response and "}" in model_response:
                # 提取JSON部分
                json_start = model_response.find("{")
                json_end = model_response.rfind("}") + 1
                json_str = model_response[json_start:json_end]
                
                character_data = json.loads(json_str)
                
                # 确保包含必要字段
                character_data.setdefault("name", name)
                character_data.setdefault("role", role)
                character_data.setdefault("created_at", time.time())
                
                return character_data
            else:
                # 如果无法提取JSON，使用基础数据
                raise ValueError("模型回复中未找到有效的JSON数据")
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}")
            # 尝试修复JSON
            try:
                from json_repair import repair_json
                fixed_json = repair_json(model_response, ensure_ascii=False)
                character_data = json.loads(fixed_json)
                
                character_data.setdefault("name", name)
                character_data.setdefault("role", role)
                character_data.setdefault("created_at", time.time())
                
                return character_data
            except:
                raise ValueError("JSON修复失败")
    
    def _create_basic_character_data(self, name: str, role: str, basic_info: Dict[str, Any], 
                                   personality: Dict[str, Any], background: str, story_requirements: str) -> Dict[str, Any]:
        """创建基础人物数据"""
        return {
            "name": name,
            "role": role,
            "basic_info": basic_info,
            "personality": personality,
            "background": background,
            "story_requirements": story_requirements,
            "created_at": time.time(),
            "relationships": {},
            "character_arc": "待补充的人物成长弧线",
            "strengths": [],
            "weaknesses": [],
            "motivations": [],
            "quirks": [],
            "appearance": {
                "height": "待补充",
                "build": "待补充",
                "hair": "待补充",
                "eyes": "待补充",
                "distinctive_features": []
            },
            "skills": [],
            "current_status": {
                "health": "良好",
                "mood": "平静",
                "goal": "待补充"
            }
        }


class ReadCharacterTool(Tool):
    """读取人物工具"""
    
    def __init__(self):
        super().__init__(
            name="read_character",
            description="读取已存在的人物角色信息",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "人物姓名"},
                    "character_file": {"type": "string", "description": "人物文件路径（可选）"}
                },
                "required": ["name"]
            }
        )
        self.character_dir = "characters"
    
    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            name = arguments.get("name", "")
            character_file = arguments.get("character_file", "")
            
            # 确定文件路径
            if character_file:
                file_path = character_file
            else:
                file_path = os.path.join(self.character_dir, f"{name}.json")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return json.dumps({
                    "error": f"人物文件不存在: {file_path}",
                    "suggestion": "请先使用create_character工具创建该人物"
                })
            
            # 读取人物数据
            with open(file_path, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            return json.dumps({
                "success": True,
                "character_name": name,
                "file_path": file_path,
                "character_data": character_data
            })
            
        except Exception as e:
            return json.dumps({"error": f"读取人物失败: {str(e)}"})


class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        self.register_tool(CreateCharacterTool())
        self.register_tool(ReadCharacterTool())
    
    def register_tool(self, tool: Tool):
        """注册新工具"""
        self.tools[tool.name] = tool
        logger.info(f"工具注册成功: {tool.name}")
    
    def unregister_tool(self, tool_name: str):
        """注销工具"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"工具注销成功: {tool_name}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def execute_tool(self, tool_call: ToolCall) -> ToolMessage:
        """执行工具调用"""
        tool_name = tool_call.name
        if tool_name not in self.tools:
            error_msg = json.dumps({"error": f"工具不存在: {tool_name}"})
            return ToolMessage(content=error_msg, tool_call_id=tool_call.id)
        
        try:
            tool = self.tools[tool_name]
            result = tool.execute(tool_call.arguments)
            return ToolMessage(content=result, tool_call_id=tool_call.id)
        except Exception as e:
            error_msg = json.dumps({"error": f"工具执行失败: {str(e)}"})
            return ToolMessage(content=error_msg, tool_call_id=tool_call.id)
    
    def list_tools(self) -> List[str]:
        """列出所有可用工具名称"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具详细信息"""
        if tool_name in self.tools:
            return self.tools[tool_name].to_dict()
        return None


class ToolEnabledModelManager:
    """支持工具调用的模型管理器"""
    
    def __init__(self,  model_name: str = "default",config: Optional[ModelConfig] = None, tool_manager: Optional[ToolManager] = None):
        self.model_name = model_name
        self.config = config or ModelConfig()
        self.tool_manager = tool_manager or ToolManager()
        self.history: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, Any]] = []
        
        # 验证配置
        if not self.config.api_key:
            logger.warning("未设置API Key，模型调用将使用模拟模式")

    def extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取JSON，包含中文标点符号的后处理"""
        fixed_text = repair_json(text, ensure_ascii=False)
        return json.loads(fixed_text)

    def set_config(self, **kwargs):
        """更新模型配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def call_model_with_tools(self, prompt: str, system_prompt: str = "", 
                             max_iterations: int = 5, **kwargs) -> str:
        """
        支持工具调用的模型调用方法
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            max_iterations: 最大迭代次数（防止无限循环）
            **kwargs: 其他参数
            
        Returns:
            str: 最终的模型回复
        """
        # 构建初始消息
        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # 添加对话历史
        messages.extend(self.conversation_history)
        
        # 迭代处理工具调用
        for iteration in range(max_iterations):
            logger.info(f"工具调用迭代 {iteration + 1}/{max_iterations}")
            
            # 构建工具列表
            tools = self.tool_manager.get_available_tools()
            
            # 调用模型
            response_data = self._call_model_api(messages, tools, **kwargs)
            
            if "error" in response_data:
                logger.error(f"模型调用失败: {response_data['error']}")
                return response_data["error"]
            
            # 添加模型回复到消息历史
            model_message = {
                "role": "assistant",
                "content": response_data.get("content", "")
            }
            
            # 如果有工具调用，处理工具调用
            tool_calls = response_data.get("tool_calls", [])
            if tool_calls:
                # 添加工具调用信息到消息
                model_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments, ensure_ascii=False)
                        }
                    } for tc in tool_calls
                ]
                
                messages.append(model_message)
                
                # 处理工具调用
                tool_messages = self._process_tool_calls(tool_calls)
                messages.extend(tool_messages)
                
                # 继续下一次迭代
                continue
            else:
                # 没有工具调用，返回最终回复
                messages.append(model_message)
                
                # 更新对话历史
                self.conversation_history.extend([
                    {"role": "user", "content": prompt},
                    model_message
                ])
                
                # 记录历史
                self.history.append({
                    "timestamp": time.time(),
                    "prompt": prompt,
                    "response": response_data.get("content", ""),
                    "config": asdict(self.config),
                    "kwargs": kwargs,
                    "iterations": iteration + 1
                })
                
                return response_data.get("content", "")
        
        # 达到最大迭代次数
        error_msg = f"达到最大迭代次数 {max_iterations}，可能陷入无限循环"
        logger.error(error_msg)
        return error_msg
    
    def _call_model_api(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], 
                       **kwargs) -> Dict[str, Any]:
        """调用模型API"""
        # 构建请求参数
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p)
        }
        
        # 如果有工具，添加工具参数
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        # 重试机制
        max_retries = 3
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"调用模型: {self.config.model_name} (尝试 {attempt + 1}/{max_retries})")
                print(json.dumps(payload, ensure_ascii=False, indent=2))

                response = requests.post(
                    self.config.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                
                response_data = response.json()
                
                # 解析响应
                return self._parse_response(response_data)
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"API请求错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                
            except Exception as e:
                last_exception = e
                logger.error(f"模型调用异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
        
        # 所有重试都失败
        error_msg = f"模型调用失败，经过 {max_retries} 次重试后仍然无法成功"
        logger.error(error_msg)
        return {"error": error_msg}
    
    def _parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析模型响应"""
        try:
            choice = response_data["choices"][0]
            message = choice["message"]
            finish_reason = choice.get("finish_reason", "unknown")
            
            result = {
                "content": message.get("content", ""),
                "finish_reason": finish_reason,
                "tool_calls": [],
                "usage": response_data.get("usage", {})
            }
            
            # 解析工具调用
            if "tool_calls" in message and message["tool_calls"]:
                tool_calls = []
                for tc_data in message["tool_calls"]:
                    tool_call = ToolCall(
                        id=tc_data["id"],
                        name=tc_data["function"]["name"],
                        arguments=json.loads(tc_data["function"]["arguments"])
                    )
                    tool_calls.append(tool_call)
                result["tool_calls"] = tool_calls
            
            return result
            
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            error_msg = f"响应解析失败: {e}"
            logger.error(f"{error_msg}\n原始响应: {response_data}")
            return {"error": error_msg}
    
    def _process_tool_calls(self, tool_calls: List[ToolCall]) -> List[Dict[str, Any]]:
        """处理工具调用并返回工具消息"""
        tool_messages = []
        
        for tool_call in tool_calls:
            logger.info(f"执行工具调用: {tool_call.name}")
            
            # 执行工具
            tool_message = self.tool_manager.execute_tool(tool_call)
            
            # 创建工具消息
            tool_msg = {
                "role": "tool",
                "content": tool_message.content,
                "tool_call_id": tool_call.id
            }
            
            tool_messages.append(tool_msg)
            
            # 记录执行结果
            try:
                result_data = json.loads(tool_message.content)
                if "error" in result_data:
                    logger.warning(f"工具执行失败: {result_data['error']}")
                else:
                    logger.info(f"工具执行成功: {tool_call.name}")
            except:
                logger.warning("工具执行结果解析失败")
        
        return tool_messages
    
    def call_with_template(self, template_name: str, template_data: Dict[str, Any], 
                          system_prompt: str = "", **kwargs) -> str:
        """使用模板调用模型，支持工具调用"""
        from .prompt_config import PromptManager
        
        # 获取模板
        prompt_manager = PromptManager()
        prompt = prompt_manager.get_prompt(template_name, template_data)
        
        if not prompt:
            logger.error(f"未找到模板: {template_name}")
            raise ValueError(f"未找到模板: {template_name}")
        
        # 获取系统提示词
        if not system_prompt:
            system_prompt = prompt_manager.get_system_prompt(template_name)
        
        # 调用模型
        return self.call_model_with_tools(prompt, system_prompt, **kwargs)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取调用历史"""
        return self.history
    
    def clear_history(self):
        """清空调用历史"""
        self.history = []
        self.conversation_history = []
    
    def save_history(self, file_path: str):
        """保存调用历史到文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            logger.info(f"历史已保存: {file_path}")
        except Exception as e:
            logger.error(f"保存历史失败: {e}")
    
    def get_tool_usage_statistics(self) -> Dict[str, Any]:
        """获取工具使用统计"""
        tool_stats = {}
        
        for record in self.history:
            iterations = record.get("iterations", 0)
            if iterations > 1:
                # 有工具调用
                tool_stats["total_tool_calls"] = tool_stats.get("total_tool_calls", 0) + (iterations - 1)
        
        # 统计每个工具的使用次数
        for tool_name in self.tool_manager.list_tools():
            tool_stats[tool_name] = 0
        
        return tool_stats
    
    def create_character_directly(self, name: str, role: str = "配角", 
                                 basic_info: Dict[str, Any] = None,
                                 personality: Dict[str, Any] = None,
                                 background: str = "") -> Dict[str, Any]:
        """直接创建人物（绕过模型调用）"""
        try:
            # 直接调用创建人物工具
            tool_call = ToolCall(
                id=f"direct_create_{int(time.time())}",
                name="create_character",
                arguments={
                    "name": name,
                    "role": role,
                    "basic_info": basic_info or {},
                    "personality": personality or {},
                    "background": background
                }
            )
            
            tool_message = self.tool_manager.execute_tool(tool_call)
            result = json.loads(tool_message.content)
            
            if "error" in result:
                logger.error(f"直接创建人物失败: {result['error']}")
                return {"error": result["error"]}
            
            logger.info(f"直接创建人物成功: {name}")
            return result
            
        except Exception as e:
            error_msg = f"直接创建人物异常: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def read_character_directly(self, name: str, character_file: str = "") -> Dict[str, Any]:
        """直接读取人物（绕过模型调用）"""
        try:
            # 直接调用读取人物工具
            tool_call = ToolCall(
                id=f"direct_read_{int(time.time())}",
                name="read_character",
                arguments={
                    "name": name,
                    "character_file": character_file
                }
            )
            
            tool_message = self.tool_manager.execute_tool(tool_call)
            result = json.loads(tool_message.content)
            
            if "error" in result:
                logger.error(f"直接读取人物失败: {result['error']}")
                return {"error": result["error"]}
            
            logger.info(f"直接读取人物成功: {name}")
            return result
            
        except Exception as e:
            error_msg = f"直接读取人物异常: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}


def test_tool_enabled_model_manager():
    """测试工具调用模型管理器"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 创建工具调用模型管理器
    manager = ToolEnabledModelManager()
    
    # 测试工具调用
    print("测试工具调用模型管理器...")
    
    # 测试创建人物
    print("\n1. 测试创建人物...")
    response = manager.call_model_with_tools(
        prompt="请创建一个名为'亚瑟'的主角人物，他是一个年轻的勇者",
        system_prompt="你是一个小说创作助手，可以使用工具来创建和读取人物。"
    )
    print(f"响应: {response}")
    
    # 测试读取人物
    print("\n2. 测试读取人物...")
    response = manager.call_model_with_tools(
        prompt="请读取刚才创建的亚瑟的人物信息",
        system_prompt="你是一个小说创作助手，可以使用工具来创建和读取人物。"
    )
    print(f"响应: {response}")
    
    print("\n测试完成")


if __name__ == "__main__":
    test_tool_enabled_model_manager()