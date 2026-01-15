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
    "title": "眉间雪·江湖未远",
    "concept": "以《剑网三》为背景的师徒故事，以徒弟（男主）视角展开，讲述他从懵懂少年拜入师门，经历成长、离别、追寻与领悟，最终在时光流转中理解师父当年的选择与守护，完成一场关于传承与放下的江湖旅程。",
    "parts": [
        {
            "part_title": "起·风雪叩山门",
            "chapters": [
                {
                    "id": "P1C1",
                    "title": "雪落纯阳",
                    "summary": "战乱中失去亲人的少年陆昭，于纯阳宫山门外被一身着道袍、眉目清冷的女子所救。女子自称‘清微’，问其可愿拜师。陆昭为求安身与力量，叩首拜师，却不知师父眼底深藏的孤寂与过往。",
                    "estimated_words": 8000,
                    "characters": [
                        "陆昭（少年）",
                        "清微"
                    ],
                    "locations": [
                        "纯阳宫山门",
                        "华山风雪道"
                    ]
                },
                {
                    "id": "P1C2",
                    "title": "问道",
                    "summary": "陆昭开始跟随清微学习纯阳武学与道经。清微教导严苛，少言寡笑，常于论剑台静坐望雪。陆昭虽觉师父疏离，却也在日常中感受到细微关怀（如深夜盖被、为其调理寒症）。他听闻门派前辈提及师父曾有一故人，陨于多年前的枫华谷之战。",
                    "estimated_words": 12000,
                    "characters": [
                        "陆昭",
                        "清微",
                        "纯阳掌教（配角）"
                    ],
                    "locations": [
                        "论剑台",
                        "太极广场",
                        "弟子房"
                    ]
                },
                {
                    "id": "P1C3",
                    "title": "初涉江湖",
                    "summary": "陆昭武功初成，随清微下山执行第一次门派任务——护送物资前往洛阳。途中遭遇狼牙军斥候，清微为护陆昭首次展现惊人剑艺，却因动用真气过度引发旧疾。陆昭方知师父身体有损，内心震动。",
                    "estimated_words": 15000,
                    "characters": [
                        "陆昭",
                        "清微",
                        "狼牙军斥候"
                    ],
                    "locations": [
                        "华山小道",
                        "洛阳郊外"
                    ]
                }
            ]
        },
        {
            "part_title": "承·同行渐殊途",
            "chapters": [
                {
                    "id": "P2C1",
                    "title": "名动四方",
                    "summary": "数年过去，陆昭成长为青年才俊，在名剑大会崭露头角，结交各路侠士（可引入重要配角如天策好友、七秀红颜）。清微却渐渐减少亲自指导，更多时间独自闭关或远游。陆昭渴望与师父分享喜悦，却常找不到人，心生困惑与淡淡埋怨。",
                    "estimated_words": 18000,
                    "characters": [
                        "陆昭（青年）",
                        "清微",
                        "天策将领-秦烽",
                        "七秀弟子-苏婉（配角）"
                    ],
                    "locations": [
                        "名剑大会会场",
                        "纯阳宫闭关洞"
                    ]
                },
                {
                    "id": "P2C2",
                    "title": "裂隙",
                    "summary": "陆昭欲调查师父旧事，私下前往枫华谷，意外卷入一场针对当年战役幸存者的阴谋，身受重伤。清微及时赶到救下他，却第一次对他动了怒，责其冒进。两人爆发争吵，陆昭质问师父为何总是推开自己，清微终只留下一句‘你的江湖不应困于我的过往’，飘然离去。",
                    "estimated_words": 20000,
                    "characters": [
                        "陆昭",
                        "清微",
                        "神秘黑衣人（反派线索）"
                    ],
                    "locations": [
                        "枫华谷",
                        "红叶湖"
                    ]
                },
                {
                    "id": "P2C3",
                    "title": "空山",
                    "summary": "清微留下书信，让陆昭出师，并嘱其前往万花谷寻医圣治疗体内暗伤。陆昭回到纯阳，只见空荡的院落与积满雪的棋盘。他从掌教处得知，清微为救他强行出关，旧疾加剧，已前往昆仑绝地寻找疗伤之法，归期不定。陆昭悔恨不已。",
                    "estimated_words": 15000,
                    "characters": [
                        "陆昭",
                        "纯阳掌教"
                    ],
                    "locations": [
                        "纯阳宫·清微居所",
                        "三清殿"
                    ]
                }
            ]
        },
        {
            "part_title": "转·天涯各风雪",
            "chapters": [
                {
                    "id": "P3C1",
                    "title": "独行客",
                    "summary": "陆昭踏上江湖，一边行侠仗义、磨练心性，一边暗中追寻师父踪迹与当年往事线索。他逐渐理解师父当年承受的痛苦与孤独，武功心境皆大有长进，开始有人称其‘小剑君’。他也在旅途中帮助他人，体会师父所说的‘守护’之义。",
                    "estimated_words": 22000,
                    "characters": [
                        "陆昭",
                        "秦烽",
                        "苏婉",
                        "江湖各色人物"
                    ],
                    "locations": [
                        "扬州",
                        "巴陵县"
                    ]
                },
                {
                    "id": "P3C2",
                    "title": "往事书",
                    "summary": "陆昭在浩气盟故纸堆中查到线索，拼凑出真相：清微的故人（亦是其师兄）为救被困同门，孤身引开狼牙大军而战死。清微因此自责一生，立誓守护宗门与徒弟，却不愿亲近之人再因自己涉险。陆昭亦发现，当年枫华谷阴谋的幕后黑手，可能与师父旧敌有关。",
                    "estimated_words": 25000,
                    "characters": [
                        "陆昭",
                        [
                            "浩气盟文书（配角）"
                        ],
                        [
                            "神秘人（当年战役幸存者）"
                        ]
                    ],
                    "locations": [
                        "浩气盟·落雁城",
                        [
                            "瞿塘峡"
                        ]
                    ]
                },
                {
                    "id": "P3C3",
                    "title": "昆仑雪",
                    "summary": "根据线索，陆昭远赴昆仑。在冰天雪地中遭遇当年暗算师父旧敌的势力阻截，苦战后重伤濒危。危急时刻，一熟悉剑光破雪而来，清微现身。师徒并肩作战退敌。清微伤势未愈更显憔悴，但眼中坚冰已融。两人于冰洞中暂避风雪，清微终于缓缓讲述全部过往。",
                    "estimated_words": 28000,
                    "characters": [
                        "陆昭",
                        [
                            "清微"
                        ],
                        [
                            "宿敌·乌蒙贵（关联反派）"
                        ]
                    ],
                    "locations": [
                        "昆仑·玉虚峰",
                        [
                            "冰封洞窟"
                        ]
                    ]
                }
            ]
        },
        {
            "part_title": "合·归处是此心",
            "chapters": [
                {
                    "id": "P4C1",
                    "title": "传承",
                    "summary": "清微将代表纯阳一脉的剑印与心法全篇正式传予陆昭，承认他已青出于蓝。两人关系从师徒渐变为亦师亦友的知己。清微告知陆昭，自己将留在昆仑秘境疗伤修行，或许不再下山。她希望陆昭去走自己的路，守护这片他们共同牵挂的江湖。",
                    "estimated_words": 20000,
                    "characters": [
                        "陆昭",
                        [
                            "清微"
                        ]
                    ],
                    "locations": [
                        "昆仑秘境",
                        [
                            "论剑台（回忆穿插）"
                        ]
                    ]
                },
                {
                    "id": "P4C2",
                    "title": "新雪",
                    "summary": "多年后，已成为一代侠士、受人敬仰的陆昭，于又一个雪天回到纯阳宫。他在论剑台看到一名怯生生的孤儿（或新入门的少年弟子），如同当年的自己。他走上前，询问少年是否愿拜师。结尾，他独立雪中，望向远方昆仑，仿佛看到师父当年身影与自己重叠。眉间雪落，江湖未远，传承不息。",
                    "estimated_words": 15000,
                    "characters": [
                        "陆昭（中年）",
                        [
                            "纯阳新弟子（少年）"
                        ],
                        [
                            "秦烽、苏婉等（侧面提及）"
                        ]
                    ],
                    "locations": [
                        "纯阳宫·论剑台",
                        [
                            "华山山道"
                        ]
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
- 任何字符串内容中可以包含中文符号，若为json特殊字符请转移，json结构必须是英文标点
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
            characters=", ".join(chapter.get("characters", [])),
            locations=", ".join(chapter.get("locations", [])),
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
            characters=", ".join(scene.get("characters_involved", [])),
            location=scene.get("location", "未知地点"),
            events=", ".join(scene.get("key_events", [])),
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