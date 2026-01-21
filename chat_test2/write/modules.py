"""四个核心模块实现"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
import re
from datetime import datetime

from utils import FileManager, ModelManager, JsonStorage


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
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_outline(self, story_concept: str, **kwargs) -> Dict[str, Any]:
        """生成故事大纲"""
        print("开始生成故事大纲...")
        
        # 构建提示词
        prompt = self._build_outline_prompt(story_concept, kwargs)
        
        # 调用模型
        response = self.model_manager.call_model(prompt, system_prompt="", response_format={"type": "json_object"})
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
    
    def _build_outline_prompt(self, concept: str, kwargs: Dict) -> str:
        """构建大纲生成提示词"""
        template = """
        你是江南，《龙族》作者，擅长写作与构思
        请为以下小说思路生成一个详细的小说大纲：

小说思路：{concept}

要求：
1. 将故事分为6-8个主要部分，每个部分都应有一个或多个大的爆点与高潮，能够留住读者。
2. 每个部分包含6-8卷，同理，每个卷也应有一个或多个大的爆点与高潮，能够留住读者。
3. 为每个卷提供标题和简要描述
4. 估计每个卷的章节数
5. 列出每个卷涉及的主要角色和场景
6. 返回STRICT JSON格式，必须使用：
- 英文引号 ",不要使用中文双引号
- 英文冒号: ,不要使用中文冒号，
- 任何字符串内容中可以包含中文符号，若为json特殊字符请转移，json结构必须是英文标点，不要在Json格式中加入任何不能被解析的字符
请以JSON格式返回，结构如下：
{{
  "title": "故事标题",
  "concept": "故事概念",
  "parts": [
    {{
      "part_title": "部分标题",
      "chapters": [
        {{
          "id": "章节ID",
          "title": "章节标题",
          "summary": "章节概要",
          "estimated_words": 字数,
          "characters": ["角色1", "角色2"],
          "locations": ["场景1", "场景2"]
        }}
      ]
    }}
  ]
}}

附加要求：{additional_requirements}"""
        
        additional = kwargs.get('requirements', '无')
        return template.format(concept=concept, additional_requirements=additional)
    
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
        
        # 构建提示词
        prompt = self._build_detail_prompt(chapter, outline_data, previous_chapters, next_chapters, existing_details)
        
        # 调用模型
        response = self.model_manager.call_model(prompt, system_prompt="", response_format={"type": "json_object"})
        
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
    
    def _build_detail_prompt(self, chapter: Dict[str, Any], outline_data: Dict[str, Any], 
                          previous_chapters: List[Dict] = None, 
                          next_chapters: List[Dict] = None,
                          existing_details: List[Dict] = None) -> str:
        """构建细纲生成提示词，包含上下文信息"""
        
        # 构建上下文信息
        context_info = self._build_context_info(chapter, outline_data, previous_chapters, next_chapters, existing_details)
        
        template = """
        你是江南，《龙族》作者，擅长写作与构思
        请为以下章节生成详细的细纲：

{context_info}

卷信息：
卷题：{title}
概要：{summary}
涉及角色：{characters}
场景：{locations}
预估字数：{words}

请生成包含以下内容的详细细纲：
1. 6-8个具体事件/场景（每个场景大约有3-4个章节），每个场景包含有高潮点，让读者情绪起伏，能让读者产生共鸣。
2. 场景之间的过渡，如何衔接，人物的转变
3. 关键转折点，如何让读者产生共鸣
4. 情感发展弧线
5. 节奏控制
6. 返回STRICT JSON格式，必须使用：
- 英文引号 ",不要使用中文双引号
- 英文冒号: ,不要使用中文冒号，
- 任何字符串内容中可以包含中文符号，若为json特殊字符请转移，json结构必须是英文标点，不要在Json格式中加入任何不能被解析的字符
请以JSON格式返回，结构如下：

