"""提示词配置管理"""

import json
import os
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """提示词模板"""
    name: str
    template: str
    description: str = ""
    version: str = "1.0"
    variables: List[str] = None
    system_prompt: str = ""
    
    def __post_init__(self):
        if self.variables is None:
            # 自动提取变量
            self.variables = self._extract_variables()
    
    def _extract_variables(self) -> List[str]:
        """从模板中提取变量名"""
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, self.template)
        return list(set(variables))  # 去重
    
    def format(self, **kwargs) -> str:
        """格式化模板"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"模板变量缺失: {e}")
            # 尝试用空字符串替换缺失变量
            formatted = self.template
            for var in self.variables:
                if var not in kwargs:
                    formatted = formatted.replace(f"{{{var}}}", "")
            return formatted
        except Exception as e:
            logger.error(f"模板格式化失败: {e}")
            return self.template


class PromptManager:
    """提示词管理器"""
    
    def __init__(self, config_dir: str = "prompt_configs"):
        self.config_dir = config_dir
        self.templates: Dict[str, PromptTemplate] = {}
        
        # 加载默认模板
        self._load_default_templates()
        
        # 加载用户配置
        self._load_user_configs()
    
    def _load_default_templates(self):
        """加载默认模板"""
        default_templates = {
            "outline_generation": PromptTemplate(
                name="outline_generation",
                description="故事大纲生成",
                template="""请为以下故事概念生成一个详细的故事大纲：

故事概念：{concept}

要求：
1. 将故事分为{parts_count}个主要部分（起承转合）
2. 每个部分包含{chapters_per_part}个章节
3. 为每个章节提供标题和简要描述
4. 估计每个章节的字数
5. 列出每个章节涉及的主要角色和场景
6. 风格要求：{style}

请以JSON格式返回，结构如下：
{{
  "title": "故事标题",
  "concept": "故事概念",
  "genre": "{genre}",
  "parts": [
    {{
      "part_title": "部分标题",
      "chapters": [
        {{
          "id": "章节ID（如ch_1）",
          "title": "章节标题",
          "summary": "章节概要（100-200字）",
          "estimated_words": 字数,
          "characters": ["角色1", "角色2"],
          "locations": ["场景1", "场景2"],
          "key_themes": ["主题1", "主题2"]
        }}
      ]
    }}
  ]
}}

附加要求：{additional_requirements}""",
                system_prompt="你是一个专业的小说家，擅长创作各种类型的小说。请根据用户提供的故事概念，创作一个结构完整、情节丰富的大纲。确保大纲逻辑清晰，章节划分合理，并充分考虑角色的发展和情节的推进。"
            ),
            
            "detail_generation": PromptTemplate(
                name="detail_generation",
                description="详细细纲生成",
                template="""请为以下章节生成详细的细纲：

章节信息：
标题：{title}
概要：{summary}
涉及角色：{characters}
场景：{locations}
预估字数：{words}
故事风格：{style}

请生成包含以下内容的详细细纲：
1. {scenes_count}个具体场景
2. 每个场景的主要事件
3. 场景之间的过渡
4. 关键转折点
5. 情感发展弧线
6. 节奏控制

以JSON格式返回，结构如下：
{{
  "section_id": "{section_id}",
  "title": "章节标题",
  "scenes": [
    {{
      "scene_id": "场景ID（如scene_1）",
      "scene_title": "场景标题",
      "description": "场景描述（150-300字）",
      "characters_involved": ["角色"],
      "location": "地点",
      "key_events": ["事件1", "事件2"],
      "emotional_tone": "情感基调",
      "duration": "持续时间（如：30分钟）",
      "sensory_details": ["视觉细节", "听觉细节"]
    }}
  ],
  "transitions": ["过渡描述1", "过渡描述2"],
  "key_events": ["关键事件1", "关键事件2"],
  "emotional_arc": "情感发展描述",
  "pace": "节奏描述（快/慢/中等）",
  "conflicts": ["冲突1", "冲突2"]
}}""",
                system_prompt="你是一个经验丰富的小说编辑，擅长将大纲细化为具体的场景和情节。请根据章节信息，创作详细的细纲，确保每个场景都有明确的目标、冲突和解决，场景之间的过渡自然流畅。"
            ),
            
            "frame_generation": PromptTemplate(
                name="frame_generation",
                description="固定帧生成",
                template="""请为以下场景生成{frames_count}个"固定帧"，每个固定帧代表故事中的一个瞬间快照：

