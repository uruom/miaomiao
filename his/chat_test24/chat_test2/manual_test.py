#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手动测试记忆功能"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_manager import get_memory_manager

def test_memory():
    """测试记忆功能"""
    print("=== 测试记忆管理器 ===\n")
    
    # 获取记忆管理器
    memory_manager = get_memory_manager()
    
    # 测试分析内容
    test_contents = [
        "我叫张三",
        "我今年25岁",
        "我喜欢吃火锅",
        "我讨厌下雨天",
        "好的，我同意这个方案",
        "帮我写一段Python代码",
        "我喜欢喝咖啡",
        "我的职业是程序员"
    ]
    
    print("测试内容分析:")
    for content in test_contents:
        categories = memory_manager.analyze_content(content)
        print(f"内容: {content}")
        print(f"分析结果: {categories}")
        
        # 提取记忆信息
        if categories:
            for category in categories:
                info = memory_manager.extract_memory_info(category, content)
                print(f"  类别 {category}: {info}")
        print()
    
    # 测试添加记忆
    print("\n=== 测试添加记忆 ===")
    for content in test_contents:
        print(f"添加记忆: {content}")
        memory_manager.add_memory("test_user", content, "user")
    
    # 查看记忆
    print("\n=== 查看记忆 ===")
    memories = memory_manager.get_user_memories("test_user")
    for i, memory in enumerate(memories):
        print(f"{i+1}. [{memory['category']}] {memory['content']}")
    
    # 获取摘要
    print("\n=== 记忆摘要 ===")
    summary = memory_manager.get_memory_summary("test_user")
    print(f"摘要: {summary}")
    
    # 保存文件
    print("\n=== 检查文件 ===")
    if os.path.exists("user_memory.json"):
        print("记忆文件已创建")
        import json
        with open("user_memory.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"文件内容预览: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
    else:
        print("记忆文件未创建")

if __name__ == "__main__":
    test_memory()