以JSON格式返回，结构如下：
{{
  "section_id": "章节ID",
  "title": "章节标题",
  "scenes": [
    {{
      "scene_id": "场景ID",
      "scene_title": "场景标题",
      "description": "场景描述",
      "characters_involved": ["角色"],
      "location": "地点",
      "key_events": ["事件1", "事件2"],
      "emotional_tone": "情感基调"
    }}
  ],
  "transitions": ["过渡描述1", "过渡描述2"],
  "key_events": ["关键事件1", "关键事件2"],
  "emotional_arc": "情感发展描述",
  "pace": "节奏描述（快/慢/中等）"
}}"""
        
        return template.format(
            context_info=context_info,
            title=chapter.get("title", "未命名章节"),
            summary=chapter.get("summary", ""),
            characters=", ".join(str(c) for c in chapter.get("characters", [])),
            locations=", ".join(str(c) for c in chapter.get("locations", [])),
            words=chapter.get("estimated_words", 0)
        )
    
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
        
        # 生成固定帧
        frames = self._create_frames_for_scene(scene, detail_data, previous_scenes, next_scenes, existing_frames, outline_data)
        
        # 保存固定帧
        for frame in frames:
            # 清理frame_id中的非法字符
            clean_frame_id = re.sub(r'[<>:"/\\|?*]', '_', frame['frame_id'])
            frame_file = os.path.join(self.output_dir, f"frame_{clean_frame_id}.json")
            self.file_manager.write_json(frame_file, frame)
            
            # 提取并保存角色、地点等信息
            # self._extract_and_save_entities(frame)
        
        print(f"已生成 {len(frames)} 个固定帧")
        return frames
    
    def _find_scene(self, detail_data: Dict[str, Any], scene_id: str) -> Optional[Dict[str, Any]]:
        """查找指定场景"""
        for scene in detail_data.get("scenes", []):
            if scene.get("scene_id") == scene_id:
                return scene
        return None
    
    def _create_frames_for_scene(self, scene: Dict[str, Any], detail_data: Dict[str, Any],
                              previous_scenes: List[Dict] = None,
                              next_scenes: List[Dict] = None,
                              existing_frames: List[Dict] = None,
                              outline_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """为场景创建固定帧，包含上下文信息"""
        # 构建提示词
        prompt = self._build_frame_prompt(scene, detail_data, previous_scenes, next_scenes, existing_frames, outline_data)
        
        # 调用模型
        response = self.model_manager.call_model(prompt, response_format={"type": "json_object"})
        
        # 解析响应
        frames_data = self._parse_frames_response(response, scene)
        
        return frames_data
    
    def _build_frame_prompt(self, scene: Dict[str, Any], detail_data: Dict[str, Any],
                          previous_scenes: List[Dict] = None,
                          next_scenes: List[Dict] = None,
                          existing_frames: List[Dict] = None,
                          outline_data: Dict[str, Any] = None) -> str:
        """构建固定帧生成提示词，包含上下文信息"""
        
        # 构建上下文信息
        context_info = self._build_frame_context_info(scene, detail_data, previous_scenes, next_scenes, existing_frames, outline_data)
        
        template = """
        你是江南，《龙族》作者，擅长写作与构思
        请为以下场景生成6-8个"章节帧段"，每个帧代表这章中最为高潮，最吸引读者的瞬间：

{context_info}

场景信息：
标题：{scene_title}
描述：{scene_description}
涉及角色：{characters}
地点：{location}
关键事件：{events}
情感基调：{tone}

章节帧要求：
1. 每个章节帧包含该瞬间的完整状态
2. 包括在场角色及其状态（位置、动作、情绪）、环境描述（光线、声音、气味等）、物品状态
3. 当前进行的对话或动作
4. 角色的内心想法，
5. 如何过度到这个高潮帧，该帧前后是如何设计，以及后续描写的指导，如何让读者产生共鸣，如何让这个高潮帧成为下一个高潮的铺垫
6. 返回STRICT JSON格式，必须使用：
- 英文引号 ",不要使用中文双引号
- 英文冒号: ,不要使用中文冒号，
- 任何字符串内容中可以包含中文符号，若为json特殊字符请转移，json结构必须是英文标点，不要在Json格式中加入任何不能被解析的字符
请以JSON格式返回，结构如下：


