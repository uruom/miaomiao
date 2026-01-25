"""工具调用集成示例 - 演示如何在现有系统中集成工具调用功能"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime

from tool_enabled_model_manager import ToolEnabledModelManager
from tool_enabled_modules import CharacterModule, ToolEnabledOutlineModule, ToolEnabledWritingModule
from utils import FileManager


class ToolIntegrationExample:
    """工具调用集成示例类"""
    
    def __init__(self, project_path: str = "tool_integration_project"):
        self.project_path = project_path
        self.file_manager = FileManager()
        
        # 创建项目目录结构
        os.makedirs(os.path.join(project_path, "data", "characters"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "output", "outlines"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "output", "chapters"), exist_ok=True)
        
        # 初始化模块
        self.character_module = CharacterModule(project_path)
        self.outline_module = ToolEnabledOutlineModule(project_path)
        self.writing_module = ToolEnabledWritingModule(project_path)
        
        print(f"工具调用集成示例初始化完成")
        print(f"项目路径: {project_path}")
    
    def demonstrate_character_creation(self) -> Dict[str, Any]:
        """演示人物创建功能"""
        print("\n=== 演示人物创建功能 ===")
        
        # 创建主角
        print("1. 创建主角人物...")
        protagonist = self.character_module.create_character(
            name="林风",
            role="主角",
            basic_info={
                "age": 25,
                "gender": "男",
                "appearance": "身材修长，眼神锐利，黑色短发"
            },
            personality={
                "traits": ["冷静", "果断", "重情义"],
                "strengths": ["剑术高超", "观察力强"],
                "weaknesses": ["有时过于固执"]
            },
            background="曾是皇家卫队成员，因故离开后成为自由佣兵"
        )
        
        print(f"主角创建成功: {protagonist['name']}")
        
        # 创建配角
        print("\n2. 创建配角人物...")
        supporting = self.character_module.create_character(
            name="苏婉儿",
            role="配角",
            basic_info={
                "age": 22,
                "gender": "女", 
                "appearance": "温婉秀丽，长发及腰，气质优雅"
            },
            personality={
                "traits": ["温柔", "聪慧", "坚韧"],
                "strengths": ["医术高明", "善于交际"],
                "weaknesses": ["有时过于善良"]
            },
            background="医馆之女，因家族变故踏上寻亲之路"
        )
        
        print(f"配角创建成功: {supporting['name']}")
        
        return {
            "protagonist": protagonist,
            "supporting": supporting
        }
    
    def demonstrate_outline_generation(self, story_concept: str, character_names: List[str]) -> Dict[str, Any]:
        """演示大纲生成功能"""
        print("\n=== 演示大纲生成功能 ===")
        
        print(f"故事概念: {story_concept}")
        print(f"涉及人物: {character_names}")
        
        # 生成包含人物的故事大纲
        outline = self.outline_module.generate_outline_with_characters(
            story_concept=story_concept,
            character_names=character_names
        )
        
        print(f"大纲生成成功: {outline['title']}")
        print(f"包含 {len(outline.get('parts', []))} 个部分")
        
        # 统计章节数量
        total_chapters = 0
        for part in outline.get("parts", []):
            total_chapters += len(part.get("chapters", []))
        
        print(f"总计 {total_chapters} 个章节")
        
        return outline
    
    def demonstrate_chapter_writing(self, outline_data: Dict[str, Any], character_names: List[str]) -> str:
        """演示章节创作功能"""
        print("\n=== 演示章节创作功能 ===")
        
        # 选择第一个章节进行创作
        first_chapter = None
        for part in outline_data.get("parts", []):
            if part.get("chapters"):
                first_chapter = part["chapters"][0]
                break
        
        if not first_chapter:
            print("未找到可创作的章节")
            return ""
        
        chapter_id = first_chapter["id"]
        chapter_title = first_chapter["title"]
        
        print(f"创作章节: {chapter_title} ({chapter_id})")
        
        # 创作章节内容
        content = self.writing_module.write_chapter_with_characters(
            outline_data=outline_data,
            chapter_id=chapter_id,
            character_names=character_names
        )
        
        print(f"章节创作完成，内容长度: {len(content)} 字符")
        
        return content
    
    def demonstrate_tool_usage_analysis(self):
        """演示工具使用分析"""
        print("\n=== 演示工具使用分析 ===")
        
        # 创建工具调用模型管理器实例
        model_manager = ToolEnabledModelManager()
        
        # 获取可用工具列表
        available_tools = model_manager.tool_manager.list_tools()
        print(f"可用工具: {available_tools}")
        
        # 显示每个工具的详细信息
        for tool_name in available_tools:
            tool_info = model_manager.tool_manager.get_tool_info(tool_name)
            if tool_info:
                function_info = tool_info.get("function", {})
                print(f"\n工具: {tool_name}")
                print(f"描述: {function_info.get('description', '无描述')}")
                print(f"参数: {function_info.get('parameters', {})}")
        
        # 演示直接工具调用
        print("\n=== 演示直接工具调用 ===")
        
        # 直接创建人物
        print("1. 直接创建人物...")
        result = model_manager.create_character_directly(
            name="李逍遥",
            role="主角",
            basic_info={"age": 20, "gender": "男", "appearance": "英俊潇洒"},
            personality={"traits": ["机智", "幽默", "重情义"]},
            background="江湖游侠，擅长剑术"
        )
        
        if "error" not in result:
            print(f"直接创建人物成功: {result.get('character_name', '未知')}")
        else:
            print(f"直接创建人物失败: {result['error']}")
        
        # 直接读取人物
        print("\n2. 直接读取人物...")
        result = model_manager.read_character_directly("李逍遥")
        
        if "error" not in result:
            print(f"直接读取人物成功: {result.get('character_name', '未知')}")
            character_data = result.get("character_data", {})
            print(f"人物信息: {character_data.get('role', '未知')} - {character_data.get('background', '背景待补充')}")
        else:
            print(f"直接读取人物失败: {result['error']}")
        
        # 显示工具使用统计
        print("\n=== 工具使用统计 ===")
        stats = model_manager.get_tool_usage_statistics()
        print(f"总工具调用次数: {stats.get('total_tool_calls', 0)}")
        for tool_name in available_tools:
            print(f"{tool_name} 使用次数: {stats.get(tool_name, 0)}")
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("开始运行工具调用集成完整演示...")
        
        # 1. 演示人物创建
        characters = self.demonstrate_character_creation()
        character_names = list(characters.keys())
        
        # 2. 演示大纲生成
        story_concept = "一个关于佣兵林风与医女苏婉儿共同寻找真相的冒险故事"
        outline = self.demonstrate_outline_generation(story_concept, character_names)
        
        # 3. 演示章节创作
        content = self.demonstrate_chapter_writing(outline, character_names)
        
        # 4. 演示工具使用分析
        self.demonstrate_tool_usage_analysis()
        
        # 保存演示结果
        self._save_demo_results(characters, outline, content)
        
        print("\n=== 演示完成 ===")
        print(f"项目文件保存在: {self.project_path}")
    
    def _save_demo_results(self, characters: Dict[str, Any], outline: Dict[str, Any], content: str):
        """保存演示结果"""
        # 保存人物信息
        characters_file = os.path.join(self.project_path, "demo_characters.json")
        self.file_manager.write_json(characters_file, characters)
        
        # 保存大纲
        outline_file = os.path.join(self.project_path, "demo_outline.json")
        self.file_manager.write_json(outline_file, outline)
        
        # 保存章节内容
        content_file = os.path.join(self.project_path, "demo_chapter_content.txt")
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 创建演示报告
        report = {
            "demo_timestamp": datetime.now().isoformat(),
            "characters_created": len(characters),
            "outline_parts": len(outline.get("parts", [])),
            "total_chapters": sum(len(part.get("chapters", [])) for part in outline.get("parts", [])),
            "chapter_content_length": len(content),
            "files_generated": [
                "demo_characters.json",
                "demo_outline.json", 
                "demo_chapter_content.txt"
            ]
        }
        
        report_file = os.path.join(self.project_path, "demo_report.json")
        self.file_manager.write_json(report_file, report)
        
        print(f"演示结果已保存到: {self.project_path}")


def main():
    """主函数"""
    print("工具调用集成示例程序")
    print("=" * 50)
    
    # 创建示例实例
    example = ToolIntegrationExample()
    
    # 运行完整演示
    example.run_complete_demo()
    
    print("\n程序执行完毕！")


if __name__ == "__main__":
    main()