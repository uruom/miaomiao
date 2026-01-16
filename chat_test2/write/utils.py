"""工具类 - 提供通用功能"""

import json
import os
import re
import hashlib
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileManager:
    """文件管理工具"""
    
    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """读取JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"文件不存在: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误 {file_path}: {e}")
            return {}
    
    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any], indent: int = 2):
        """写入JSON文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            logger.info(f"已保存: {file_path}")
        except Exception as e:
            logger.error(f"保存失败 {file_path}: {e}")
            raise
    
    @staticmethod
    def read_text(file_path: str) -> str:
        """读取文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"文件不存在: {file_path}")
            return ""
    
    @staticmethod
    def write_text(file_path: str, content: str):
        """写入文本文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"已保存: {file_path}")
        except Exception as e:
            logger.error(f"保存失败 {file_path}: {e}")
            raise
    
    @staticmethod
    def list_files(directory: str, pattern: str = "*.json") -> List[str]:
        """列出目录下的文件"""
        try:
            return [f for f in os.listdir(directory) if f.endswith(pattern.replace("*", ""))]
        except FileNotFoundError:
            logger.warning(f"目录不存在: {directory}")
            return []
    
    @staticmethod
    def generate_hash(content: str) -> str:
        """生成内容哈希值"""
        return hashlib.md5(content.encode()).hexdigest()


class JsonStorage:
    """JSON存储管理器"""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.types = ["characters", "items", "locations", "environments", "misc"]
        
        # 创建存储目录
        for storage_type in self.types:
            os.makedirs(os.path.join(storage_dir, storage_type), exist_ok=True)
    
    def save_entity(self, entity_type: str, entity_id: str, data: Dict[str, Any]):
        """保存实体数据"""
        if entity_type not in self.types:
            raise ValueError(f"无效的实体类型: {entity_type}")
        
        file_path = os.path.join(self.storage_dir, entity_type, f"{entity_id}.json")
        FileManager.write_json(file_path, data)
    
    def load_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """加载实体数据"""
        file_path = os.path.join(self.storage_dir, entity_type, f"{entity_id}.json")
        return FileManager.read_json(file_path)
    
    def list_entities(self, entity_type: str) -> List[str]:
        """列出所有实体ID"""
        if entity_type not in self.types:
            return []
        
        directory = os.path.join(self.storage_dir, entity_type)
        files = FileManager.list_files(directory)
        return [f.replace(".json", "") for f in files]
    
    def update_entity(self, entity_type: str, entity_id: str, updates: Dict[str, Any]):
        """更新实体数据"""
        existing = self.load_entity(entity_type, entity_id)
        if not existing:
            existing = {}
        
        existing.update(updates)
        self.save_entity(entity_type, entity_id, existing)
    
    def delete_entity(self, entity_type: str, entity_id: str):
        """删除实体数据"""
        file_path = os.path.join(self.storage_dir, entity_type, f"{entity_id}.json")
        try:
            os.remove(file_path)
            logger.info(f"已删除: {file_path}")
        except FileNotFoundError:
            logger.warning(f"文件不存在: {file_path}")


