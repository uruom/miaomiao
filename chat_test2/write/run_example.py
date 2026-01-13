"""运行示例 - 演示如何使用小说写作系统"""

import os
import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import AutoStoryWriter
from model_manager import APIModelManager, ModelConfig
from prompt_config import PromptManager


def example_without_api():
    """不使用API的示例（模拟模式）"""
    print("="*60)
    print("示例1: 不使用API的模拟模式")
    print("="*60)
    
    # 创建写作系统
    writer = AutoStoryWriter("example_story")
    
    # 设置项目配置
    config = {
        "title": "AI觉醒记",
        "genre": "科幻",
        "style": "文学",
        "word_count": 5000
    }
    writer.setup_project(config)
    
    # 运行完整流水线
    story_concept = "一个关于AI在实验室中意外觉醒自我意识，开始探索世界并最终选择帮助人类的故事。"
    result = writer.run_full_pipeline(story_concept, style="科幻")
    
    # 显示状态
    status = writer.get_status()
    print(f"\n项目状态:")
    print(f"  大纲生成: {'✓' if status['stages']['outline'] else '✗'}")
    print(f"  细纲生成: {'✓' if status['stages']['details'] else '✗'}")
    print(f"  固定帧生成: {'✓' if status['stages']['frames'] else '✗'}")
    print(f"  故事扩写: {'✓' if status['stages']['chapters'] else '✗'}")
    
    return writer


def example_with_api():
    """使用API的示例"""
    print("\n" + "="*60)
    print("示例2: 使用API的模式")
    print("="*60)
    
    # 创建模型配置
    model_config = ModelConfig(
        api_key="YOUR_API_KEY_HERE",  # 替换为你的API Key
        model_name="deepseek-ai/DeepSeek-V3.2",
        temperature=0.7,
        max_tokens=8000
    )
    
    # 创建API模型管理器
    api_manager = APIModelManager(model_config)
    
    # 测试API调用
    print("测试API调用...")
    response = api_manager.call_model("你好，请简单介绍一下自己")
    print(f"API响应: {response[:100]}...")
    
    return api_manager


def example_prompt_templates():
    """示例：使用提示词模板"""
    print("\n" + "="*60)
    print("示例3: 使用提示词模板")
    print("="*60)
    
    # 创建提示词管理器
    prompt_manager = PromptManager()
    
    # 显示可用模板
    templates = prompt_manager.list_templates()
    print(f"可用模板 ({len(templates)} 个):")
    for template_name in templates:
        info = prompt_manager.get_template_info(template_name)
        print(f"  - {template_name}: {info['description']}")
    
    # 使用大纲模板
    print("\n使用大纲模板生成提示词:")
    data = {
        "concept": "一个关于魔法学校的少年成长故事",
        "parts_count": 4,
        "chapters_per_part": 3,
        "style": "奇幻",
        "genre": "奇幻",
        "additional_requirements": "需要有友谊、勇气和成长的元素"
    }
    
    prompt = prompt_manager.get_prompt("outline_generation", data)
    print(f"生成的提示词长度: {len(prompt)}")
    print(f"提示词预览:\n{prompt[:200]}...")
    
    # 获取系统提示词
    system_prompt = prompt_manager.get_system_prompt("outline_generation")
    print(f"\n系统提示词长度: {len(system_prompt)}")
    print(f"系统提示词预览: {system_prompt[:150]}...")


