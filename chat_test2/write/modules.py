"""四个核心模块实现"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
import re
from datetime import datetime

from utils import FileManager, ModelManager, JsonStorage
from prompt_config import PromptManager


@dataclass
class OutlineSection:
    """大纲章节"""
    id: str
    title: str
    summary: str
    order: int
    sub_sections: List[Dict] = field(default_factory=list)
    estimated_words: int = 0
    characters: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)


@dataclass
class DetailOutline:
    """详细细纲"""
    section_id: str
    title: str
    scenes: List[Dict]  # 场景列表
    transitions: List[str]  # 转场描述
    key_events: List[str]  # 关键事件
    emotional_arc: str  # 情感弧线
    pace: str  # 节奏


@dataclass
class StoryFrame:
    """故事固定帧"""
    frame_id: str
    scene_id: str
    timestamp: str
    characters_present: List[Dict]  # 在场角色及状态
    location: Dict[str, Any]
    environment: Dict[str, Any]
    objects: List[Dict]  # 物品列表
    current_action: str
    dialogue: List[Dict]  # 对话列表
    inner_thoughts: List[str]  # 内心独白
    sensory_details: Dict[str, str]  # 感官细节


class OutlineModule:
    """模块1: 主体拆解为大纲"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.output_dir = os.path.join(project_path, "output", "outlines")
        self.model_manager = ModelManager("outline_generator")
        self.file_manager = FileManager()
        self.prompt_manager = PromptManager()
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_outline(self, story_concept: str, **kwargs) -> Dict[str, Any]:
        """生成故事大纲"""
        print("开始生成故事大纲...")
        
        # 构建提示词数据
        prompt_data = {
            "concept": story_concept,
            "additional_requirements": kwargs.get('requirements', '无')
        }
        
        # 使用PromptManager获取提示词
        prompt = self.prompt_manager.get_prompt("outline_generation", prompt_data)
        system_prompt = self.prompt_manager.get_system_prompt("outline_generation")
        
        if not prompt:
            raise ValueError("无法获取大纲生成提示词")
        
        # 调用模型
        response = self.model_manager.call_model(prompt, system_prompt=system_prompt, response_format={"type": "json_object"})
        # 提取JSON
        try:
            outline_data = self._parse_outline_response(response)
        except ValueError as e:
            print(f"大纲生成失败: {e}")
            raise ValueError(f"generate_outline方法失败：{str(e)}")
        
        # 保存大纲
        outline_file = os.path.join(self.output_dir, f"outline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.file_manager.write_json(outline_file, outline_data)
        
        print(f"大纲已保存: {outline_file}")
        return outline_data
    

    
    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """解析模型响应"""
        try:
            # 尝试提取JSON
            data = self.model_manager.extract_json(response)
            if not data:
                raise ValueError("JSON解析失败：无法从响应中提取有效数据")
            
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
    
    def _create_default_outline(self, concept: str) -> Dict[str, Any]:
        """创建默认大纲结构"""
        return {
            "title": concept[:20] + "...",
            "concept": concept,
            "parts": [
                {
                    "part_title": "开端",
                    "chapters": [
                        {
                            "id": "ch_1",
                            "title": "故事开始",
                            "summary": "介绍主角和背景",
                            "estimated_words": 1000,
                            "characters": ["主角"],
                            "locations": ["起始场景"]
                        }
                    ]
                }
            ]
        }


class DetailOutlineModule:
    """模块2: 大纲拆解为细纲"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.output_dir = os.path.join(project_path, "output", "details")
        self.model_manager = ModelManager("detail_generator")
        self.file_manager = FileManager()
        self.prompt_manager = PromptManager()
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_details(self, outline_data: Dict[str, Any], chapter_id: str, 
                        previous_chapters: List[Dict] = None, 
                        next_chapters: List[Dict] = None,
                        existing_details: List[Dict] = None) -> Dict[str, Any]:
        """为指定章节生成详细细纲，包含上下文信息"""
        print(f"为章节 {chapter_id} 生成详细细纲...")
        
        # 查找章节
        chapter = self._find_chapter(outline_data, chapter_id)
        if not chapter:
            print(f"未找到章节: {chapter_id}")
            return {}
        
        # 构建上下文信息
        context_info = self._build_context_info(chapter, outline_data, previous_chapters, next_chapters, existing_details)
        
        # 构建提示词数据
        prompt_data = {
            "context_info": context_info,
            "title": chapter.get("title", "未命名章节"),
            "summary": chapter.get("summary", ""),
            "characters": ", ".join(str(c) for c in chapter.get("characters", [])),
            "locations": ", ".join(str(c) for c in chapter.get("locations", [])),
            "words": chapter.get("estimated_words", 0)
        }
        
        # 使用PromptManager获取提示词
        prompt = self.prompt_manager.get_prompt("detail_generation", prompt_data)
        system_prompt = self.prompt_manager.get_system_prompt("detail_generation")
        
        if not prompt:
            raise ValueError("无法获取细纲生成提示词")
        
        # 调用模型
        response = self.model_manager.call_model(prompt, system_prompt=system_prompt, response_format={"type": "json_object"})
        
        # 解析响应
        try:
            detail_data = self._parse_detail_response(response, chapter)
        except ValueError as e:
            print(f"细纲生成失败: {e}")
            raise ValueError(f"generate_details方法失败：{str(e)}")
        
        # 清理章节ID中的非法字符
        clean_chapter_id = re.sub(r'[<>:"/\\|?*]', '_', chapter_id)
        
        # 保存细纲
        detail_file = os.path.join(self.output_dir, f"detail_{clean_chapter_id}_{datetime.now().strftime('%H%M%S')}.json")
        self.file_manager.write_json(detail_file, detail_data)
        
        print(f"细纲已保存: {detail_file}")
        return detail_data
    
    def _find_chapter(self, outline_data: Dict[str, Any], chapter_id: str) -> Optional[Dict[str, Any]]:
        """查找指定章节"""
        for part in outline_data.get("parts", []):
            for chapter in part.get("chapters", []):
                if chapter.get("id") == chapter_id:
                    return chapter
        return None
    

    
    def _build_context_info(self, current_chapter: Dict[str, Any], outline_data: Dict[str, Any], 
                           previous_chapters: List[Dict] = None, 
                           next_chapters: List[Dict] = None,
                           existing_details: List[Dict] = None) -> str:
        """构建上下文信息"""
        context_parts = []
# 故事概述
        context_parts.append(f"故事概述：{outline_data.get('title', '未命名故事')} - {outline_data.get('concept', '')}")
        
        # 前一章节信息
        if previous_chapters:
            prev_info = []
            for i, chapter in enumerate(previous_chapters[-2:]):  # 最近2个章节
                prev_info.append(f"{chapter.get('title', '')}: {chapter.get('summary', '')}")
            if prev_info:
                context_parts.append("前一章节信息：" + " | ".join(prev_info))
        
        # 下一章节信息
        if next_chapters:
            next_info = []
            for i, chapter in enumerate(next_chapters[:2]):  # 后续2个章节
                next_info.append(f"{chapter.get('title', '')}: {chapter.get('summary', '')}")
            if next_info:
                context_parts.append("下一章节信息：" + " | ".join(next_info))
        
        # 已有细纲信息
        if existing_details:
            existing_info = []
            for detail in existing_details:
                existing_info.append(f"{detail.get('title', '')} - {len(detail.get('scenes', []))}个场景")
            if existing_info:
                context_parts.append("已有细纲：" + ", ".join(existing_info))
        
        return "\n".join(context_parts) if context_parts else "无上下文信息"
    
    def _parse_detail_response(self, response: str, chapter: Dict[str, Any]) -> Dict[str, Any]:
        """解析细纲响应"""
        try:
            data = self.model_manager.extract_json(response)
            if not data:
                raise ValueError("JSON解析失败：无法从响应中提取有效数据")
            
            # 处理列表类型响应（如果模型返回了数组）
            if isinstance(data, list):
                print(f"警告：模型返回了列表类型，尝试提取第一个元素")
                if len(data) > 0:
                    data = data[0]  # 取第一个元素作为字典
                else:
                    raise ValueError("JSON解析失败：列表为空")
            
            if not isinstance(data, dict):
                raise ValueError(f"JSON解析失败：期望字典类型，但得到 {type(data).__name__}")
            
            # 验证必要字段
            required_fields = ["section_id", "title", "scenes"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"JSON解析失败：缺少必要字段 '{field}'")
            
            # 验证scenes字段
            if not isinstance(data.get("scenes"), list):
                raise ValueError(f"JSON解析失败：scenes字段应为列表类型，但得到 {type(data.get('scenes')).__name__}")
            
            # 确保section_id正确
            data["section_id"] = chapter.get("id", data.get("section_id", "unknown"))
            
            return data
            
        except Exception as e:
            print(f"解析细纲响应时出错: {e}")
            print(f"原始响应内容: {response[:500]}...")
            # 记录完整的解析失败内容到文件
            import logging
            logger = logging.getLogger("modules")
            logger.error(f"细纲解析失败: {e}")
            logger.error(f"完整响应内容:\n{response}")
            raise ValueError(f"_parse_detail_response方法解析失败：{str(e)}")


class FrameModule:
    """模块3: 细纲拆解为固定帧"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.output_dir = os.path.join(project_path, "output", "frames")
        self.data_dir = os.path.join(project_path, "data")
        self.model_manager = ModelManager("frame_generator")
        self.file_manager = FileManager()
        self.storage = JsonStorage(self.data_dir)
        self.prompt_manager = PromptManager()
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_frames(self, detail_data: Dict[str, Any], scene_id: str,
                       previous_scenes: List[Dict] = None,
                       next_scenes: List[Dict] = None,
                       existing_frames: List[Dict] = None,
                       outline_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """为指定场景生成固定帧，包含上下文信息"""
        print(f"为场景 {scene_id} 生成固定帧...")
        
        # 查找场景
        scene = self._find_scene(detail_data, scene_id)
        if not scene:
            print(f"未找到场景: {scene_id}")
            return []
        
        # 构建上下文信息
        context_info = self._build_frame_context_info(scene, detail_data, previous_scenes, next_scenes, existing_frames, outline_data)
        
        # 构建提示词数据
        prompt_data = {
            "context_info": context_info,
            "scene_title": scene.get("scene_title", "未命名场景"),
            "scene_description": scene.get("description", ""),
            "characters": ", ".join(str(c) for c in scene.get("characters_involved", [])),
            "location": scene.get("location", "未知地点"),
            "events": ", ".join(str(sc) for sc in scene.get("key_events", [])),
            "tone": scene.get("emotional_tone", "中性")
        }
        
        # 使用PromptManager获取提示词
        prompt = self.prompt_manager.get_prompt("frame_generation", prompt_data)
        system_prompt = self.prompt_manager.get_system_prompt("frame_generation")
        
        if not prompt:
            raise ValueError("无法获取固定帧生成提示词")
        
        # 调用模型
        response = self.model_manager.call_model(prompt, system_prompt=system_prompt, response_format={"type": "json_object"})
        
        # 解析响应
        try:
            frames_data = self._parse_frames_response(response, scene)
        except ValueError as e:
            print(f"固定帧生成失败: {e}")
            raise ValueError(f"generate_frames方法失败：{str(e)}")
        
        # 保存固定帧
        for frame in frames_data:
            # 清理frame_id中的非法字符
            clean_frame_id = re.sub(r'[<>:"/\\|?*]', '_', frame['frame_id'])
            frame_file = os.path.join(self.output_dir, f"frame_{clean_frame_id}.json")
            self.file_manager.write_json(frame_file, frame)
            
            # 提取并保存角色、地点等信息
            # self._extract_and_save_entities(frame)
        
        print(f"已生成 {len(frames_data)} 个固定帧")
        return frames_data
    
    def _build_frame_context_info(self, scene: Dict[str, Any], detail_data: Dict[str, Any],
                                previous_scenes: List[Dict], next_scenes: List[Dict],
                                existing_frames: List[Dict], outline_data: Dict[str, Any]) -> str:
        """构建固定帧生成的上下文信息"""
        context_parts = []
        
        # 添加前序场景信息
        if previous_scenes:
            prev_context = "前序场景："
            for prev_scene in previous_scenes[-3:]:  # 最近3个场景
                prev_context += f"{prev_scene.get('scene_title', '')}（{prev_scene.get('description', '')[:50]}...）；"
            context_parts.append(prev_context)
        
        # 添加后续场景信息
        if next_scenes:
            next_context = "后续场景："
            for next_scene in next_scenes[:3]:  # 最近3个后续场景
                next_context += f"{next_scene.get('scene_title', '')}（{next_scene.get('description', '')[:50]}...）；"
            context_parts.append(next_context)
        
        # 添加现有固定帧信息
        if existing_frames:
            frame_context = f"已有固定帧：{len(existing_frames)}个"
            context_parts.append(frame_context)
        
        # 添加大纲信息
        if outline_data:
            outline_context = f"大纲：{outline_data.get('title', '')} - {outline_data.get('description', '')[:100]}..."
            context_parts.append(outline_context)
        
        return "\n".join(context_parts)
    
    def _find_scene(self, detail_data: Dict[str, Any], scene_id: str) -> Optional[Dict[str, Any]]:
        """在细纲数据中查找指定场景"""
        for scene in detail_data.get('scenes', []):
            if scene.get('scene_id') == scene_id:
                return scene
        return None
    
    def _create_frames_for_scene(self, scene: Dict[str, Any], detail_data: Dict[str, Any],
                              previous_scenes: List[Dict] = None,
                              next_scenes: List[Dict] = None,
                              existing_frames: List[Dict] = None,
                              outline_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """为场景创建固定帧，包含上下文信息"""
        # 构建上下文信息
        context_info = self._build_frame_context_info(scene, detail_data, previous_scenes, next_scenes, existing_frames, outline_data)
        
        # 构建提示词数据
        prompt_data = {
            "context_info": context_info,
            "scene_title": scene.get("scene_title", "未命名场景"),
            "scene_description": scene.get("description", ""),
            "characters": ", ".join(str(c) for c in scene.get("characters_involved", [])),
            "location": scene.get("location", "未知地点"),
            "events": ", ".join(str(sc) for sc in scene.get("key_events", [])),
            "tone": scene.get("emotional_tone", "中性")
        }
        
        # 使用PromptManager获取提示词
        prompt = self.prompt_manager.get_prompt("frame_generation", prompt_data)
        system_prompt = self.prompt_manager.get_system_prompt("frame_generation")
        
        if not prompt:
            raise ValueError("无法获取固定帧生成提示词")
        
        # 调用模型
        response = self.model_manager.call_model(prompt, system_prompt=system_prompt, response_format={"type": "json_object"})
        
        # 解析响应
        frames_data = self._parse_frames_response(response, scene)
        
        return frames_data
    

    
    def _build_frame_context_info(self, current_scene: Dict[str, Any], detail_data: Dict[str, Any],
                                 previous_scenes: List[Dict] = None,
                                 next_scenes: List[Dict] = None,
                                 existing_frames: List[Dict] = None,
                                 outline_data: Dict[str, Any] = None) -> str:
        """构建固定帧上下文信息"""
        context_parts = []
        
        # 章节信息
        context_parts.append(f"章节：{detail_data.get('title', '未命名章节')}")
        context_parts.append(f"章节概要：{detail_data.get('emotional_arc', '')}")
        
        # 前一场景信息
        if previous_scenes:
            prev_info = []
            for i, scene in enumerate(previous_scenes[-2:]):  # 最近2个场景
                prev_info.append(f"{scene.get('scene_title', '')}: {scene.get('description', '')[:50]}...")
            if prev_info:
                context_parts.append("前一场景：" + " | ".join(prev_info))
        
        # 下一场景信息
        if next_scenes:
            next_info = []
            for i, scene in enumerate(next_scenes[:2]):  # 后续2个场景
                next_info.append(f"{scene.get('scene_title', '')}: {scene.get('description', '')[:50]}...")
            if next_info:
                context_parts.append("下一场景：" + " | ".join(next_info))
        
        # 已有固定帧信息
        if existing_frames:
            frame_info = []
            for frame in existing_frames:
                frame_info.append(f"{frame.get('timestamp', '')} - {frame.get('current_action', '')[:30]}...")
            if frame_info:
                context_parts.append("已有固定帧：" + ", ".join(frame_info))
        
        # 大纲信息
        if outline_data:
            context_parts.append(f"故事主题：{outline_data.get('title', '')}")
            context_parts.append(f"故事概念：{outline_data.get('concept', '')[:100]}...")
        
        return "\n".join(context_parts) if context_parts else "无上下文信息"
    
    def _parse_frames_response(self, response: str, scene: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析固定帧生成响应"""
        try:
            data = json.loads(response)
            
            # 验证响应结构
            if 'frames' not in data:
                raise ValueError("响应中缺少'frames'字段")
            
            frames = data['frames']
            if not isinstance(frames, list):
                raise ValueError("'frames'字段必须是列表")
            
            # 验证每个帧的结构
            required_fields = ['frame_id', 'frame_title', 'description', 'characters_present',
                             'location', 'key_actions', 'emotional_tone', 'climax_point']
            
            for i, frame in enumerate(frames):
                for field in required_fields:
                    if field not in frame:
                        raise ValueError(f"帧 {i} 缺少字段: {field}")
                
                # 确保frame_id唯一
                frame['frame_id'] = f"{scene.get('scene_id', 'scene')}_frame_{i+1}"
            
            return frames
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {e}")
        except Exception as e:
            raise ValueError(f"响应解析失败: {e}")
    
    def _process_frame(self, frame: Dict[str, Any], scene: Dict[str, Any], frame_index: int) -> Dict[str, Any]:
        """处理单个帧数据"""
        # 确保每个帧都有scene_id
        frame["scene_id"] = scene.get("scene_id", "unknown")
        
        # 验证和清理frame_id
        if "frame_id" not in frame:
            frame["frame_id"] = f"frame_{frame_index + 1}"
        else:
            # 清理frame_id中的非法字符
            frame_id = str(frame["frame_id"]).strip()
            # 移除换行符、制表符等空白字符
            frame_id = re.sub(r'\s+', '_', frame_id)
            # 移除文件名非法字符
            frame_id = re.sub(r'[<>:"/\\|?*，。！？]', '', frame_id)
            # 限制长度并确保不为空
            frame_id = frame_id[:50] if frame_id else f"frame_{frame_index + 1}"
            frame["frame_id"] = frame_id
        
        return frame
    
    def _create_default_frame(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """创建默认固定帧"""
        return {
            "frame_id": "frame_1",
            "scene_id": scene.get("scene_id", "unknown"),
            "timestamp": "场景开始",
            "characters_present": [
                {
                    "character_id": "char_1",
                    "name": scene.get("characters_involved", ["未知角色"])[0] if scene.get("characters_involved") else "未知角色",
                    "position": "场景中心",
                    "action": "站立",
                    "emotion": "中性",
                    "dialogue_line": ""
                }
            ],
            "location": {
                "name": scene.get("location", "未知地点"),
                "description": "默认地点描述",
                "lighting": "正常",
                "sounds": [],
                "smells": []
            },
            "environment": {
                "weather": "晴朗",
                "time_of_day": "白天",
                "temperature": "舒适",
                "atmosphere": "平静"
            },
            "objects": [],
            "current_action": "场景开始",
            "dialogue": [],
            "inner_thoughts": [],
            "sensory_details": {
                "visual": "默认视觉描述",
                "auditory": "安静",
                "olfactory": "无特殊气味",
                "tactile": "正常"
            }
        }
    
    def _extract_and_save_entities(self, frame: Dict[str, Any]):
        """从帧中提取并保存实体信息"""
        # 保存角色
        for char in frame.get("characters_present", []):
            char_id = char.get("character_id", f"char_{hash(char.get('name', 'unknown'))}")
            self.storage.save_entity("characters", char_id, char)
        
        # 保存地点
        location = frame.get("location", {})
        if location:
            loc_id = f"loc_{hash(location.get('name', 'unknown'))}"
            self.storage.save_entity("locations", loc_id, location)
        
        # 保存环境
        environment = frame.get("environment", {})
        if environment:
            env_id = f"env_{hash(frame.get('scene_id', 'unknown'))}"
            self.storage.save_entity("environments", env_id, environment)
        
        # 保存物品
        for obj in frame.get("objects", []):
            obj_id = obj.get("object_id", f"obj_{hash(obj.get('name', 'unknown'))}")
            self.storage.save_entity("items", obj_id, obj)


class WritingModule:
    """模块4: 固定帧扩写为文章"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.output_dir = os.path.join(project_path, "output", "chapters")
        self.model_manager = ModelManager("writing_generator")
        self.file_manager = FileManager()
        self.prompt_manager = PromptManager()
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def expand_frame(self, frame_data: Dict[str, Any], writing_style: str = "文学",
                    previous_frames: List[Dict] = None,
                    next_frames: List[Dict] = None,
                    existing_writings: List[str] = None,
                    scene_data: Dict[str, Any] = None,
                    detail_data: Dict[str, Any] = None,
                    outline_data: Dict[str, Any] = None) -> str:
        """将固定帧扩写为文章段落，包含上下文信息"""
        print(f"扩写固定帧 {frame_data.get('frame_id', 'unknown')}...")
        
        # 构建上下文信息
        context_info = self._build_writing_context_info(frame_data, previous_frames, 
                                                       next_frames, existing_writings,
                                                       scene_data, detail_data, outline_data)
        
        # 构建提示词数据
        prompt_data = {
            "context_info": context_info,
            "writing_style": writing_style,
            "frame_title": frame_data.get('frame_title', '未命名帧'),
            "frame_description": frame_data.get('description', ''),
            "characters_present": ', '.join(str(c) for c in frame_data.get('characters_present', [])),
            "location": frame_data.get('location', '未知地点'),
            "key_actions": frame_data.get('key_actions', ''),
            "emotional_tone": frame_data.get('emotional_tone', '中性'),
            "climax_point": frame_data.get('climax_point', False)
        }
        
        # 使用PromptManager获取提示词
        prompt = self.prompt_manager.get_prompt("writing_expansion", prompt_data)
        system_prompt = self.prompt_manager.get_system_prompt("writing_expansion")
        
        if not prompt:
            raise ValueError("无法获取扩写提示词")
        
        # 调用模型
        response = self.model_manager.call_model(prompt, system_prompt=system_prompt, response_format={"type": "text"})
        
        # 清理和格式化文本
        expanded_text = self._clean_writing_response(response)
        
        # 保存扩写结果
        chapter_file = os.path.join(self.output_dir, f"chapter_{frame_data.get('frame_id', 'unknown')}.txt")
        self.file_manager.write_text(chapter_file, expanded_text)
        
        print(f"扩写已保存: {chapter_file}")
        return expanded_text
    
    def _build_writing_context_info(self, frame: Dict[str, Any], previous_frames: List[Dict],
                                  next_frames: List[Dict], existing_writings: List[Dict],
                                  scene_data: Dict[str, Any], detail_data: Dict[str, Any],
                                  outline_data: Dict[str, Any]) -> str:
        """构建扩写的上下文信息"""
        context_parts = []
        
        # 添加前序帧信息
        if previous_frames:
            prev_context = "前序帧："
            for prev_frame in previous_frames[-2:]:  # 最近2个帧
                prev_context += f"{prev_frame.get('frame_title', '')}（{prev_frame.get('description', '')[:50]}...）；"
            context_parts.append(prev_context)
        
        # 添加后续帧信息
        if next_frames:
            next_context = "后续帧："
            for next_frame in next_frames[:2]:  # 最近2个后续帧
                next_context += f"{next_frame.get('frame_title', '')}（{next_frame.get('description', '')[:50]}...）；"
            context_parts.append(next_context)
        
        # 添加现有扩写信息
        if existing_writings:
            writing_context = f"已有扩写：{len(existing_writings)}个"
            context_parts.append(writing_context)
        
        # 添加场景信息
        if scene_data:
            scene_context = f"场景：{scene_data.get('scene_title', '')} - {scene_data.get('description', '')[:100]}..."
            context_parts.append(scene_context)
        
        # 添加细纲信息
        if detail_data:
            detail_context = f"细纲：{detail_data.get('title', '')} - {detail_data.get('description', '')[:100]}..."
            context_parts.append(detail_context)
        
        # 添加大纲信息
        if outline_data:
            outline_context = f"大纲：{outline_data.get('title', '')} - {outline_data.get('description', '')[:100]}..."
            context_parts.append(outline_context)
        
        return "\n".join(context_parts)
    
    def _build_writing_context_info(self, current_frame: Dict[str, Any],
                                   previous_frames: List[Dict] = None,
                                   next_frames: List[Dict] = None,
                                   existing_writings: List[str] = None,
                                   scene_data: Dict[str, Any] = None,
                                   detail_data: Dict[str, Any] = None,
                                   outline_data: Dict[str, Any] = None) -> str:
        """构建扩写上下文信息"""
        context_parts = []
        
        # 前一固定帧信息
        if previous_frames:
            prev_info = []
            for i, frame in enumerate(previous_frames[-2:]):  # 最近2个固定帧
                prev_info.append(f"{frame.get('timestamp', '')} - {frame.get('current_action', '')[:30]}...")
            if prev_info:
                context_parts.append("前一固定帧：" + " | ".join(prev_info))
        
        # 下一固定帧信息
        if next_frames:
            next_info = []
            for i, frame in enumerate(next_frames[:2]):  # 后续2个固定帧
                next_info.append(f"{frame.get('timestamp', '')} - {frame.get('current_action', '')[:30]}...")
            if next_info:
                context_parts.append("下一固定帧：" + " | ".join(next_info))
        
        # 已有扩写内容
        if existing_writings:
            writing_info = []
            for i, writing in enumerate(existing_writings[-2:]):  # 最近2个扩写
                writing_info.append(f"段落{i+1}: {writing[:50]}...")
            if writing_info:
                context_parts.append("已有扩写：" + " | ".join(writing_info))
        
        # 场景信息
        if scene_data:
            context_parts.append(f"场景：{scene_data.get('scene_title', '')}")
            context_parts.append(f"场景描述：{scene_data.get('description', '')[:100]}...")
        
        # 章节信息
        if detail_data:
            context_parts.append(f"章节：{detail_data.get('title', '未命名章节')}")
            context_parts.append(f"章节概要：{detail_data.get('emotional_arc', '')[:100]}...")
        
        # 大纲信息
        if outline_data:
            context_parts.append(f"故事主题：{outline_data.get('title', '')}")
            context_parts.append(f"故事概念：{outline_data.get('concept', '')[:100]}...")
        
        return "\n".join(context_parts) if context_parts else "无上下文信息"
    
    def _clean_writing_response(self, response: str) -> str:
        """清理扩写响应"""
        # 移除可能的标记和多余空格
        cleaned = response.strip()
        
        # 确保以段落形式
        if not cleaned.startswith((' ', '\t', '\n')):
            cleaned = '  ' + cleaned
        
        return cleaned


def test_modules():
    """测试模块功能"""
    project_path = "test_project"
    
    # 创建测试目录
    import shutil
    if os.path.exists(project_path):
        shutil.rmtree(project_path)
    
    # 测试大纲模块
    print("测试大纲模块...")
    outline_module = OutlineModule(project_path)
    outline = outline_module.generate_outline("一个关于勇者击败恶龙的故事")
    print(f"生成大纲: {outline.get('title', '无标题')}")
    
    # 测试细纲模块
    print("\n测试细纲模块...")
    if outline.get("parts"):
        chapter_id = outline["parts"][0]["chapters"][0]["id"]
        detail_module = DetailOutlineModule(project_path)
        detail = detail_module.generate_details(outline, chapter_id)
        print(f"生成细纲: {detail.get('title', '无标题')}")
        
        # 测试固定帧模块
        print("\n测试固定帧模块...")
        if detail.get("scenes"):
            scene_id = detail["scenes"][0]["scene_id"]
            frame_module = FrameModule(project_path)
            frames = frame_module.generate_frames(detail, scene_id)
            print(f"生成固定帧: {len(frames)} 个")
            
            # 测试扩写模块
            print("\n测试扩写模块...")
            if frames:
                writing_module = WritingModule(project_path)
                expanded = writing_module.expand_frame(frames[0])
                print(f"扩写结果长度: {len(expanded)} 字符")
    
    # 清理测试目录
    if os.path.exists(project_path):
        shutil.rmtree(project_path)
    
    print("\n模块测试完成")


if __name__ == "__main__":
    test_modules()