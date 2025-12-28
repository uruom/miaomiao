# memory_manager.py
import json
import os
import re
import uuid
from typing import Dict, Any, List, Optional, Set
from datetime import datetime


class MemoryManager:
    """记忆管理器 - 用于记录用户对话中的关键信息"""
    
    def __init__(self, memory_file: str = "user_memory.json"):
        self.memory_file = memory_file
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.load_memory()
        
        # 关键词分类定义
        self.keyword_categories = {
            "agreement": {
                "keywords": ["同意", "好的", "可以", "行", "没问题", "赞成", "接受", "ok", "okay", "yes", "yeah", "好"],
                "description": "用户同意的内容"
            },
            "personal": {
                "keywords": ["名字", "姓名", "叫我", "称呼", "年龄", "岁数", "性别", "住在", "家乡", "来自", "工作", "职业", "爱好", "喜欢", "生日"],
                "description": "个人信息"
            },
            "preference": {
                "keywords": ["喜欢", "不喜欢", "讨厌", "偏好", "习惯", "经常", "总是", "从不", "爱", "恨", "习惯性", "爱喝", "爱吃"],
                "description": "用户偏好习惯"
            },
            "task": {
                "keywords": ["帮我", "需要", "想要", "请", "请求", "要求", "任务", "完成", "做", "写", "修改", "创建", "删除"],
                "description": "任务需求"
            },
            "technical": {
                "keywords": ["代码", "编程", "python", "java", "javascript", "html", "css", "api", "数据库", "算法", "函数", "类"],
                "description": "技术相关"
            }
        }
        
    def load_memory(self):
        """加载记忆文件"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
                print(f"已加载记忆文件: {self.memory_file}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载记忆文件失败: {e}")
                self.memories = {}
        else:
            print(f"记忆文件不存在，将创建: {self.memory_file}")
            self.memories = {}
    
    def save_memory(self):
        """保存记忆到文件"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
            print(f"记忆已保存到: {self.memory_file}")
        except IOError as e:
            print(f"保存记忆文件失败: {e}")
    
    def analyze_content(self, content: str) -> Dict[str, List[str]]:
        """分析内容，提取关键信息"""
        results = {}
        content_lower = content.lower()
        
        for category, config in self.keyword_categories.items():
            found_keywords = []
            for keyword in config["keywords"]:
                # 使用正则匹配单词边界，避免部分匹配
                if keyword in content_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                results[category] = found_keywords
        
        return results
    
    def extract_memory_info(self, category: str, content: str) -> Optional[str]:
        content = content.strip()
        if not content or len(content)<2:
            return None
        return content
    
    def add_memory(self, user_id: str = "default", content: str = None, role: str = "user"):
        """添加记忆 - 只记录用户消息"""
        if role != "user" or not content:
            return
        
        print(f"分析用户消息: {content[:50]}...")
        
        # 分析内容
        categories = self.analyze_content(content)
        
        if not categories:
            print("未发现关键词，跳过记忆")
            return
        
        print(f"发现关键词类别: {list(categories.keys())}")
        
        # 确保用户记忆字典存在
        if user_id not in self.memories:
            self.memories[user_id] = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "memories": []
            }
        
        # 提取记忆信息
        memory_items = []
        for category_name in categories:
            info = self.extract_memory_info(category_name, content)
            if info:
                # 按照新格式创建记忆项
                memory_item = {
                    "type": category_name,
                    "content": info,
                    "tags": ["general"],
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat()
                }
                memory_items.append(memory_item)
                print(f"提取记忆: {category_name} - {info}")
        
        # 添加到记忆列表
        if memory_items:
            self.memories[user_id]["memories"].extend(memory_items)
            self.memories[user_id]["last_updated"] = datetime.now().isoformat()
            
            # 去重 - 基于内容和类型
            unique_memories = []
            seen = set()
            for item in self.memories[user_id]["memories"]:
                key = (item["type"], item["content"])
                if key not in seen:
                    seen.add(key)
                    unique_memories.append(item)
            
            self.memories[user_id]["memories"] = unique_memories
            self.save_memory()
            print(f"已保存 {len(memory_items)} 条记忆")
        else:
            print("未提取到有效记忆信息")
    
    def get_user_memories(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """获取用户的记忆"""
        if user_id in self.memories:
            return self.memories[user_id].get("memories", [])
        return []
    
    def get_memory_summary(self, user_id: str = "default") -> str:
        """获取记忆摘要"""
        memories = self.get_user_memories(user_id)
        if not memories:
            return ""
        
        print(f"获取到 {len(memories)} 条记忆")
        
        # 按类别分组
        grouped = {}
        for memory in memories:
            category = memory["type"]
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(memory["content"])
        
        # 生成摘要
        summary_parts = []
        for category, items in grouped.items():
            category_name = self.keyword_categories.get(category, {}).get("description", category)
            summary_parts.append(f"{category_name}: {', '.join(items)}")
        
        summary = "；".join(summary_parts)
        print(f"生成的记忆摘要: {summary}")
        return summary
    
    def clear_memory(self, user_id: str = "default"):
        """清除用户记忆"""
        if user_id in self.memories:
            del self.memories[user_id]
            self.save_memory()


# 单例模式
_memory_manager_instance = None

def get_memory_manager():
    """获取记忆管理器单例"""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance