#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将转义字符串转换回正常文本
支持命令行输入和文件输入输出
"""
import argparse
import json

def escaped_string_to_text(escaped_string):
    """将转义字符串转换回正常文本"""
    try:
        # 使用json.loads来处理转义，这样可以正确还原换行符、引号等
        return json.loads(escaped_string)
    except json.JSONDecodeError as e:
        print(f"字符串解析失败: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='将转义字符串转换回正常文本')
    parser.add_argument('--string', '-s', type=str, help='直接输入的转义字符串')
    parser.add_argument('--input', '-i', type=str, help='输入文件路径')
    parser.add_argument('--output', '-o', type=str, help='输出文件路径')
    
    args = parser.parse_args()
    
    # 获取输入字符串
    if args.string:
        input_string = args.string
    elif args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                input_string = f.read().strip()  # 去除可能的首尾空白
        except Exception as e:
            print(f"读取输入文件失败: {e}")
            return
    else:
        # 如果没有提供命令行参数，从标准输入读取
        print("请输入要转换的转义字符串（按Ctrl+D结束输入）:")
        input_string = '''
        
        '''
        try:
            while True:
                line = input()
                input_string += line
        except EOFError:
            pass
        input_string = input_string.strip()
    
    # 转换字符串
    normal_text = escaped_string_to_text(input_string)
    
    if normal_text is None:
        return
    
    # 输出结果
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(normal_text)
            print(f"转换结果已保存到 {args.output}")
        except Exception as e:
            print(f"写入输出文件失败: {e}")
    else:
        print("\n转换后的正常文本:")
        print(normal_text)

if __name__ == "__main__":
    main()