class ModelManager:
    """模型管理器（兼容接口）"""
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        self.history = []
        
        # 尝试导入实际模型管理器
        try:
            from model_manager import APIModelManager, ModelConfig
            from prompt_config import PromptManager
            
            # 创建配置
            config = ModelConfig()
            self.api_manager = APIModelManager(config)
            self.prompt_manager = PromptManager()
            self.use_api = True
            logger.info(f"使用API模型管理器: {model_name}")
        except ImportError as e:
            logger.warning(f"无法导入API模型管理器，使用模拟模式: {e}")
            self.api_manager = None
            self.prompt_manager = None
            self.use_api = False
    
    def call_model(self, prompt: str, **kwargs) -> str:
        """调用模型"""
        logger.info(f"调用模型 {self.model_name}: {prompt[:50]}...")
        
        if self.use_api and self.api_manager:
            # 使用API管理器
            system_prompt = kwargs.pop('system_prompt', '')
            response = self.api_manager.call_model(prompt, system_prompt, **kwargs)
            print(response)
        else:
            # 使用模拟模式
            response = f"模型响应: {prompt[:100]}...（模拟模式）"
        
        # 记录历史
        self.history.append({
            "prompt": prompt,
            "response": response,
            "kwargs": kwargs
        })
        
        return response
    
    def call_with_template(self, template_name: str, template_data: Dict[str, Any], **kwargs) -> str:
        """使用模板调用模型"""
        if self.use_api and self.api_manager and self.prompt_manager:
            # 使用模板和API
            return self.api_manager.call_with_template(template_name, template_data, **kwargs)
        else:
            # 模拟调用
            logger.info(f"模拟模板调用: {template_name}")
            return f"模板响应: {template_name} - {template_data}"
    
    def extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取JSON，包含中文标点符号的后处理"""
        if self.use_api and self.api_manager:
            # 使用API管理器的增强解析功能
            return self.api_manager.extract_json(text)
        else:
            # 使用改进的本地解析
            return self._local_extract_json(text)
    
    def _local_extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """本地JSON解析，包含中文标点符号修复"""
        try:
            # 首先尝试直接解析（可能已经是有效的JSON）
            try:
                fixed_text = self._fix_json_format(text)
                return json.loads(fixed_text)
            except json.JSONDecodeError:
                pass
            
            # 尝试查找JSON代码块
            json_pattern = r'```json\s*(.*?)\s*```'
            matches = re.findall(json_pattern, text, re.DOTALL | re.IGNORECASE)
            
            if matches:
                json_text = matches[0]
                # 进行后处理修复
                json_text = self._fix_json_format(json_text)
                return json.loads(json_text)
            
            # 尝试查找普通JSON
            json_pattern2 = r'\{.*\}'
            matches2 = re.findall(json_pattern2, text, re.DOTALL)
            
            if matches2:
                # 尝试从后往前找到最长的有效JSON
                for match in reversed(matches2):
                    try:
                        # 进行后处理修复
                        fixed_match = self._fix_json_format(match)
                        return json.loads(fixed_match)
                    except json.JSONDecodeError:
                        continue
            
            # 如果都没有，尝试对整个文本进行后处理
            fixed_text = self._fix_json_format(text)
            return json.loads(fixed_text)
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON提取失败: {e}")
            # 尝试更宽松的解析
            return self._parse_json_with_fallback(text)
        except Exception as e:
            logger.warning(f"JSON提取异常: {e}")
            return None
    
    def _fix_json_format(self, text: str) -> str:
        """修复JSON格式问题，特别是中文标点符号"""
        if not text:
            return text
        
        # 首先，我们需要智能地替换中文标点，但只在JSON结构部分，而不是字符串内容部分
        # 使用正则表达式来识别JSON结构中的标点符号
        
        # 1. 修复JSON键名和值分隔符中的中文标点
        # 匹配模式："键名"后跟中文标点，然后是值
        text = re.sub(r'"([^"]+)"\s*：\s*', r'"\1": ', text)
        
        # 2. 修复JSON结构中的中文逗号（在属性之间）
        # 匹配模式：值后跟中文逗号，然后是下一个属性
        text = re.sub(r'(["\]\dtruefalsenull])\s*，\s*"', r'\1, "', text)
        
        # 3. 修复数组中的中文逗号
        text = re.sub(r'(["\]\dtruefalsenull])\s*，\s*(["\[\]\dtruefalsenull])', r'\1, \2', text)
        
        # 4. 修复中文双引号问题 - 只在JSON结构部分替换，不在字符串内容中替换
        # 先尝试找到JSON结构部分，然后只替换结构中的中文双引号
        
        # 策略：先尝试解析，如果失败再逐步修复
        # 这里我们采用更保守的方法，只修复明显的结构问题
        
        # 5. 修复属性名缺少引号的问题
        text = re.sub(r'(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)
        
        # 6. 修复数组和对象末尾的逗号问题
        text = re.sub(r',\s*([\}\]])', r'\1', text)
        
        # 7. 修复布尔值大小写问题
        text = re.sub(r'\btrue\b', 'true', text, flags=re.IGNORECASE)
        text = re.sub(r'\bfalse\b', 'false', text, flags=re.IGNORECASE)
        text = re.sub(r'\bnull\b', 'null', text, flags=re.IGNORECASE)
        
        # 8. 修复数字格式问题
        text = re.sub(r'\b(\d+)\.(\d+)\b', r'\1.\2', text)
        
        logger.debug(f"修复后的JSON文本: {text[:200]}...")
        return text
    
    def _parse_json_with_fallback(self, text: str) -> Optional[Dict[str, Any]]:
        """使用更宽松的方式解析JSON，作为最后的手段"""
        try:
            # 尝试多种修复策略
            text = self._fix_json_format(text)
            
            # 策略1: 尝试找到最长的可能JSON对象
            json_pattern = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            
            if matches:
                # 选择最长的匹配项
                longest_match = max(matches, key=len)
                return json.loads(longest_match)
            
            # 策略2: 尝试手动构建JSON
            lines = text.split('\n')
            json_data = {}
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().strip('"\'')  # 移除可能的引号
                        value = parts[1].strip().strip('"\'')
                        json_data[key] = value
            
            if json_data:
                return json_data
            
            # 策略3: 如果所有方法都失败，返回None
            return None
            
        except Exception as e:
            logger.warning(f"宽松JSON解析失败: {e}")
            return None
    
    def generate_with_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """使用模板生成内容（兼容旧接口）"""
        return self.call_with_template(template_name, data)
    
    def set_api_config(self, **kwargs):
        """设置API配置"""
        if self.use_api and self.api_manager:
            self.api_manager.set_config(**kwargs)
    
    def get_history(self):
        """获取调用历史"""
        return self.history


class TextProcessor:
    """文本处理工具"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        # 移除多余空格和换行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    @staticmethod
    def split_into_sections(text: str, max_length: int = 1000) -> List[str]:
        """将文本分割成段落"""
        paragraphs = text.split('\n\n')
        sections = []
        current_section = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            if current_length + para_length > max_length and current_section:
                sections.append('\n\n'.join(current_section))
                current_section = [para]
                current_length = para_length
            else:
                current_section.append(para)
                current_length += para_length
        
        if current_section:
            sections.append('\n\n'.join(current_section))
        
        return sections
    
    @staticmethod
    def count_words(text: str) -> int:
        """统计字数"""
        # 简单的中英文单词统计
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        return chinese_chars + english_words


def test_utils():
    """测试工具类"""
    # 测试文件管理器
    fm = FileManager()
    test_data = {"test": "data"}
    fm.write_json("test.json", test_data)
    loaded = fm.read_json("test.json")
    print(f"文件管理器测试: {loaded == test_data}")
    
    # 清理测试文件
    if os.path.exists("test.json"):
        os.remove("test.json")
    
    # 测试JSON存储
    storage = JsonStorage("test_storage")
    storage.save_entity("characters", "hero", {"name": "英雄", "age": 25})
    hero_data = storage.load_entity("characters", "hero")
    print(f"JSON存储测试: {hero_data}")
    
    # 测试模型管理器
    mm = ModelManager("test_model")
    response = mm.call_model("测试消息")
    print(f"模型管理器测试: {response[:50]}...")
    
    # 清理测试目录
    import shutil
    if os.path.exists("test_storage"):
        shutil.rmtree("test_storage")
    
    print("工具类测试完成")


if __name__ == "__main__":
    test_utils()