场景信息：
标题：{scene_title}
描述：{scene_description}
涉及角色：{characters}
地点：{location}
关键事件：{events}
情感基调：{tone}
故事风格：{style}

固定帧要求：
1. 每个固定帧包含该瞬间的完整状态
2. 包括在场角色及其状态（位置、动作、情绪）
3. 环境描述（光线、声音、气味等）
4. 物品状态
5. 当前进行的对话或动作
6. 角色的内心想法
7. 感官细节（视觉、听觉、嗅觉、触觉）

以JSON数组格式返回，每个固定帧结构如下：
[
  {{
    "frame_id": "帧ID（如frame_1）",
    "scene_id": "{scene_id}",
    "timestamp": "时间描述（如：开场后5分钟）",
    "characters_present": [
      {{
        "character_id": "角色ID",
        "name": "角色名",
        "position": "位置描述",
        "action": "当前动作",
        "emotion": "情绪状态",
        "dialogue_line": "当前对话（如有）",
        "physical_state": "身体状态（如：呼吸急促）"
      }}
    ],
    "location": {{
      "name": "地点名",
      "description": "地点描述",
      "lighting": "光线",
      "sounds": ["声音1", "声音2"],
      "smells": ["气味1", "气味2"],
      "temperature": "温度",
      "weather_effects": "天气影响"
    }},
    "environment": {{
      "weather": "天气",
      "time_of_day": "时间",
      "atmosphere": "氛围",
      "season": "季节"
    }},
    "objects": [
      {{
        "object_id": "物品ID",
        "name": "物品名",
        "description": "物品描述",
        "position": "位置",
        "state": "状态",
        "significance": "重要性"
      }}
    ],
    "current_action": "当前主要动作描述",
    "dialogue": [
      {{
        "speaker": "说话者",
        "content": "对话内容",
        "tone": "语气",
        "subtext": "潜台词"
      }}
    ],
    "inner_thoughts": ["角色1的内心想法", "角色2的内心想法"],
    "sensory_details": {{
      "visual": "视觉细节",
      "auditory": "听觉细节",
      "olfactory": "嗅觉细节",
      "tactile": "触觉细节",
      "gustatory": "味觉细节（如有）"
    }},
    "tension_level": "紧张程度（1-10）"
  }}
]

请确保每个固定帧都是独立的、完整的瞬间描述，能够为后续的扩写提供充分的细节。"""
            ),
            
            "writing_expansion": PromptTemplate(
                name="writing_expansion",
                description="固定帧扩写",
                template="""请将以下"固定帧"扩写为一个完整的文学段落：

固定帧信息：
时间：{timestamp}
场景：{scene_id}
当前动作：{current_action}
紧张程度：{tension_level}

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
5. 字数控制在{word_count}字左右
6. 使用生动的语言和恰当的修辞
7. 注意节奏和韵律
8. 体现{emotional_tone}的情感基调

请直接输出扩写后的段落，不需要额外的说明或标记。"""
            ),
            
            "character_creation": PromptTemplate(
                name="character_creation",
                description="角色创建",
                template="""请创建一个详细的角色：

角色基本信息：
姓名：{name}
年龄：{age}
性别：{gender}
职业：{occupation}

角色要求：
1. 外貌特征
2. 性格特点
3. 背景故事
4. 动机和目标
5. 弱点和缺陷
6. 人际关系
7. 技能和能力

