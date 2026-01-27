#!/usr/bin/env python3
"""测试修改后的人物创建工具"""

import sys
import os
import json

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tool_enabled_model_manager import ToolEnabledModelManager, CreateCharacterTool, SimpleModelCaller

def test_character_creation():
    """测试人物创建功能"""
    
    # 创建工具实例
    character_tool = CreateCharacterTool()
    
    # 测试数据
    test_arguments = {
        "name": "林婉儿",
        "role": "女主角",
        "basic_info": {
            "age": 22,
            "gender": "女",
            "occupation": "大学生"
        },
        "personality": {
            "traits": ["善良", "独立", "有主见"],
            "values": ["正义", "自由", "真诚"]
        },
        "background": "一个普通家庭出身的女孩，父母都是教师，从小受到良好的教育",
        "story_requirements": "需要成为一个有成长弧线的女主角，从青涩到成熟"
    }
    
    print("开始测试人物创建工具...")
    print("测试数据:")
    print(json.dumps(test_arguments, ensure_ascii=False, indent=2))
    print("\n" + "="*50 + "\n")
    
    try:
        # 执行工具
        result = character_tool.execute(test_arguments)
        
        # 解析结果
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print("✅ 人物创建成功!")
            print(f"角色名称: {result_data.get('character_name')}")
            print(f"文件路径: {result_data.get('file_path')}")
            print(f"模型回复: {result_data.get('model_response')[:200]}...")
            
            # 显示创建的人物数据
            character_data = result_data.get("character_data", {})
            print("\n创建的人物数据:")
            print(json.dumps(character_data, ensure_ascii=False, indent=2))
            
            # 检查文件是否创建成功
            file_path = result_data.get("file_path")
            if os.path.exists(file_path):
                print(f"\n✅ 人物文件已成功创建: {file_path}")
                
                # 读取文件内容验证
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = json.load(f)
                print("\n文件内容验证通过!")
            else:
                print(f"❌ 人物文件未找到: {file_path}")
                
        else:
            print("❌ 人物创建失败!")
            print(f"错误信息: {result_data.get('error')}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_tool_enabled_model():
    """测试完整的工具调用模型"""
    
    print("\n" + "="*50)
    print("测试完整的工具调用模型...")
    print("="*50 + "\n")
    
    try:
        # 创建模型管理器
        model_manager = ToolEnabledModelManager()
        
        # 测试提示词
        prompt = "请创建一个名为'张明'的男主角，他是一名25岁的程序员，性格内向但聪明，需要为科幻故事服务。"
        
        print(f"发送提示词: {prompt}")
        
        # 调用模型（应该会触发工具调用）
        response = model_manager.call_model_with_tools(
            prompt=prompt,
            system_prompt="你是一个小说创作助手，可以帮助用户创建角色和故事内容。",
            max_iterations=3
        )
        
        print("\n模型回复:")
        print(response)
        
        # 检查历史记录
        history = model_manager.get_history()
        if history:
            print(f"\n调用历史记录 ({len(history)} 条):")
            for i, record in enumerate(history, 1):
                print(f"\n记录 {i}:")
                print(f"  迭代次数: {record.get('iterations', 1)}")
                print(f"  提示词: {record.get('prompt')[:100]}...")
                print(f"  回复: {record.get('response')[:200]}...")
        
    except Exception as e:
        print(f"❌ 模型调用测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*50)
    print("人物创建工具测试")
    print("="*50)
    
    # 测试直接工具调用
    test_character_creation()
    
    # 测试完整的模型工具调用
    test_tool_enabled_model()
    
    print("\n" + "="*50)
    print("测试完成!")
    print("="*50)