#!/usr/bin/env python3
# direct_test.py - 直接测试总结管理器

import json
import os

def test_memory_keywords():
    """测试记忆关键词"""
    print("测试记忆关键词...")
    
    # 记忆管理器的关键词
    keywords = {
        "agreement": ["同意", "好的", "可以", "行", "没问题", "赞成", "接受", "ok", "okay", "yes", "yeah", "好"],
        "personal": ["名字", "姓名", "叫我", "称呼", "年龄", "岁数", "性别", "住在", "家乡", "来自", "工作", "职业", "爱好", "喜欢", "生日"],
        "preference": ["喜欢", "不喜欢", "讨厌", "偏好", "习惯", "经常", "总是", "从不", "爱", "恨", "习惯性", "爱喝", "爱吃"],
        "task": ["帮我", "需要", "想要", "请", "请求", "要求", "任务", "完成", "做", "写", "修改", "创建", "删除"],
        "technical": ["代码", "编程", "python", "java", "javascript", "html", "css", "api", "数据库", "算法", "函数", "类"]
    }
    
    # 测试内容
    test_contents = [
        ("好的，我同意", "agreement"),
        ("我的名字是张三", "personal"),
        ("我喜欢苹果", "preference"),
        ("帮我写代码", "task"),
        ("用python实现", "technical"),
    ]
    
    for content, expected_category in test_contents:
        print(f"\n测试: '{content}'")
        found = False
        for category, words in keywords.items():
            for word in words:
                if word in content:
                    print(f"  发现关键词 '{word}' -> 分类 '{category}'")
                    found = True
                    break
            if found:
                break
        if not found:
            print("  未发现关键词")
    
    return True

def create_test_data():
    """创建测试数据文件"""
    print("\n创建测试数据...")
    
    # 创建测试记忆文件
    test_memory = {
        "test_user": {
            "created_at": "2025-12-18T22:00:00.000000",
            "last_updated": "2025-12-18T22:00:00.000000",
            "memories": [
                {
                    "category": "agreement",
                    "content": "好的，我同意这个方案",
                    "original_text": "好的，我同意这个方案",
                    "timestamp": "2025-12-18T22:00:01.000000",
                    "description": "用户同意的内容"
                },
                {
                    "category": "personal",
                    "content": "我的名字叫李四",
                    "original_text": "我的名字叫李四",
                    "timestamp": "2025-12-18T22:00:02.000000",
                    "description": "个人信息"
                },
                {
                    "category": "preference",
                    "content": "我喜欢简洁的设计",
                    "original_text": "我喜欢简洁的设计",
                    "timestamp": "2025-12-18T22:00:03.000000",
                    "description": "用户偏好习惯"
                },
                {
                    "category": "task",
                    "content": "帮我创建一个登录页面",
                    "original_text": "帮我创建一个登录页面",
                    "timestamp": "2025-12-18T22:00:04.000000",
                    "description": "任务需求"
                },
                {
                    "category": "technical",
                    "content": "用React实现",
                    "original_text": "用React实现",
                    "timestamp": "2025-12-18T22:00:05.000000",
                    "description": "技术相关"
                }
            ]
        }
    }
    
    # 写入文件
    with open("test_memory.json", "w", encoding="utf-8") as f:
        json.dump(test_memory, f, ensure_ascii=False, indent=2)
    
    print("测试记忆文件已创建: test_memory.json")
    
    # 创建测试总结文件
    test_summary = {
        "test_user": {
            "created_at": "2025-12-18T22:00:00.000000",
            "last_updated": "2025-12-18T22:00:00.000000",
            "summaries": {
                "agreement": {
                    "content": "用户同意的内容：好的，我同意这个方案",
                    "last_updated": "2025-12-18T22:00:00.000000",
                    "category_name": "用户同意的内容",
                    "memory_count": 1
                },
                "personal": {
                    "content": "个人信息：我的名字叫李四",
                    "last_updated": "2025-12-18T22:00:00.000000",
                    "category_name": "个人信息",
                    "memory_count": 1
                },
                "preference": {
                    "content": "用户偏好习惯：我喜欢简洁的设计",
                    "last_updated": "2025-12-18T22:00:00.000000",
                    "category_name": "用户偏好习惯",
                    "memory_count": 1
                },
                "task": {
                    "content": "任务需求：帮我创建一个登录页面",
                    "last_updated": "2025-12-18T22:00:00.000000",
                    "category_name": "任务需求",
                    "memory_count": 1
                },
                "technical": {
                    "content": "技术相关：用React实现",
                    "last_updated": "2025-12-18T22:00:00.000000",
                    "category_name": "技术相关",
                    "memory_count": 1
                }
            }
        }
    }
    
    with open("test_summary.json", "w", encoding="utf-8") as f:
        json.dump(test_summary, f, ensure_ascii=False, indent=2)
    
    print("测试总结文件已创建: test_summary.json")
    
    return True

def test_summary_generation():
    """测试总结生成"""
    print("\n测试总结生成...")
    
    # 模拟总结生成逻辑
    memories = [
        {"category": "agreement", "content": "好的，我同意"},
        {"category": "agreement", "content": "没问题，可以"},
        {"category": "personal", "content": "我叫王五"},
        {"category": "personal", "content": "我是程序员"},
        {"category": "preference", "content": "喜欢暗色主题"},
        {"category": "task", "content": "帮我写代码"},
        {"category": "technical", "content": "用Python实现"},
    ]
    
    categories = {
        "agreement": "用户同意的内容",
        "personal": "个人信息",
        "preference": "用户偏好习惯",
        "task": "任务需求",
        "technical": "技术相关"
    }
    
    # 按分类分组
    grouped = {}
    for memory in memories:
        category = memory["category"]
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(memory["content"])
    
    # 生成总结
    summary_parts = []
    for category, items in grouped.items():
        category_name = categories.get(category, category)
        
        if len(items) <= 3:
            summary = f"{category_name}：{'；'.join(items)}"
        else:
            recent_items = items[-3:]  # 取最近3条
            summary = f"{category_name}（最近记录）：{'；'.join(recent_items)}"
        
        summary_parts.append(summary)
    
    full_summary = "；".join(summary_parts)
    
    print("生成的总结:")
    print(full_summary)
    
    # 生成喵喵副脑格式
    prompt = f"\n\n### 喵喵副脑：\n{full_summary}\n"
    print("\n喵喵副脑格式:")
    print(prompt)
    
    return True

def main():
    print("=== 直接测试总结功能 ===")
    
    # 测试关键词
    test_memory_keywords()
    
    # 创建测试数据
    create_test_data()
    
    # 测试总结生成
    test_summary_generation()
    
    print("\n=== 测试完成 ===")
    print("总结性prompt生成逻辑测试完成。")
    print("实际使用时，系统会自动从用户对话中提取记忆并生成总结。")

if __name__ == "__main__":
    main()