"""模型管理器 - 实际调用API"""

import json
import os
import requests
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """模型配置"""
    api_key: str = ""
    model_name: str = "deepseek-ai/DeepSeek-V3.2"
    api_url: str = "https://api.siliconflow.cn/v1/chat/completions"
    temperature: float = 0.7
    max_tokens: int = 12000
    top_p: float = 0.9
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1
    timeout: int = 300  # 秒


class APIModelManager:
    """API模型管理器"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.history: List[Dict[str, Any]] = []
        
        # 验证配置
        if not self.config.api_key:
            logger.warning("未设置API Key，模型调用将使用模拟模式")
    
    def set_config(self, **kwargs):
        """更新模型配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def call_model(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """调用模型API"""
        # 如果未设置API Key，使用模拟模式
        if not self.config.api_key:
            logger.info("使用模拟模式（未设置API Key）")
            return self._mock_response(prompt)
        
        # 构建消息
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
        
        # 构建请求参数
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"调用模型: {self.config.model_name}")
            logger.debug(f"请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            response = requests.post(
                self.config.api_url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 提取响应内容
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # 记录历史
                self.history.append({
                    "timestamp": time.time(),
                    "prompt": prompt,
                    "response": content,
                    "config": asdict(self.config),
                    "kwargs": kwargs
                })
                
                logger.info(f"模型调用成功，响应长度: {len(content)}")
                return content
            else:
                logger.error(f"API响应格式异常: {result}")
                return self._mock_response(prompt)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求错误: {e}")
            return self._mock_response(prompt)
        except json.JSONDecodeError as e:
            logger.error(f"响应解析错误: {e}")
            return self._mock_response(prompt)
        except Exception as e:
            logger.error(f"模型调用异常: {e}")
            return self._mock_response(prompt)
    
    def call_with_template(self, template_name: str, template_data: Dict[str, Any], 
                          system_prompt: str = "", **kwargs) -> str:
        """使用模板调用模型"""
        from .prompt_config import PromptManager
        
        # 获取模板
        prompt_manager = PromptManager()
        prompt = prompt_manager.get_prompt(template_name, template_data)
        
        if not prompt:
            logger.error(f"未找到模板: {template_name}")
            return ""
        
        # 获取系统提示词
        if not system_prompt:
            system_prompt = prompt_manager.get_system_prompt(template_name)
        
        # 调用模型
        return self.call_model(prompt, system_prompt, **kwargs)
    
    def extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取JSON"""
        import re
        
        try:
            # 尝试查找JSON代码块
            json_pattern = r'```json\s*(.*?)\s*```'
            matches = re.findall(json_pattern, text, re.DOTALL | re.IGNORECASE)
            
            if matches:
                return json.loads(matches[0])
            
            # 尝试查找普通JSON
            json_pattern2 = r'\{.*\}'
            matches2 = re.findall(json_pattern2, text, re.DOTALL)
            
            if matches2:
                # 尝试从后往前找到最长的有效JSON
                for match in reversed(matches2):
                    try:
                        return json.loads(match)
                    except json.JSONDecodeError:
                        continue
            
            # 如果都没有，尝试直接解析整个文本
            return json.loads(text)
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON提取失败: {e}")
            return None
        except Exception as e:
            logger.warning(f"JSON提取异常: {e}")
            return None
    
    def _mock_response(self, prompt: str) -> str:
        """模拟模型响应（用于测试）"""
        logger.info(f"模拟响应: {prompt[:50]}...")
        
        # 根据prompt类型返回模拟响应
        if "大纲" in prompt or "outline" in prompt.lower():
            return self._mock_outline_response()
        elif "细纲" in prompt or "detail" in prompt.lower():
            return self._mock_detail_response()
        elif "固定帧" in prompt or "frame" in prompt.lower():
            return self._mock_frame_response()
        elif "扩写" in prompt or "writing" in prompt.lower():
            return self._mock_writing_response()
        else:
            return f"模型响应: {prompt[:100]}...（模拟模式）"
    
    def _mock_outline_response(self) -> str:
        """模拟大纲响应"""
        return json.dumps({
            "title": "勇者传奇",
            "concept": "一个关于勇者击败恶龙的故事",
            "parts": [
                {
                    "part_title": "开端",
                    "chapters": [
                        {
                            "id": "ch_1",
                            "title": "平凡的开始",
                            "summary": "主角亚瑟在村庄过着平静的生活",
                            "estimated_words": 800,
                            "characters": ["亚瑟", "村民"],
                            "locations": ["亚瑟的村庄"]
                        },
                        {
                            "id": "ch_2", 
                            "title": "命运的召唤",
                            "summary": "亚瑟意外发现勇者之剑",
                            "estimated_words": 1200,
                            "characters": ["亚瑟", "梅林"],
                            "locations": ["村庄神庙"]
                        }
                    ]
                }
            ]
        }, ensure_ascii=False, indent=2)
    
    def _mock_detail_response(self) -> str:
        """模拟细纲响应"""
        return json.dumps({
            "section_id": "ch_1",
            "title": "平凡的开始",
            "scenes": [
                {
                    "scene_id": "scene_1",
                    "scene_title": "清晨的村庄",
                    "description": "亚瑟在村庄中开始新的一天",
                    "characters_involved": ["亚瑟", "村民"],
                    "location": "亚瑟的村庄",
                    "key_events": ["亚瑟起床", "与村民打招呼", "开始日常工作"],
                    "emotional_tone": "平静"
                }
            ],
            "transitions": ["时间推移到中午"],
            "key_events": ["亚瑟发现异常"],
            "emotional_arc": "从平静到好奇",
            "pace": "缓慢"
        }, ensure_ascii=False, indent=2)
    
    def _mock_frame_response(self) -> str:
        """模拟固定帧响应"""
        return json.dumps([
            {
                "frame_id": "frame_1",
                "scene_id": "scene_1",
                "timestamp": "清晨6点",
                "characters_present": [
                    {
                        "character_id": "char_1",
                        "name": "亚瑟",
                        "position": "床边",
                        "action": "起床伸懒腰",
                        "emotion": "平静",
                        "dialogue_line": ""
                    }
                ],
                "location": {
                    "name": "亚瑟的小屋",
                    "description": "简陋但整洁的小木屋",
                    "lighting": "清晨的阳光透过窗户",
                    "sounds": ["鸟叫声", "远处的鸡鸣"],
                    "smells": ["木头的香气", "清晨的空气"]
                },
                "environment": {
                    "weather": "晴朗",
                    "time_of_day": "清晨",
                    "temperature": "凉爽",
                    "atmosphere": "宁静"
                },
                "objects": [
                    {
                        "object_id": "obj_1",
                        "name": "木床",
                        "description": "简单的木制床铺",
                        "position": "房间角落",
                        "state": "整洁"
                    }
                ],
                "current_action": "亚瑟从睡梦中醒来",
                "dialogue": [],
                "inner_thoughts": ["又是平静的一天"],
                "sensory_details": {
                    "visual": "阳光在地板上形成光斑",
                    "auditory": "远处传来村庄的声音",
                    "olfactory": "清新的空气",
                    "tactile": "粗糙的亚麻床单"
                }
            }
        ], ensure_ascii=False, indent=2)
    
    def _mock_writing_response(self) -> str:
        """模拟扩写响应"""
        return """清晨的第一缕阳光透过木窗的缝隙，在地板上洒下斑驳的光点。亚瑟缓缓睁开眼，感受到粗糙的亚麻床单贴在皮肤上的触感。他伸了个懒腰，关节发出轻微的响声。

小屋的空气里弥漫着木头的香气，混合着从窗外飘来的清晨的清新气息。远处传来鸡鸣声，还有鸟儿在枝头欢快的歌唱。亚瑟坐起身，揉了揉惺忪的睡眼。

"又是平静的一天。"他心想。这样的早晨已经重复了无数个日夜，村庄的生活就像一条缓慢流淌的小河，波澜不惊。

他穿上简单的布衣，走到窗边。透过窗户，可以看到村庄开始苏醒。炊烟从几户人家的烟囱升起，在清晨的空气中缓缓飘散。亚瑟深吸一口气，准备开始新的一天。

阳光越来越明亮，小屋里的光线也变得更加清晰。亚瑟可以看到空气中的微尘在光柱中飞舞，像是一群微小的精灵。他拿起木桌上的水壶，倒了杯水，清凉的液体顺着喉咙滑下，驱散了最后一丝睡意。

又是一个平凡的开始，在这座宁静的村庄里。亚瑟并不知道，命运的齿轮已经开始转动，而他平静的生活即将迎来翻天覆地的变化。"""
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取调用历史"""
        return self.history
    
    def clear_history(self):
        """清空调用历史"""
        self.history = []
    
    def save_history(self, file_path: str):
        """保存调用历史到文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            logger.info(f"历史已保存: {file_path}")
        except Exception as e:
            logger.error(f"保存历史失败: {e}")


def test_model_manager():
    """测试模型管理器"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 创建模型管理器
    manager = APIModelManager()
    
    # 测试模拟调用
    print("测试模拟调用...")
    response = manager.call_model("生成一个故事大纲")
    print(f"响应长度: {len(response)}")
    print(f"响应预览: {response[:100]}...")
    
    # 测试JSON提取
    print("\n测试JSON提取...")
    json_data = manager.extract_json(response)
    if json_data:
        print(f"成功提取JSON，键: {list(json_data.keys())}")
    
    # 测试历史记录
    print(f"\n调用历史: {len(manager.get_history())} 条")
    
    print("\n模型管理器测试完成")


if __name__ == "__main__":
    test_model_manager()