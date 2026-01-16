#!/usr/bin/env python3
"""简单测试JSON解析功能"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接导入函数进行测试
def test_fix_json_format():
    """测试JSON格式修复功能"""
    from model_manager import APIModelManager
    
    manager = APIModelManager()
    
    # 测试中文标点修复
    test_cases = [
        # 中文双引号
        ('{“title”: "测试"}', '{"title": "测试"}'),
        # 中文冒号
        ('{"title"： "测试"}', '{"title": "测试"}'),
        # 中文逗号
        ('{"title": "测试"， "value": 1}', '{"title": "测试", "value": 1}'),
        # 混合问题
        ('{“title”： "测试"， "value"： 1}', '{"title": "测试", "value": 1}'),
    ]
    
    print("测试JSON格式修复功能...")
    
    for input_text, expected in test_cases:
        result = manager._fix_json_format(input_text)
        print(f"输入: {input_text}")
        print(f"输出: {result}")
        print(f"期望: {expected}")
        print(f"结果: {'✓' if result == expected else '✗'}")
        print("-" * 40)

def test_extract_json():
    """测试JSON提取功能"""
    from model_manager import APIModelManager
    
    manager = APIModelManager()
    
    # 测试用例
    test_cases = [
        ('{"title": "正常JSON"}', "正常JSON"),
        ('{“title”: "中文双引号"}', "中文双引号"),
        ('{"title"： "中文冒号"}', "中文冒号"),
    ]
    
    print("\n测试JSON提取功能...")
    
    for input_text, description in test_cases:
        print(f"测试: {description}")
        result = manager.extract_json(input_text)
        if result:
            print(f"✓ 解析成功: {result}")
        else:
            print("✗ 解析失败")
        print("-" * 40)

if __name__ == "__main__":
    test_fix_json_format()
    test_extract_json()
    print("测试完成!")