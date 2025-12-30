#!/usr/bin/env python3
# run_test.py - 运行测试

import subprocess
import sys

def run_test():
    """运行测试"""
    print("运行总结管理器测试...")
    
    try:
        # 运行测试脚本
        result = subprocess.run([sys.executable, "test_summary.py"], 
                               capture_output=True, text=True, encoding='utf-8')
        
        print("输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
            
        if result.returncode != 0:
            print(f"测试失败，返回码: {result.returncode}")
        else:
            print("测试成功完成")
            
    except Exception as e:
        print(f"运行测试时出错: {e}")

if __name__ == "__main__":
    run_test()