def example_custom_prompt():
    """示例：创建自定义提示词模板"""
    print("\n" + "="*60)
    print("示例4: 创建自定义提示词模板")
    print("="*60)
    
    from prompt_config import PromptTemplate
    
    # 创建自定义模板
    custom_template = PromptTemplate(
        name="custom_dialogue_generation",
        description="对话生成模板",
        template="""请为以下场景生成一段自然生动的对话：

场景描述：{scene_description}
角色1：{character1}（性格：{char1_personality}）
角色2：{character2}（性格：{char2_personality}）
对话主题：{dialogue_topic}
情感基调：{emotional_tone}

要求：
1. 对话要符合角色的性格特点
2. 对话要推动情节发展
3. 要有适当的潜台词
4. 对话长度：{dialogue_length}句左右

请以JSON格式返回：
{{
  "dialogue": [
    {{
      "speaker": "说话者",
      "content": "对话内容",
      "tone": "语气",
      "subtext": "潜台词"
    }}
  ],
  "summary": "对话摘要"
}}""",
        system_prompt="你是一个专业的剧本作家，擅长创作生动、自然的对话。请根据角色性格和场景要求，创作符合角色特点的对话。"
    )
    
    # 创建提示词管理器并添加模板
    prompt_manager = PromptManager()
    prompt_manager.add_template(custom_template)
    
    print(f"已添加自定义模板: {custom_template.name}")
    print(f"模板变量: {custom_template.variables}")
    
    # 使用自定义模板
    data = {
        "scene_description": "两个老朋友在咖啡馆重逢",
        "character1": "李明",
        "char1_personality": "外向、幽默、怀旧",
        "character2": "王芳", 
        "char2_personality": "内向、细腻、理性",
        "dialogue_topic": "回忆大学时光",
        "emotional_tone": "温馨、略带感伤",
        "dialogue_length": 8
    }
    
    prompt = prompt_manager.get_prompt(custom_template.name, data)
    print(f"\n自定义模板生成的提示词长度: {len(prompt)}")
    print(f"提示词预览:\n{prompt[:250]}...")


def example_step_by_step():
    """示例：逐步运行故事生成"""
    print("\n" + "="*60)
    print("示例5: 逐步运行故事生成")
    print("="*60)
    
    # 创建写作系统
    writer = AutoStoryWriter("step_by_step_story")
    
    # 设置项目配置
    config = {
        "title": "时间旅者的日记",
        "genre": "科幻",
        "style": "文学",
        "word_count": 3000
    }
    writer.setup_project(config)
    
    # 1. 只生成大纲
    print("\n1. 生成故事大纲...")
    story_concept = "一个时间旅行者发现自己被困在过去，必须找到回家的方法，同时避免改变历史。"
    outline = writer.generate_outline(story_concept)
    
    if outline:
        print(f"大纲标题: {outline.get('title')}")
        print(f"章节数量: {sum(len(part['chapters']) for part in outline.get('parts', []))}")
        
        # 2. 为第一个章节生成细纲
        print("\n2. 生成详细细纲...")
        if outline.get("parts"):
            chapter_id = outline["parts"][0]["chapters"][0]["id"]
            details = writer.generate_details(outline, [chapter_id])
            
            if details:
                print(f"细纲生成完成，场景数量: {len(details[chapter_id].get('scenes', []))}")
                
                # 3. 为第一个场景生成固定帧
                print("\n3. 生成固定帧...")
                if details[chapter_id].get("scenes"):
                    scene_id = details[chapter_id]["scenes"][0]["scene_id"]
                    frames = writer.generate_frames({chapter_id: details[chapter_id]}, [scene_id])
                    
                    if frames and chapter_id in frames:
                        print(f"固定帧生成完成，帧数量: {len(frames[chapter_id])}")
                        
                        # 4. 扩写第一个固定帧
                        print("\n4. 扩写为文章...")
                        if frames[chapter_id]:
                            result = writer.expand_to_story({chapter_id: [frames[chapter_id][0]]})
                            if result:
                                print(f"扩写完成，字数: {len(result['chapters'][chapter_id])}")
    
    # 显示最终状态
    status = writer.get_status()
    print(f"\n项目状态:")
    for stage, completed in status["stages"].items():
        print(f"  {stage}: {'✓' if completed else '✗'}")


def main():
    """主函数"""
    print("小说自动写作系统示例")
    print("="*60)
    
    # 示例1: 模拟模式
    writer1 = example_without_api()
    
    # 示例2: API模式（需要API Key）
    # api_manager = example_with_api()
    
    # 示例3: 提示词模板
    example_prompt_templates()
    
    # 示例4: 自定义提示词
    example_custom_prompt()
    
    # 示例5: 逐步运行
    example_step_by_step()
    
    print("\n" + "="*60)
    print("示例运行完成！")
    print("="*60)
    print("\n使用说明:")
    print("1. 修改 config_example.json 配置你的故事")
    print("2. 运行: python main.py --project my_story --concept '你的故事概念'")
    print("3. 或者使用: python run_example.py")
    print("4. 要使用真实API，请在 model_manager.py 中设置你的API Key")


if __name__ == "__main__":
    main()