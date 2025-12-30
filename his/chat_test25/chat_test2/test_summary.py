#!/usr/bin/env python3
# test_summary.py - 测试总结管理器功能

from memory_manager import get_memory_manager
from summary_manager import get_summary_manager

def test_summary_system():
    """测试总结系统"""
    print("=== 测试总结管理器 ===")
    
    # 获取管理器实例
    memory_manager = get_memory_manager()
    summary_manager = get_summary_manager()
    
    # 1. 显示当前记忆
    print("\n1. 当前记忆数据:")
    memories = memory_manager.get_user_memories("default")
    for i, memory in enumerate(memories, 1):
        print(f"  {i}. [{memory['category']}] {memory['content'][:50]}...")
    
    # 2. 更新总结
    print("\n2. 更新总结性prompt...")
    summary_manager.update_summaries("default")
    
    # 3. 获取总结性prompt
    print("\n3. 生成的总结性prompt:")
    summary_prompt = summary_manager.get_summary_prompt("default")
    if summary_prompt:
        print(summary_prompt)
    else:
        print("  无总结性prompt")
    
    # 4. 显示总结详情
    print("\n4. 总结详情:")
    if "default" in summary_manager.summaries:
        summaries = summary_manager.summaries["default"].get("summaries", {})
        for category, data in summaries.items():
            print(f"  [{category}] {data.get('category_name', category)}:")
            print(f"    内容: {data.get('content', '')}")
            print(f"    记忆数量: {data.get('memory_count', 0)}")
            print(f"    更新时间: {data.get('last_updated', '')}")
    else:
        print("  无总结数据")
    
    # 5. 测试分类总结
    print("\n5. 分类总结:")
    for category in ["agreement", "personal", "preference", "task", "technical"]:
        summary = summary_manager.get_summary_for_category("default", category)
        if summary:
            print(f"  [{category}]: {summary}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_summary_system()