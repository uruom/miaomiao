"""工具调用集成指南 - 演示如何在现有系统中集成工具调用功能"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime

from tool_enabled_model_manager import ToolEnabledModelManager
from tool_enabled_modules import CharacterModule, ToolEnabledOutlineModule, ToolEnabledWritingModule
from utils import FileManager


class ToolIntegrationGuide:
    """工具调用集成指南类"""
    
    def __init__(self):
        self.file_manager = FileManager()
        print("工具调用集成指南初始化完成")
    
    def demonstrate_basic_tool_calls(self):
        """演示基础工具调用"""
        print("\n=== 基础工具调用演示 ===")
        
        # 1. 创建工具调用模型管理器
        print("1. 创建工具调用模型管理器...")
        model_manager = ToolEnabledModelManager()
        
        # 2. 查看可用工具
        print("2. 查看可用工具...")
        available_tools = model_manager.tool_manager.list_tools()
        print(f"可用工具: {available_tools}")
        
        # 3. 演示创建人物工具
        print("\n3. 演示创建人物工具...")
        response = model_manager.call_model_with_tools(
            prompt="请创建一个名为'赵灵儿'的女主角，她是一个神秘的仙女",
            system_prompt="你是一个小说创作助手，可以使用工具来创建人物。"
        )
        print(f"创建人物结果: {response[:200]}...")
        
        # 4. 演示读取人物工具
        print("\n4. 演示读取人物工具...")
        response = model_manager.call_model_with_tools(
            prompt="请读取赵灵儿的人物信息",
            system_prompt="你是一个小说创作助手，可以使用工具来读取人物信息。"
        )
        print(f"读取人物结果: {response[:200]}...")
    
    def demonstrate_advanced_tool_integration(self):
        """演示高级工具集成"""
        print("\n=== 高级工具集成演示 ===")
        
        # 1. 创建项目目录
        project_path = "advanced_tool_project"
        os.makedirs(project_path, exist_ok=True)
        
        # 2. 创建工具调用模块
        print("1. 创建工具调用模块...")
        character_module = CharacterModule(project_path)
        outline_module = ToolEnabledOutlineModule(project_path)
        writing_module = ToolEnabledWritingModule(project_path)
        
        # 3. 批量创建人物
        print("\n2. 批量创建人物...")
        characters_to_create = [
            {"name": "孙悟空", "role": "主角", "description": "齐天大圣，神通广大"},
            {"name": "唐僧", "role": "主角", "description": "金蝉子转世，慈悲为怀"},
            {"name": "猪八戒", "role": "配角", "description": "天蓬元帅，贪吃好色"},
            {"name": "沙僧", "role": "配角", "description": "卷帘大将，忠诚老实"}
        ]
        
        created_characters = []
        for char_info in characters_to_create:
            character = character_module.create_character(
                name=char_info["name"],
                role=char_info["role"],
                background=char_info["description"]
            )
            created_characters.append(char_info["name"])
            print(f"创建人物: {char_info['name']}")
        
        # 4. 生成包含人物的大纲
        print("\n3. 生成包含人物的大纲...")
        outline = outline_module.generate_outline_with_characters(
            story_concept="西游记：取经团队历经九九八十一难的故事",
            character_names=created_characters
        )
        print(f"大纲标题: {outline.get('title', '未知')}")
        print(f"大纲部分: {len(outline.get('parts', []))}")
        
        # 5. 创作章节内容
        print("\n4. 创作章节内容...")
        if outline.get("parts") and outline["parts"][0].get("chapters"):
            chapter_id = outline["parts"][0]["chapters"][0]["id"]
            content = writing_module.write_chapter_with_characters(
                outline_data=outline,
                chapter_id=chapter_id,
                character_names=created_characters
            )
            print(f"章节创作完成，内容长度: {len(content)} 字符")
    
    def demonstrate_direct_tool_operations(self):
        """演示直接工具操作"""
        print("\n=== 直接工具操作演示 ===")
        
        # 1. 创建模型管理器
        model_manager = ToolEnabledModelManager()
        
        # 2. 直接创建人物（绕过模型调用）
        print("1. 直接创建人物...")
        result = model_manager.create_character_directly(
            name="白素贞",
            role="主角",
            basic_info={"age": 1000, "gender": "女", "appearance": "白衣飘飘，仙气十足"},
            personality={"traits": ["温柔", "善良", "执着"]},
            background="千年蛇精，为报恩来到人间"
        )
        
        if "error" not in result:
            print(f"直接创建成功: {result.get('character_name', '未知')}")
        
        # 3. 直接读取人物
        print("\n2. 直接读取人物...")
        result = model_manager.read_character_directly("白素贞")
        
        if "error" not in result:
            character_data = result.get("character_data", {})
            print(f"读取成功: {character_data.get('name', '未知')}")
            print(f"角色: {character_data.get('role', '未知')}")
            print(f"背景: {character_data.get('background', '未知')}")
        
        # 4. 工具使用统计
        print("\n3. 工具使用统计...")
        stats = model_manager.get_tool_usage_statistics()
        print(f"总工具调用: {stats.get('total_tool_calls', 0)}")
        for tool_name in model_manager.tool_manager.list_tools():
            print(f"{tool_name}: {stats.get(tool_name, 0)} 次")
    
    def demonstrate_integration_with_existing_system(self):
        """演示与现有系统的集成"""
        print("\n=== 与现有系统集成演示 ===")
        
        # 1. 检查现有系统
        print("1. 检查现有系统组件...")
        
        # 导入现有模块
        try:
            from model_manager import ModelManager
            from modules import OutlineModule, WritingModule
            print("✓ 现有模块导入成功")
        except ImportError as e:
            print(f"✗ 现有模块导入失败: {e}")
            return
        
        # 2. 创建混合系统
        print("\n2. 创建混合系统...")
        
        # 使用工具调用模型管理器
        tool_model_manager = ToolEnabledModelManager()
        
        # 使用现有模块，但替换模型管理器
        print("✓ 工具调用模型管理器已创建")
        
        # 3. 演示混合使用
        print("\n3. 演示混合使用...")
        
        # 使用工具调用创建人物
        response = tool_model_manager.call_model_with_tools(
            prompt="请创建一个名为'许仙'的男主角，他是一个善良的医生",
            system_prompt="你是一个小说创作助手，可以使用工具来创建人物。"
        )
        print(f"工具调用创建人物: {response[:100]}...")
        
        # 4. 集成建议
        print("\n4. 集成建议:")
        print("- 在现有ModelManager中添加工具调用支持")
        print("- 为现有模块添加工具调用选项")
        print("- 保持向后兼容性")
        print("- 提供工具调用开关配置")
    
    def provide_integration_guidelines(self):
        """提供集成指南"""
        print("\n=== 工具调用集成指南 ===")
        
        guidelines = [
            {
                "step": 1,
                "title": "导入工具调用模块",
                "description": "在现有代码中导入ToolEnabledModelManager和相关模块",
                "code": "from tool_enabled_model_manager import ToolEnabledModelManager"
            },
            {
                "step": 2,
                "title": "替换模型管理器",
                "description": "将现有的ModelManager替换为ToolEnabledModelManager",
                "code": "model_manager = ToolEnabledModelManager()  # 替换原有的ModelManager"
            },
            {
                "step": 3,
                "title": "配置工具调用",
                "description": "根据需要配置工具调用参数",
                "code": "model_manager.set_config(temperature=0.7, max_tokens=8000)"
            },
            {
                "step": 4,
                "title": "使用工具调用功能",
                "description": "在提示词中引导模型使用工具",
                "code": "response = model_manager.call_model_with_tools(prompt, system_prompt)"
            },
            {
                "step": 5,
                "title": "处理工具调用结果",
                "description": "解析和处理工具调用的结果",
                "code": "# 工具调用结果会自动处理，无需额外代码"
            }
        ]
        
        for guideline in guidelines:
            print(f"\n步骤 {guideline['step']}: {guideline['title']}")
            print(f"描述: {guideline['description']}")
            print(f"代码示例: {guideline['code']}")
    
    def run_complete_guide(self):
        """运行完整指南"""
        print("开始运行工具调用集成完整指南...")
        print("=" * 60)
        
        # 1. 基础工具调用演示
        self.demonstrate_basic_tool_calls()
        
        # 2. 高级工具集成演示
        self.demonstrate_advanced_tool_integration()
        
        # 3. 直接工具操作演示
        self.demonstrate_direct_tool_operations()
        
        # 4. 与现有系统集成演示
        self.demonstrate_integration_with_existing_system()
        
        # 5. 提供集成指南
        self.provide_integration_guidelines()
        
        print("\n=== 指南完成 ===")
        print("现在您已经掌握了如何在现有系统中集成工具调用功能！")


def main():
    """主函数"""
    print("工具调用集成指南")
    print("=" * 50)
    
    # 创建指南实例
    guide = ToolIntegrationGuide()
    
    # 运行完整指南
    guide.run_complete_guide()
    
    print("\n程序执行完毕！")


if __name__ == "__main__":
    main()