以JSON数组格式返回，每个固定帧结构如下：
[
  {{
    "frame_id": "帧ID",
    "scene_id": "场景ID",
    "timestamp": "时间描述（如：开场后5分钟）",
    "characters_present": [
      {{
        "character_id": "角色ID",
        "name": "角色名",
        "position": "位置描述",
        "action": "当前动作",
        "emotion": "情绪状态",
        "dialogue_line": "当前对话（如有）"
      }}
    ],
    "location": {{
      "name": "地点名",
      "description": "地点描述",
      "lighting": "光线",
      "sounds": ["声音1", "声音2"],
      "smells": ["气味1", "气味2"]
    }},
    "environment": {{
      "weather": "天气",
      "time_of_day": "时间",
      "temperature": "温度",
      "atmosphere": "氛围"
    }},
    "objects": [
      {{
        "object_id": "物品ID",
        "name": "物品名",
        "description": "物品描述",
        "position": "位置",
        "state": "状态"
      }}
    ],
    "current_action": "当前主要动作描述",
    "dialogue": [
      {{
        "speaker": "说话者",
        "content": "对话内容",
        "tone": "语气"
      }}
    ],
    "inner_thoughts": ["角色1的内心想法", "角色2的内心想法"],
    "sensory_details": {{
      "visual": "视觉细节",
      "auditory": "听觉细节",
      "olfactory": "嗅觉细节",
      "tactile": "触觉细节"
    }}
  }}
]

请确保每个固定帧都是独立的、完整的瞬间描述。"""
        
        return template.format(
            context_info=context_info,
            scene_title=scene.get("scene_title", "未命名场景"),
            scene_description=scene.get("description", ""),
            characters=", ".join(str(c) for c in scene.get("characters_involved", [])),
            location=scene.get("location", "未知地点"),
            events=", ".join(str(sc) for sc in scene.get("key_events", [])),
            tone=scene.get("emotional_tone", "中性")
        )
    
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
        """解析固定帧响应"""
        try:
            data = self.model_manager.extract_json(response)
            if not data:
                raise ValueError("JSON解析失败：无法从响应中提取有效数据")
            
            # 检测是否是细纲数据（错误的数据格式）
            if isinstance(data, dict):
                # 检查是否包含细纲特有的字段
                if ("section_id" in data or "title" in data or "scenes" in data or 
                    "transitions" in data or "emotional_arc" in data):
                    print("错误：模型返回了细纲数据而非固定帧数据")
                    print("这可能是因为模型没有正确理解提示词要求")
                    print(f"原始响应内容: {response[:500]}...")
                    raise ValueError("模型返回了错误的格式（细纲数据而非固定帧数据）")
            
            # 处理不同的返回类型：列表或字典
            frames_data = []
            if isinstance(data, list):
                # 如果是列表，直接使用
                frames_data = data
            elif isinstance(data, dict):
                # 如果是字典，检查是否包含frame_id，如果是单个帧对象
                if "frame_id" in data or "timestamp" in data or "characters_present" in data:
                    frames_data = [data]
                else:
                    # 可能是包含frames键的字典
                    frames_data = data.get("frames", [])
                    if not isinstance(frames_data, list):
                        frames_data = [data]
            else:
                raise ValueError(f"JSON解析失败：期望列表或字典类型，但得到 {type(data).__name__}")
            
            # 确保frames_data是列表且不为空
            if not isinstance(frames_data, list):
                raise ValueError(f"JSON解析失败：frames_data应为列表类型，但得到 {type(frames_data).__name__}")
            
            if len(frames_data) == 0:
                print("错误：frames_data为空列表")
                print(f"原始响应内容: {response[:500]}...")
                raise ValueError("JSON解析失败：frames_data为空列表")
            
            # 确保每个帧都有正确的数据结构
            valid_frames = []
            for i, frame in enumerate(frames_data):
                # 处理嵌套列表的情况（如果frame是列表而不是字典）
                if isinstance(frame, list):
                    print(f"警告：第{i+1}个帧是列表类型，尝试提取其中的字典元素")
                    for sub_frame in frame:
                        if isinstance(sub_frame, dict):
                            # 处理子帧
                            processed_frame = self._process_frame(sub_frame, scene, len(valid_frames))
                            valid_frames.append(processed_frame)
                    continue
                
                # 处理字符串类型的情况（可能是无效数据或格式错误）
                if isinstance(frame, str):
                    print(f"警告：第{i+1}个帧是字符串类型，内容：'{frame[:100]}...'，跳过处理")
                    continue
                
                if not isinstance(frame, dict):
                    print(f"警告：第{i+1}个帧是{type(frame).__name__}类型，跳过处理")
                    continue
                
                # 处理单个帧
                processed_frame = self._process_frame(frame, scene, len(valid_frames))
                valid_frames.append(processed_frame)
            
            if not valid_frames:
                print("错误：没有有效的帧数据")
                print(f"原始响应内容: {response[:500]}...")
                raise ValueError("JSON解析失败：没有有效的帧数据")
            
            return valid_frames
            
        except Exception as e:
            print(f"解析固定帧响应时出错: {e}")
            print(f"原始响应内容: {response[:500]}...")
            # 记录完整的解析失败内容到文件
            import logging
            logger = logging.getLogger("modules")
            logger.error(f"固定帧解析失败: {e}")
            logger.error(f"完整响应内容:\n{response}")
            raise ValueError(f"固定帧解析失败: {e}")
    
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
        
        # 构建提示词
        prompt = self._build_writing_prompt(frame_data, writing_style, 
                                           previous_frames, next_frames, 
                                           existing_writings, scene_data,
                                           detail_data, outline_data)
        
        # 调用模型
        response = self.model_manager.call_model(prompt)
        
        # 清理和格式化文本
        expanded_text = self._clean_writing_response(response)
        
        # 保存扩写结果
        chapter_file = os.path.join(self.output_dir, f"chapter_{frame_data.get('frame_id', 'unknown')}.txt")
        self.file_manager.write_text(chapter_file, expanded_text)
        
        print(f"扩写已保存: {chapter_file}")
        return expanded_text
    
    def _build_writing_prompt(self, frame_data: Dict[str, Any], style: str,
                           previous_frames: List[Dict] = None,
                           next_frames: List[Dict] = None,
                           existing_writings: List[str] = None,
                           scene_data: Dict[str, Any] = None,
                           detail_data: Dict[str, Any] = None,
                           outline_data: Dict[str, Any] = None) -> str:
        """构建扩写提示词，包含上下文信息"""
        
        # 构建上下文信息
        context_info = self._build_writing_context_info(frame_data, previous_frames, 
                                                       next_frames, existing_writings,
                                                       scene_data, detail_data, outline_data)
        
        template = """请将以下"固定帧"扩写为一个完整的文学段落：

