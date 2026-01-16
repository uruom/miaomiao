#!/usr/bin/env python3
"""测试JSON解析器的后处理功能"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_manager import APIModelManager

def test_json_parsing():
    """测试各种JSON解析场景"""
    manager = APIModelManager()
    
    # 测试用例
    test_cases = [
        # 1. 正常JSON
        ('{"title": "正常标题", "parts": [{"name": "部分1"}]}', "正常JSON"),
        
        # 2. 中文双引号问题
        ('{“title”: "中文双引号标题", “parts”: [{“name”: “部分1”}]}', "中文双引号"),
        
        # 3. 中文冒号问题
        ('{"title"： "中文冒号标题", "parts"： [{"name"： "部分1"}]}', "中文冒号"),
        
        # 4. 中文逗号问题
        ('{"title": "中文逗号标题"， "parts": [{"name": "部分1"}， {"name": "部分2"}]}', "中文逗号"),
        
        # 5. 混合问题
        ('{“title”： "混合问题标题"， "parts"： [{“name”： "部分1"}， {“name”： "部分2"}]}', "混合问题"),
        
        # 6. JSON代码块
        ('```json\n{"title": "代码块标题", "parts": [{"name": "部分1"}]}\n```', "JSON代码块"),
        
        # 7. 包含中文标点的代码块
        ('```json\n{“title”： "代码块中文标题"， "parts"： [{“name”： "部分1"}]}\n```', "代码块中文标点"),
        
        # 8. 属性名缺少引号
        ('{title: "缺少引号标题", parts: [{name: "部分1"}]}', "缺少引号"),
        
        # 9. 末尾多余逗号
        ('{"title": "多余逗号标题", "parts": [{"name": "部分1"},]},', "多余逗号"),
        
        # 10. 布尔值大小写问题
        ('{"title": "布尔值标题", "published": TRUE, "active": False}', "布尔值大小写"),
    ]
    
    print("开始测试JSON解析器...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_input, description in test_cases:
        print(f"\n测试: {description}")
        print(f"输入: {test_input[:100]}...")
        
        try:
            result = manager.extract_json(test_input)
            if result:
                print(f"✓ 解析成功: {result}")
                passed += 1
            else:
                print("✗ 解析失败")
                failed += 1
        except Exception as e:
            print(f"✗ 解析异常: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: 通过 {passed}/10, 失败 {failed}/10")
    
    # 测试复杂场景
    print("\n测试复杂场景...")
    complex_test = """
    这是一个包含JSON的文本，JSON如下：
    
    {“title”： "复杂故事标题"，
     “concept”： "这是一个复杂的故事概念，包含各种标点符号。"，
     “parts”： [
         {“part_title”： "第一部分"，
          “chapters”： [
              {“id”： "ch_1"， “title”： "章节一"， “summary”： "章节概要，包含中文标点。"}，
              {“id”： "ch_2"， “title”： "章节二"， “summary”： "另一个章节概要。"}
          ]
         }
     ]
    }
    
    这是JSON后面的文本。
    """
    
    print("复杂测试输入:")
    print(complex_test)
    
    result = manager.extract_json(complex_test)
    if result:
        print("✓ 复杂场景解析成功:")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("✗ 复杂场景解析失败")

if __name__ == "__main__":
    test_json_parsing()