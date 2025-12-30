#!/usr/bin/env python3
# demo_summary.py - 演示总结性prompt功能

import json
import os
from memory_manager import get_memory_manager
from summary_manager import get_summary_manager

def main():
    print("=== 喵喵副脑总结性prompt演示 ===")
    print("本演示展示如何将用户记忆整合为总结性prompt\n")
    
    # 清理旧的测试数据
    if os.path.exists("summary_prompts.json"):
        os.remove("summary_prompts.json")
        print("已清理旧的总结文件")
    
    # 创建新的记忆管理器
    memory_manager = get_memory_manager()
    summary_manager = get_summary_manager()
    
    # 1. 添加不同类型的用户记忆（确保包含关键词）
    print("\n1. 添加用户记忆...")
    
    test_conversations = [
        ("好的，我同意修改代码风格", "agreement"),
        ("我的名字叫张三", "personal"),
        ("我喜欢简洁的设计风格", "preference"),
        ("帮我创建一个登录页面", "task"),
        ("用React实现这个功能", "technical"),
        ("可以，确认这个方案", "agreement"),
        ("我是前端开发工程师", "personal"),
        ("我讨厌复杂的界面", "preference"),
        ("需要添加表单验证功能", "task"),
        ("要用TypeScript来写", "technical"),
        ("行，同意时间安排", "agreement"),
        ("我在北京工作", "personal"),
        ("习惯用暗色主题", "preference"),
        ("要求优化页面性能", "task"),
        ("建议用Webpack打包代码", "technical"),
    ]
    
    for i, (content, category) in enumerate(test_conversations, 1):
        memory_manager.add_memory("demo_user", content, "user")
        print(f"  添加记忆 {i}: [{category}] {content}")
    
    # 2. 显示记忆数据
    print("\n2. 当前记忆数据:")
    memories = memory_manager.get_user_memories("demo_user")
    if memories:
        for i, memory in enumerate(memories, 1):
            print(f"  {i:2d}. [{memory['category']:10}] {memory['content']}")
    else:
        print("  没有找到记忆数据，可能是因为内容不包含关键词")
        # 显示关键词供参考
        print("\n  记忆管理器关键词:")
        memory_manager = get_memory_manager()
        for category, config in memory_manager.keyword_categories.items():
            print(f"  [{category}]: {', '.join(config['keywords'][:3])}...")
    
    # 3. 生成并显示总结性prompt
    print("\n3. 生成总结性prompt...")
    summary_manager.update_summaries("demo_user")
    
    print("\n4. 生成的总结性prompt内容:")
    summary_prompt = summary_manager.get_summary_prompt("demo_user")
    if summary_prompt:
        print(summary_prompt)
    else:
        print("  没有生成总结性prompt")
    
    # 5. 显示总结详情
    print("\n5. 总结详情:")
    if "demo_user" in summary_manager.summaries:
        user_summary = summary_manager.summaries["demo_user"]
        print(f"  创建时间: {user_summary.get('created_at', '未知')}")
        print(f"  更新时间: {user_summary.get('last_updated', '未知')}")
        
        summaries = user_summary.get("summaries", {})
        print(f"  总结分类数: {len(summaries)}")
        
        for category, data in summaries.items():
            print(f"\n  [{category}] {data.get('category_name', category)}:")
            print(f"    内容: {data.get('content', '')}")
            print(f"    记忆数量: {data.get('memory_count', 0)}")
    else:
        print("  没有找到总结数据")
    
    # 6. 展示如何集成到system prompt
    print("\n6. 集成到system prompt示例:")
    base_system_prompt = """# 你是喵喵

嘴上嫌弃用户笨，心里还是愿意默默帮助用户完成所有的请求。"""
    
    if summary_prompt:
        enhanced_prompt = base_system_prompt + summary_prompt
        print("原始system prompt + 总结性prompt:")
        print("-" * 50)
        print(enhanced_prompt)
        print("-" * 50)
    else:
        print("  没有总结性prompt可集成")
    
    # 7. 保存文件内容展示
    print("\n7. 生成的文件:")
    if os.path.exists("summary_prompts.json"):
        with open("summary_prompts.json", "r", encoding="utf-8") as f:
            summary_data = json.load(f)
        
        print(f"  summary_prompts.json: {len(json.dumps(summary_data, ensure_ascii=False))} 字符")
        print(f"  包含用户: {list(summary_data.keys())}")
    
    if os.path.exists("user_memory.json"):
        with open("user_memory.json", "r", encoding="utf-8") as f:
            memory_data = json.load(f)
        
        print(f"  user_memory.json: {len(json.dumps(memory_data, ensure_ascii=False))} 字符")
        if "demo_user" in memory_data:
            demo_memories = memory_data["demo_user"].get("memories", [])
            print(f"  demo_user记忆数量: {len(demo_memories)}")
    
    print("\n=== 演示完成 ===")
    print("总结性prompt已成功生成并可以注入到system prompt中。")
    print("每次用户对话后，总结会自动更新。")

if __name__ == "__main__":
    main()