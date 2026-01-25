"""工具调用示例"""

import json
import logging
from tool_enabled_model_manager import ToolEnabledModelManager

# 配置日志
logging.basicConfig(level=logging.INFO)


def test_character_creation():
    """测试人物创建工具"""
    print("=== 测试人物创建工具 ===")
    
    # 创建工具调用模型管理器
    manager = ToolEnabledModelManager()
    
    # 测试创建人物
    response = manager.call_model_with_tools(
        prompt="请创建一个名为'亚瑟'的主角人物，他是一个年轻的勇者，年龄18岁，性格勇敢善良",
        system_prompt="你是一个小说创作助手，可以使用工具来创建和读取人物。请根据用户需求创建合适的人物角色。"
    )
    
    print("模型响应:")
    print(response)
    print("=" * 50)


def test_character_reading():
    """测试人物读取工具"""
    print("=== 测试人物读取工具 ===")
    
    # 创建工具调用模型管理器
    manager = ToolEnabledModelManager()
    
    # 测试读取人物
    response = manager.call_model_with_tools(
        prompt="请读取刚才创建的亚瑟的人物信息",
        system_prompt="你是一个小说创作助手，可以使用工具来创建和读取人物。"
    )
    
    print("模型响应:")
    print(response)
    print("=" * 50)


def test_story_writing_with_tools():
    """测试使用工具进行故事创作"""
    print("=== 测试使用工具进行故事创作 ===")
    
    # 创建工具调用模型管理器
    manager = ToolEnabledModelManager()
    
    # 测试复杂场景：创建人物并基于人物信息创作故事
    response = manager.call_model_with_tools(
        prompt="""
请帮我创作一个奇幻冒险故事。

首先，请创建一个主角人物：
- 姓名：艾莉娅
- 角色：女主角
- 基本信息：16岁的精灵少女，拥有绿色的长发和尖耳朵
- 性格：聪明、勇敢、善良
- 背景：来自森林深处的精灵部落

然后，请读取艾莉娅的人物信息，并基于她的特点创作一个简短的故事开头。
""",
        system_prompt="""你是一个专业的小说创作助手。你可以使用以下工具：

1. create_character - 创建新的人物角色
2. read_character - 读取已存在的人物信息

请根据用户的需求，合理地使用这些工具来辅助创作。"""
    )
    
    print("模型响应:")
    print(response)
    print("=" * 50)


def test_multiple_tools_interaction():
    """测试多个工具交互"""
    print("=== 测试多个工具交互 ===")
    
    # 创建工具调用模型管理器
    manager = ToolEnabledModelManager()
    
    # 测试多个工具调用
    response = manager.call_model_with_tools(
        prompt="""
我需要创建一个完整的冒险团队，包含以下成员：

1. 主角：雷恩，人类战士，25岁，性格坚毅
2. 法师：梅林，老年法师，性格睿智
3. 盗贼：莉莉，精灵盗贼，性格机灵

请先创建这些人物，然后告诉我这个团队的特点和可能的冒险故事。
""",
        system_prompt="""你是一个奇幻小说创作助手。请使用工具来创建人物，然后基于人物信息进行创作。"""
    )
    
    print("模型响应:")
    print(response)
    print("=" * 50)


def main():
    """主函数"""
    print("开始测试工具调用功能...\n")
    
    try:
        # 测试人物创建
        test_character_creation()
        
        # 测试人物读取
        test_character_reading()
        
        # 测试故事创作
        test_story_writing_with_tools()
        
        # 测试多个工具交互
        test_multiple_tools_interaction()
        
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()