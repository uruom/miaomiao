#!/usr/bin/env python3
# simple_test.py - 简单测试

from memory_manager import get_memory_manager
from summary_manager import get_summary_manager

def main():
    print("测试总结管理器...")
    
    # 获取管理器
    memory_manager = get_memory_manager()
    summary_manager = get_summary_manager()
    
    # 添加一些测试记忆
    print("\n1. 添加测试记忆...")
    test_memories = [
        ("我同意这个方案", "agreement"),
        ("我叫小明", "personal"),
        ("我喜欢吃苹果", "preference"),
        ("帮我写代码", "task"),
        ("用Python实现", "technical"),
        ("好的，没问题", "agreement"),
        ("我是程序员", "personal"),
        ("讨厌香蕉", "preference"),
        ("修复bug", "task"),
        ("JavaScript也行", "technical"),
    ]
    
    for content, category in test_memories:
        memory_manager.add_memory("test_user", content, "user")
    
    # 更新总结
    print("\n2. 更新总结...")
    summary_manager.update_summaries("test_user")
    
    # 获取总结
    print("\n3. 获取总结性prompt:")
    prompt = summary_manager.get_summary_prompt("test_user")
    print(prompt)
    
    # 显示总结详情
    print("\n4. 总结详情:")
    if "test_user" in summary_manager.summaries:
        summaries = summary_manager.summaries["test_user"].get("summaries", {})
        for category, data in summaries.items():
            print(f"  [{category}]: {data.get('content', '')}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()