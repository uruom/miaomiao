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
        # response = self.model_manager.call_model(prompt)
        response = '''
        {
    "title": "如寄风雪",
    "concept": "以纯阳宫弟子顾清寒（男主A）为视角，讲述他与师父谢云流的师徒传承、以及他后来所收天策弟子李承锋（B）的故事。李承锋将经历类似白骨哀、参商等事件，而顾清寒在引导徒弟的过程中，逐渐理解并追忆起自己与师父的过往。整体基调苍凉温暖，如风雪中的一盏灯。",
    "parts": [
        {
            "part_title": "起：风雪故人",
            "chapters": [
                {
                    "id": "C1",
                    "title": "纯阳雪",
                    "summary": "纯阳宫弟子顾清寒于山门扫雪，回忆起多年前师父谢云流在此教他练剑的场景。如今师父已云游多年，音讯全无。他接到掌门之命，需前往洛阳处理一桩与天策府相关的旧事。",
                    "estimated_words": 15000,
                    "characters": [
                        "顾清寒",
                        "谢云流（回忆）",
                        "纯阳掌门"
                    ],
                    "locations": [
                        "纯阳宫山门",
                        "太极广场",
                        "论剑峰"
                    ]
                },
                {
                    "id": "C2",
                    "title": "洛阳旧识",
                    "summary": "顾清寒抵达洛阳，调查中发现此事涉及多年前战死的天策将士遗物。在一处旧宅，他遇到了一个倔强而狼狈的少年——李承锋，一个因战争失去家人、一心想要加入天策府却屡屡被拒的孤儿。",
                    "estimated_words": 18000,
                    "characters": [
                        "顾清寒",
                        "李承锋",
                        "天策府校尉"
                    ],
                    "locations": [
                        "洛阳城",
                        "旧宅废墟",
                        "茶馆"
                    ]
                },
                {
                    "id": "C3",
                    "title": "一念收徒",
                    "summary": "李承锋为抢夺父亲遗留的军牌（涉及白骨哀线索）与江湖人冲突，重伤濒死。顾清寒出手相救，看着少年眼中与自己当年相似的执拗与孤寂，鬼使神差地决定暂时带他回纯阳，并教授其武艺基础。",
                    "estimated_words": 16000,
                    "characters": [
                        "顾清寒",
                        "李承锋",
                        "江湖恶徒"
                    ],
                    "locations": [
                        "洛阳郊外破庙",
                        "回纯阳的路上"
                    ]
                }
            ]
        },
        {
            "part_title": "承：枪影剑光",
            "chapters": [
                {
                    "id": "C4",
                    "title": "华山授业",
                    "summary": "顾清寒以纯阳心法为基础，为李承锋打下内功根基，同时根据其体质传授一些天策府的基础枪术（顾清寒早年从谢云流处涉猎颇广）。两人在华山之巅朝夕相处，初现师徒温情，但李承锋始终心系天策。",
                    "estimated_words": 20000,
                    "characters": [
                        "顾清寒",
                        "李承锋"
                    ],
                    "locations": [
                        "纯阳宫后山",
                        "思过崖",
                        "顾清寒的院落"
                    ]
                },
                {
                    "id": "C5",
                    "title": "白骨哀",
                    "summary": "李承锋终于得知父亲当年战死的真相及遗物“白骨哀“笛的下落（与天策著名剧情关联）。他执意前往枫华谷寻找。顾清寒不放心，陪同前往。两人在红叶湖畔找到线索，却也卷入江湖纷争，李承锋首次体会到战争的残酷与遗属的悲痛。",
                    "estimated_words": 22000,
                    "characters": [
                        "顾清寒",
                        "李承锋",
                        "神秘红衣女子（白骨哀相关人物）",
                        "江湖势力"
                    ],
                    "locations": [
                        "枫华谷",
                        "红叶湖",
                        "战乱遗址"
                    ]
                },
                {
                    "id": "C6",
                    "title": "参商离",
                    "summary": "经历枫华谷事件后，李承锋武艺与心性成长，正式通过天策府考核。离别之日，顾清寒赠其一把亲手锻造的长枪。两人于华山脚下分别，一个回纯阳，一个赴军营。顾清寒望着徒弟远去的背影，恍惚间看到了当年谢云流送别自己的情景。",
                    "estimated_words": 18000,
                    "characters": [
                        "顾清寒",
                        "李承锋"
                    ],
                    "locations": [
                        "华山脚下",
                        "官道岔路口"
                    ]
                }
            ]
        },
        {
            "part_title": "转：烽火连城",
            "chapters": [
                {
                    "id": "C7",
                    "title": "雁门烽烟",
                    "summary": "数年过去，顾清寒听闻天策府在雁门关与外敌激战，心中牵挂，遂下山寻徒。在战火纷飞的边关，他找到了已成为天校尉、却因战友接连牺牲而变得沉默坚毅的李承锋。师徒并肩作战，关系亦师亦友。",
                    "estimated_words": 21000,
                    "characters": [
                        "顾清寒",
                        "李承锋",
                        "天策将士",
                        "狼牙军"
                    ],
                    "locations": [
                        "雁门关",
                        "天策军营",
                        "战场前线"
                    ]
                },
                {
                    "id": "C8",
                    "title": "故剑尘封",
                    "summary": "在雁门关休整期间，顾清寒为救李承锋，旧伤复发。养伤时，李承锋问起师祖谢云流之事。顾清寒第一次详细讲述自己与师父的过往：谢云流如何收养他、传授绝世剑法，又为何最终选择离开，只留下一把旧剑和“守护本心“的嘱托。讲述中，顾清寒开始重新审视“师徒“与“传承“的意义。",
                    "estimated_words": 23000,
                    "characters": [
                        "顾清寒",
                        "李承锋"
                    ],
                    "locations": [
                        "雁门关伤兵营",
                        "关隘城墙"
                    ]
                },
                {
                    "id": "C9",
                    "title": "暗涌",
                    "summary": "战事暂缓，但江湖暗流涌动。当年“白骨哀“事件背后的势力再次出现，目标直指李承锋及其手中的父亲遗物。同时，有零星星的消息指向谢云流可能在南方出现。顾清寒面临选择：是继续守护徒弟追查阴谋，还是南下寻找师父的踪迹？",
                    "estimated_words": 19000,
                    "characters": [
                        "顾清寒",
                        "李承锋",
                        "神秘组织杀手",
                        "天策同袍"
                    ],
                    "locations": [
                        "雁门关市集",
                        "隐秘据点",
                        "军营"
                    ]
                }
            ]
        },
        {
            "part_title": "合：薪火如寄",
            "chapters": [
                {
                    "id": "C10",
                    "title": "双线寻踪",
                    "summary": "顾清寒决定与李承锋分头行动：李承锋借助天策力量调查神秘组织，而顾清寒则南下苗疆追寻谢云流可能的踪迹。两条线索逐渐交汇，揭示出更大的阴谋——神秘组织意图利用当年战死将士的遗物（包括白骨哀）施行某种禁忌之术。",
                    "estimated_words": 22000,
                    "characters": [
                        "顾清寒",
                        "李承锋",
                        "苗疆向导",
                        "天策情报人员"
                    ],
                    "locations": [
                        "南下路途",
                        "苗疆村落",
                        "天策府密室"
                    ]
                },
                {
                    "id": "C11",
                    "title": "再见如寄",
                    "summary": "顾清寒在苗疆一处与世隔绝的山谷中，终于找到了隐居多年、已是白发苍苍的谢云流。师徒重逢，没有激动的话语，只有一壶酒，一场静默的雪。谢云流点明顾清寒已找到了自己的“道“——即守护与传承，不必再执着于寻找师父。",
                    "estimated_words": 20000,
                    "characters": [
                        "顾清寒",
                        "谢云流"
                    ],
                    "locations": [
                        "苗疆幽谷",
                        "竹庐",
                        "雪中亭"
                    ]
                },
                {
                    "id": "C12",
                    "title": "薪火相传",
                    "summary": "顾清寒赶回中原，与李承锋会合，共同挫败神秘组织的阴谋。最终决战中，李承锋以天策之枪贯彻了守护之志，顾清寒则以纯阳之剑印证了传承之道。事件平息后，李承锋选择留在天策戍边，而顾清寒回到纯阳，偶尔下山游历。又是一个雪天，已成独当一面将领的李承锋，在军营外捡到了一个战乱孤儿……故事在轮回与希望中结束。",
                    "estimated_words": 25000,
                    "characters": [
                        "顾清寒",
                        "李承锋",
                        "神秘组织头目",
                        "孤儿"
                    ],
                    "locations": [
                        "龙门荒漠遗迹",
                        "纯阳宫",
                        "天策府边关营地"
                    ]
                }
            ]
        }
    ]
}
        '''
        # 提取JSON
        outline_data = self._parse_outline_response(response)
        
        if not outline_data:
            print("大纲生成失败，使用默认结构")
            outline_data = self._create_default_outline(story_concept)
        
        # 保存大纲
        outline_file = os.path.join(self.output_dir, f"outline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.file_manager.write_json(outline_file, outline_data)
        
        print(f"大纲已保存: {outline_file}")
        return outline_data
    
    def _build_outline_prompt(self, concept: str, kwargs: Dict) -> str:
        """构建大纲生成提示词"""
        template = """请为以下故事概念生成一个详细的故事大纲：

故事概念：{concept}

要求：
1. 将故事分为3-5个主要部分（起承转合）
2. 每个部分包含2-4个章节
3. 为每个章节提供标题和简要描述
4. 估计每个章节的字数
5. 列出每个章节涉及的主要角色和场景
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
    
    def _parse_outline_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析模型响应"""
        try:
            # 尝试提取JSON
            data = self.model_manager.extract_json(response)
            if data:
                return data
            
            # 如果没有JSON，尝试重构
            lines = response.split('\n')
            outline = {
                "title": lines[0] if lines else "未命名故事",
                "concept": "",
                "parts": []
            }
            
            current_part = None
            for line in lines:
                if line.strip().startswith('#'):
                    if current_part:
                        outline["parts"].append(current_part)
                    current_part = {"part_title": line.strip('# '), "chapters": []}
            
            return outline
        except Exception as e:
            print(f"解析大纲失败: {e}")
            return None
    
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
    
    def generate_details(self, outline_data: Dict[str, Any], chapter_id: str) -> Dict[str, Any]:
        """为指定章节生成详细细纲"""
        print(f"为章节 {chapter_id} 生成详细细纲...")
        
        # 查找章节
        chapter = self._find_chapter(outline_data, chapter_id)
        if not chapter:
            print(f"未找到章节: {chapter_id}")
            return {}
        
        # 构建提示词
        prompt = self._build_detail_prompt(chapter)
        
        # 调用模型
        response = self.model_manager.call_model(prompt)
        
        # 解析响应
        detail_data = self._parse_detail_response(response, chapter)
        
        # 保存细纲
        detail_file = os.path.join(self.output_dir, f"detail_{chapter_id}_{datetime.now().strftime('%H%M%S')}.json")
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
    
    def _build_detail_prompt(self, chapter: Dict[str, Any]) -> str:
        """构建细纲生成提示词"""
        template = """请为以下章节生成详细的细纲：

章节信息：
标题：{title}
概要：{summary}
涉及角色：{characters}
场景：{locations}
预估字数：{words}

请生成包含以下内容的详细细纲：
1. 3-8个具体场景
2. 每个场景的主要事件
3. 场景之间的过渡
4. 关键转折点
5. 情感发展弧线
6. 节奏控制

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
            title=chapter.get("title", "未命名章节"),
            summary=chapter.get("summary", ""),
            # characters=", ".join(chapter.get("characters", [])),
            characters=", ".join(str(c) for c in chapter.get("characters", [])),
            locations=", ".join(str(c) for c in chapter.get("locations", [])),
            words=chapter.get("estimated_words", 0)
        )
    
    def _parse_detail_response(self, response: str, chapter: Dict[str, Any]) -> Dict[str, Any]:
        """解析细纲响应"""
        data = self.model_manager.extract_json(response)
        if not data:
            # 创建默认细纲
            data = {
                "section_id": chapter.get("id", "unknown"),
                "title": chapter.get("title", "未命名章节"),
                "scenes": [
                    {
                        "scene_id": "scene_1",
                        "scene_title": "开场场景",
                        "description": chapter.get("summary", ""),
                        "characters_involved": chapter.get("characters", []),
                        "location": chapter.get("locations", [""])[0] if chapter.get("locations") else "未知地点",
                        "key_events": ["故事开始"],
                        "emotional_tone": "中性"
                    }
                ],
                "transitions": ["时间推移"],
                "key_events": ["主要事件"],
                "emotional_arc": "平稳发展",
                "pace": "中等"
            }
        
        data["section_id"] = chapter.get("id", data.get("section_id", "unknown"))
        return data


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
    
    def generate_frames(self, detail_data: Dict[str, Any], scene_id: str) -> List[Dict[str, Any]]:
        """为指定场景生成固定帧"""
        print(f"为场景 {scene_id} 生成固定帧...")
        
        # 查找场景
        scene = self._find_scene(detail_data, scene_id)
        if not scene:
            print(f"未找到场景: {scene_id}")
            return []
        
        # 生成固定帧
        frames = self._create_frames_for_scene(scene, detail_data)
        
        # 保存固定帧
        for frame in frames:
            frame_file = os.path.join(self.output_dir, f"frame_{frame['frame_id']}.json")
            self.file_manager.write_json(frame_file, frame)
            
            # 提取并保存角色、地点等信息
            self._extract_and_save_entities(frame)
        
        print(f"已生成 {len(frames)} 个固定帧")
        return frames
    
    def _find_scene(self, detail_data: Dict[str, Any], scene_id: str) -> Optional[Dict[str, Any]]:
        """查找指定场景"""
        for scene in detail_data.get("scenes", []):
            if scene.get("scene_id") == scene_id:
                return scene
        return None
    
    def _create_frames_for_scene(self, scene: Dict[str, Any], detail_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """为场景创建固定帧"""
        # 构建提示词
        prompt = self._build_frame_prompt(scene, detail_data)
        
        # 调用模型
        response = self.model_manager.call_model(prompt)
        
        # 解析响应
        frames_data = self._parse_frames_response(response, scene)
        
        return frames_data
    
    def _build_frame_prompt(self, scene: Dict[str, Any], detail_data: Dict[str, Any]) -> str:
        """构建固定帧生成提示词"""
        template = """请为以下场景生成2-5个"固定帧"，每个固定帧代表故事中的一个瞬间快照：

场景信息：
标题：{scene_title}
描述：{scene_description}
涉及角色：{characters}
地点：{location}
关键事件：{events}
情感基调：{tone}

固定帧要求：
1. 每个固定帧包含该瞬间的完整状态
2. 包括在场角色及其状态（位置、动作、情绪）
3. 环境描述（光线、声音、气味等）
4. 物品状态
5. 当前进行的对话或动作
6. 角色的内心想法

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
            scene_title=scene.get("scene_title", "未命名场景"),
            scene_description=scene.get("description", ""),
            characters=", ".join(str(c) for c in scene.get("characters_involved", [])),
            # characters=", ".join(scene.get("characters_involved", [])),
            location=scene.get("location", "未知地点"),
            events=", ".join(str(sc) for sc in scene.get("key_events", [])),
            tone=scene.get("emotional_tone", "中性")
        )
    
    def _parse_frames_response(self, response: str, scene: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析固定帧响应"""
        data = self.model_manager.extract_json(response)
        if not data or not isinstance(data, list):
            # 创建默认固定帧
            return [self._create_default_frame(scene)]
        
        # 确保每个帧都有scene_id
        for frame in data:
            frame["scene_id"] = scene.get("scene_id", "unknown")
            if "frame_id" not in frame:
                frame["frame_id"] = f"frame_{len(data)}"
        
        return data
    
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
    
    def expand_frame(self, frame_data: Dict[str, Any], writing_style: str = "文学") -> str:
        """将固定帧扩写为文章段落"""
        print(f"扩写固定帧 {frame_data.get('frame_id', 'unknown')}...")
        
        # 构建提示词
        prompt = self._build_writing_prompt(frame_data, writing_style)
        
        # 调用模型
        response = self.model_manager.call_model(prompt)
        
        # 清理和格式化文本
        expanded_text = self._clean_writing_response(response)
        
        # 保存扩写结果
        chapter_file = os.path.join(self.output_dir, f"chapter_{frame_data.get('frame_id', 'unknown')}.txt")
        self.file_manager.write_text(chapter_file, expanded_text)
        
        print(f"扩写已保存: {chapter_file}")
        return expanded_text
    
    def _build_writing_prompt(self, frame_data: Dict[str, Any], style: str) -> str:
        """构建扩写提示词"""
        template = """请将以下"固定帧"扩写为一个完整的文学段落：

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