{context_info}

固定帧信息：
时间：{timestamp}
场景：{scene_id}
当前动作：{current_action}

在场角色：
{characters}

地点描述：
{location}

环境条件：
{environment}

物品状态：
{objects}

对话内容：
{dialogue}

内心想法：
{thoughts}

感官细节：
{sensory_details}

写作要求：
1. 使用{style}风格进行描写
2. 将固定帧中的所有元素自然地融入叙述
3. 保持连贯性和流畅性
4. 适当添加过渡和细节描述
5. 字数控制在300-800字
6. 使用生动的语言和恰当的修辞
7. 注意与前文和后文的衔接，保持故事连贯性

请直接输出扩写后的段落，不需要额外的说明或标记。"""
        
        # 格式化各字段
        characters_text = "\n".join([
            f"- {char.get('name', '未知角色')}: {char.get('position', '未知位置')}, 正在{char.get('action', '行动')}, 情绪{char.get('emotion', '中性')}"
            for char in frame_data.get("characters_present", [])
        ])
        
        location = frame_data.get("location", {})
        location_text = f"{location.get('name', '未知地点')}: {location.get('description', '')}"
        
        environment = frame_data.get("environment", {})
        environment_text = f"天气: {environment.get('weather', '未知')}, 时间: {environment.get('time_of_day', '未知')}, 氛围: {environment.get('atmosphere', '未知')}"
        
        objects_text = "\n".join([
            f"- {obj.get('name', '未知物品')}: {obj.get('description', '')}"
            for obj in frame_data.get("objects", [])
        ])
        
        dialogue_text = "\n".join([
            f"{dial.get('speaker', '未知')}: \"{dial.get('content', '')}\""
            for dial in frame_data.get("dialogue", [])
        ])
        
        thoughts_text = "\n".join(frame_data.get("inner_thoughts", []))
        
        sensory = frame_data.get("sensory_details", {})
        sensory_text = f"视觉: {sensory.get('visual', '')}, 听觉: {sensory.get('auditory', '')}, 嗅觉: {sensory.get('olfactory', '')}, 触觉: {sensory.get('tactile', '')}"
        
        return template.format(
            context_info=context_info,
            timestamp=frame_data.get("timestamp", "未知时间"),
            scene_id=frame_data.get("scene_id", "未知场景"),
            current_action=frame_data.get("current_action", ""),
            characters=characters_text,
            location=location_text,
            environment=environment_text,
            objects=objects_text,
            dialogue=dialogue_text,
            thoughts=thoughts_text,
            sensory_details=sensory_text,
            style=style
        )
    
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