请以JSON格式返回，结构如下：
{{
  "character_id": "角色ID",
  "name": "姓名",
  "age": 年龄,
  "gender": "性别",
  "occupation": "职业",
  "appearance": {{
    "height": "身高",
    "build": "体型",
    "hair": "头发",
    "eyes": "眼睛",
    "distinctive_features": ["特征1", "特征2"]
  }},
  "personality": {{
    "traits": ["特质1", "特质2"],
    "values": ["价值观1", "价值观2"],
    "fears": ["恐惧1", "恐惧2"],
    "desires": ["欲望1", "欲望2"]
  }},
  "background": {{
    "origin": "出身",
    "family": "家庭",
    "education": "教育",
    "key_events": ["关键事件1", "关键事件2"]
  }},
  "skills": ["技能1", "技能2"],
  "weaknesses": ["弱点1", "弱点2"],
  "relationships": [
    {{
      "character": "相关角色",
      "relationship": "关系",
      "description": "关系描述"
    }}
  ],
  "current_status": {{
    "health": "健康状况",
    "mood": "当前情绪",
    "goal": "当前目标"
  }}
}}"""
            )
        }
        
        self.templates.update(default_templates)
        logger.info(f"已加载 {len(default_templates)} 个默认模板")
    
    def _load_user_configs(self):
        """加载用户配置的模板"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
            return
        
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.config_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict):
                        template = PromptTemplate(**data)
                        self.templates[template.name] = template
                    elif isinstance(data, list):
                        for item in data:
                            template = PromptTemplate(**item)
                            self.templates[template.name] = template
                    
                    logger.info(f"已加载用户模板: {filename}")
                except Exception as e:
                    logger.error(f"加载模板文件失败 {filename}: {e}")
    
    def get_prompt(self, template_name: str, data: Dict[str, Any]) -> Optional[str]:
        """获取格式化后的提示词"""
        if template_name not in self.templates:
            logger.error(f"未找到模板: {template_name}")
            return None
        
        template = self.templates[template_name]
        return template.format(**data)
    
    def get_system_prompt(self, template_name: str) -> str:
        """获取系统提示词"""
        if template_name not in self.templates:
            logger.warning(f"未找到模板: {template_name}")
            return ""
        
        return self.templates[template_name].system_prompt
    
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """获取模板对象"""
        return self.templates.get(template_name)
    
    def add_template(self, template: PromptTemplate):
        """添加新模板"""
        self.templates[template.name] = template
        
        # 保存到文件
        self._save_template(template)
    
    def update_template(self, template_name: str, **kwargs):
        """更新模板"""
        if template_name not in self.templates:
            logger.error(f"未找到模板: {template_name}")
            return
        
        template = self.templates[template_name]
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        # 保存到文件
        self._save_template(template)
    
    def _save_template(self, template: PromptTemplate):
        """保存模板到文件"""
        try:
            filepath = os.path.join(self.config_dir, f"{template.name}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(template), f, indent=2, ensure_ascii=False)
            logger.info(f"模板已保存: {filepath}")
        except Exception as e:
            logger.error(f"保存模板失败: {e}")
    
    def list_templates(self) -> List[str]:
        """列出所有模板名称"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """获取模板信息"""
        if template_name not in self.templates:
            return {}
        
        template = self.templates[template_name]
        return {
            "name": template.name,
            "description": template.description,
            "version": template.version,
            "variables": template.variables,
            "system_prompt": template.system_prompt[:100] + "..." if len(template.system_prompt) > 100 else template.system_prompt
        }


def test_prompt_manager():
    """测试提示词管理器"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    manager = PromptManager()
    
    # 测试模板列表
    print("可用模板:")
    for name in manager.list_templates():
        info = manager.get_template_info(name)
        print(f"  - {name}: {info['description']}")
    
    # 测试获取提示词
    print("\n测试大纲生成提示词:")
    data = {
        "concept": "一个关于AI觉醒的故事",
        "parts_count": 3,
        "chapters_per_part": 3,
        "style": "科幻",
        "genre": "科幻",
        "additional_requirements": "需要有哲学思考"
    }
    
    prompt = manager.get_prompt("outline_generation", data)
    if prompt:
        print(f"提示词长度: {len(prompt)}")
        print(f"提示词预览:\n{prompt[:200]}...")
    
    # 测试系统提示词
    print(f"\n系统提示词: {manager.get_system_prompt('outline_generation')[:100]}...")
    
    print("\n提示词管理器测试完成")


if __name__ == "__main__":
    test_prompt_manager()