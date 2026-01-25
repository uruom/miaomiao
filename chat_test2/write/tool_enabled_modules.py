"""支持工具调用的增强模块"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
import re
from datetime import datetime

from utils import FileManager, JsonStorage
from prompt_config import PromptManager
from tool_enabled_model_manager import ToolEnabledModelManager


@dataclass
class Character:
    """人物角色"""
    name: str
    role: str
    basic_info: Dict[str, Any]
    personality: Dict[str, Any]
    background: str
    relationships: Dict[str, Any]
    character_arc: str
    strengths: List[str]
    weaknesses: List[str]
    motivations: List[str]
    quirks: List[str]


class CharacterModule:
    """人物角色管理模块 - 支持工具调用"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.data_dir = os.path.join(project_path, "data", "characters")
        self.model_manager = ToolEnabledModelManager()
        self.file_manager = FileManager()
        
        os.makedirs(self.data_dir, exist_ok=True)
    
    def create_character(self, name: str, role: str = "配角", 
                        basic_info: Dict[str, Any] = None,
                        personality: Dict[str, Any] = None,
                        background: str = "",
                        story_requirements: str = "") -> Dict[str, Any]:
        """创建新的人物角色"""
        print(f"开始创建人物: {name}")
        
        # 构建提示词
        prompt = f"""
请创建一个名为'{name}'的{role}角色。

基本信息：{json.dumps(basic_info or {}, ensure_ascii=False)}
性格特征：{json.dumps(personality or {}, ensure_ascii=False)}
背景故事：{background}
故事需求：{story_requirements}

请使用create_character工具来创建这个人物。
"""
        
        system_prompt = """你是一个专业的人物角色设计师。请使用create_character工具来创建生动、立体的人物角色。

人物应该包含以下信息：
- 基本信息（年龄、性别、外貌、职业等）
- 性格特征（性格特点、行为习惯、价值观等）
- 详细背景故事
- 人际关系
- 人物成长弧线
- 优点/特长
- 缺点/弱点
- 动机和目标
- 独特习惯或特征"""
        
        # 调用模型（会自动使用工具）
        response = self.model_manager.call_model_with_tools(
            prompt=prompt,
            system_prompt=system_prompt
        )
        
        print(f"人物创建完成: {name}")
        
        # 解析响应，提取人物信息
        try:
            # 尝试从响应中提取人物信息
            character_data = self._extract_character_info(response, name)
            
            # 保存人物数据
            character_file = os.path.join(self.data_dir, f"{name}.json")
            self.file_manager.write_json(character_file, character_data)
            
            print(f"人物数据已保存: {character_file}")
            return character_data
            
        except Exception as e:
            print(f"人物信息提取失败: {e}")
            # 返回默认结构
            return {
                "name": name,
                "role": role,
                "basic_info": basic_info or {},
                "personality": personality or {},
                "background": background,
                "relationships": {},
                "character_arc": "待补充",
                "strengths": [],
                "weaknesses": [],
                "motivations": [],
                "quirks": []
            }
    
    def get_character(self, name: str) -> Optional[Dict[str, Any]]:
        """获取人物信息"""
        print(f"获取人物信息: {name}")
        
        # 首先检查本地文件
        character_file = os.path.join(self.data_dir, f"{name}.json")
        if os.path.exists(character_file):
            try:
                character_data = self.file_manager.read_json(character_file)
                print(f"从本地文件读取人物: {name}")
                return character_data
            except Exception as e:
                print(f"读取本地人物文件失败: {e}")
        
        # 如果本地没有，使用工具读取
        prompt = f"请读取人物'{name}'的信息"
        system_prompt = "你是一个小说创作助手，可以使用read_character工具来读取人物信息。"
        
        response = self.model_manager.call_model_with_tools(
            prompt=prompt,
            system_prompt=system_prompt
        )
        
        print(f"人物信息获取完成: {name}")
        
        # 尝试解析响应
        try:
            character_data = self._extract_character_info(response, name)
            return character_data
        except Exception as e:
            print(f"人物信息解析失败: {e}")
            return None
    
    def list_characters(self) -> List[str]:
        """列出所有已创建的人物"""
        characters = []
        
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    character_name = filename[:-5]  # 移除.json扩展名
                    characters.append(character_name)
        
        return sorted(characters)
    
    def update_character(self, name: str, updates: Dict[str, Any]) -> bool:
        """更新人物信息"""
        try:
            character_file = os.path.join(self.data_dir, f"{name}.json")
            
            if not os.path.exists(character_file):
                print(f"人物文件不存在: {character_file}")
                return False
            
            # 读取现有数据
            with open(character_file, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # 更新数据
            character_data.update(updates)
            character_data["updated_at"] = time.time()
            
            # 保存更新后的数据
            with open(character_file, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=2)
            
            print(f"人物信息更新成功: {name}")
            return True
            
        except Exception as e:
            print(f"更新人物信息失败: {e}")
            return False
    
    def delete_character(self, name: str) -> bool:
        """删除人物"""
        try:
            character_file = os.path.join(self.data_dir, f"{name}.json")
            
            if not os.path.exists(character_file):
                print(f"人物文件不存在: {character_file}")
                return False
            
            os.remove(character_file)
            print(f"人物删除成功: {name}")
            return True
            
        except Exception as e:
            print(f"删除人物失败: {e}")
            return False
    
    def _extract_character_info(self, response: str, character_name: str) -> Dict[str, Any]:
        """从模型响应中提取人物信息"""
        # 尝试解析JSON响应
        try:
            # 查找JSON格式的人物信息
            json_pattern = r'\{[^{}]*"name"[^{}]*\}'
            matches = re.findall(json_pattern, response, re.DOTALL)
            
            if matches:
                for match in matches:
                    try:
                        data = json.loads(match)
                        if data.get("name") == character_name:
                            return data
                    except:
                        continue
            
            # 如果没有找到JSON，尝试从文本中提取关键信息
            character_data = {
                "name": character_name,
                "role": "",
                "basic_info": {},
                "personality": {},
                "background": "",
                "relationships": {},
                "character_arc": "",
                "strengths": [],
                "weaknesses": [],
                "motivations": [],
                "quirks": []
            }
            
            # 简单的文本解析（可以根据需要扩展）
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if "角色" in line and character_name in line:
                    character_data["role"] = line.replace("角色", "").replace(character_name, "").strip()
                elif "背景" in line:
                    character_data["background"] = line.replace("背景", "").strip()
            
            return character_data
            
        except Exception as e:
            print(f"人物信息提取异常: {e}")
            raise e


class ToolEnabledOutlineModule:
    """支持工具调用的大纲生成模块"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.output_dir = os.path.join(project_path, "output", "outlines")
        self.model_manager = ToolEnabledModelManager()
        self.file_manager = FileManager()
        self.prompt_manager = PromptManager()
        self.character_module = CharacterModule(project_path)
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_outline_with_characters(self, story_concept: str, 
                                       character_names: List[str] = None,
                                       **kwargs) -> Dict[str, Any]:
        """生成包含人物角色的故事大纲"""
        print("开始生成包含人物的故事大纲...")
        
        # 处理人物信息
        characters_info = ""
        if character_names:
            characters_info = "主要人物：\n"
            for name in character_names:
                character = self.character_module.get_character(name)
                if character:
                    characters_info += f"- {name}: {character.get('role', '未知角色')} - {character.get('background', '背景待补充')}\n"
                else:
                    characters_info += f"- {name}: 角色待创建\n"
        
        # 构建提示词数据
        prompt_data = {
            "concept": story_concept,
            "characters_info": characters_info,
            "additional_requirements": kwargs.get('requirements', '无')
        }
        
        # 使用PromptManager获取提示词
        prompt = self.prompt_manager.get_prompt("outline_generation", prompt_data)
        system_prompt = self.prompt_manager.get_system_prompt("outline_generation")
        
        if not prompt:
            raise ValueError("无法获取大纲生成提示词")
        
        # 增强系统提示词，支持工具调用
        enhanced_system_prompt = f"""{system_prompt}

你可以使用以下工具来辅助创作：
- create_character: 创建新的人物角色
- read_character: 读取已存在的人物信息

如果故事需要新的人物，请先创建这些人物。如果已有相关人物，请读取他们的信息来丰富故事。"""
        
        # 调用模型（支持工具调用）
        response = self.model_manager.call_model_with_tools(
            prompt=prompt,
            system_prompt=enhanced_system_prompt,
            response_format={"type": "json_object"}
        )
        
        # 提取JSON
        try:
            outline_data = self._parse_outline_response(response)
        except ValueError as e:
            print(f"大纲生成失败: {e}")
            raise ValueError(f"generate_outline_with_characters方法失败：{str(e)}")
        
        # 保存大纲
        outline_file = os.path.join(self.output_dir, f"outline_with_characters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.file_manager.write_json(outline_file, outline_data)
        
        print(f"大纲已保存: {outline_file}")
        return outline_data
    
    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """解析模型响应"""
        try:
            # 尝试提取JSON
            data = json.loads(response)
            
            if not isinstance(data, dict):
                raise ValueError(f"JSON解析失败：期望字典类型，但得到 {type(data).__name__}")
            
            # 验证必要字段
            required_fields = ["title", "concept", "parts"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"JSON解析失败：缺少必要字段 '{field}'")
            
            # 验证parts字段
            if not isinstance(data.get("parts"), list):
                raise ValueError(f"JSON解析失败：parts字段应为列表类型，但得到 {type(data.get('parts')).__name__}")
            
            return data
            
        except Exception as e:
            print(f"解析大纲失败: {e}")
            raise ValueError(f"_parse_outline_response方法解析失败：{str(e)}")


class ToolEnabledWritingModule:
    """支持工具调用的写作模块"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.output_dir = os.path.join(project_path, "output", "chapters")
        self.model_manager = ToolEnabledModelManager()
        self.file_manager = FileManager()
        self.prompt_manager = PromptManager()
        self.character_module = CharacterModule(project_path)
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def write_chapter_with_characters(self, outline_data: Dict[str, Any], 
                                    chapter_id: str,
                                    character_names: List[str] = None) -> str:
        """基于人物信息创作章节内容"""
        print(f"开始创作章节 {chapter_id}...")
        
        # 查找章节
        chapter = self._find_chapter(outline_data, chapter_id)
        if not chapter:
            raise ValueError(f"未找到章节: {chapter_id}")
        
        # 构建人物信息
        characters_context = ""
        if character_names:
            characters_context = "本章涉及人物：\n"
            for name in character_names:
                character = self.character_module.get_character(name)
                if character:
                    characters_context += f"- {name}: {character.get('role', '')} - {character.get('personality', {}).get('summary', '性格待补充')}\n"
        
        # 构建提示词数据
        prompt_data = {
            "chapter_title": chapter.get("title", ""),
            "chapter_summary": chapter.get("summary", ""),
            "characters": characters_context,
            "locations": ", ".join(chapter.get("locations", [])),
            "estimated_words": chapter.get("estimated_words", 0)
        }
        
        # 使用PromptManager获取提示词
        prompt = self.prompt_manager.get_prompt("writing_expansion", prompt_data)
        system_prompt = self.prompt_manager.get_system_prompt("writing_expansion")
        
        if not prompt:
            raise ValueError("无法获取写作提示词")
        
        # 增强系统提示词，支持工具调用
        enhanced_system_prompt = f"""{system_prompt}

你可以使用以下工具来辅助创作：
- read_character: 读取人物详细信息，确保人物行为一致

请基于人物性格和背景来创作内容，确保人物行为符合其设定。"""
        
        # 调用模型（支持工具调用）
        response = self.model_manager.call_model_with_tools(
            prompt=prompt,
            system_prompt=enhanced_system_prompt
        )
        
        # 保存章节内容
        clean_chapter_id = re.sub(r'[<>:"/\\|?*]', '_', chapter_id)
        chapter_file = os.path.join(self.output_dir, f"chapter_{clean_chapter_id}.txt")
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(response)
        
        print(f"章节内容已保存: {chapter_file}")
        return response
    
    def _find_chapter(self, outline_data: Dict[str, Any], chapter_id: str) -> Optional[Dict[str, Any]]:
        """查找指定章节"""
        for part in outline_data.get("parts", []):
            for chapter in part.get("chapters", []):
                if chapter.get("id") == chapter_id:
                    return chapter
        return None


def test_tool_enabled_modules():
    """测试工具调用模块"""
    import tempfile
    
    # 创建临时项目目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print("=== 测试工具调用模块 ===")
        
        # 测试人物模块
        print("\n1. 测试人物模块...")
        character_module = CharacterModule(temp_dir)
        
        # 创建人物
        character = character_module.create_character(
            name="亚瑟",
            role="主角",
            basic_info={"age": 18, "gender": "男", "appearance": "金发碧眼"},
            personality={"traits": ["勇敢", "善良", "坚定"]},
            background="来自边境村庄的年轻勇者"
        )
        print(f"创建人物成功: {character['name']}")
        
        # 读取人物
        character_info = character_module.get_character("亚瑟")
        print(f"读取人物成功: {character_info['name']}")
        
        # 测试大纲模块
        print("\n2. 测试大纲模块...")
        outline_module = ToolEnabledOutlineModule(temp_dir)
        
        outline = outline_module.generate_outline_with_characters(
            story_concept="一个关于勇者亚瑟击败恶龙的故事",
            character_names=["亚瑟"]
        )
        print(f"生成大纲成功: {outline['title']}")
        
        # 测试写作模块
        print("\n3. 测试写作模块...")
        writing_module = ToolEnabledWritingModule(temp_dir)
        
        if outline.get("parts") and outline["parts"][0].get("chapters"):
            chapter_id = outline["parts"][0]["chapters"][0]["id"]
            content = writing_module.write_chapter_with_characters(
                outline_data=outline,
                chapter_id=chapter_id,
                character_names=["亚瑟"]
            )
            print(f"创作章节成功，内容长度: {len(content)}")
        
        print("\n所有测试完成！")


if __name__ == "__main__":
    test_tool_enabled_modules()