#!/usr/bin/env python3
# check_imports.py - 检查导入

import sys
import traceback

def check_imports():
    """检查所有必要的导入"""
    modules = [
        "memory_manager",
        "summary_manager", 
        "history_manager",
        "conversation_manager",
        "tool_manager",
        "model_message"
    ]
    
    print("检查导入...")
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} 导入成功")
        except ImportError as e:
            print(f"✗ {module} 导入失败: {e}")
            traceback.print_exc()
            return False
    
    print("\n所有导入检查通过！")
    return True

if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)