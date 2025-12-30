# summary_manager.py
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from memory_manager import get_memory_manager


class SummaryManager:
    """总结性prompt管理器 - 用于生成和管理分类总结性prompt"""
    
    def __init__(self, summary_file: str = "summary_prompts.json"):
        self.summary_file = summary_file
        self.summaries: Dict[str, Dict[str, Any]] = {}
        self.memory_manager = get_memory_manager()
        self.load_summaries()
        
        # 分类定义（与memory_manager保持一致）
        self.categories = {
            "agreement": "用户同意的内容",
            "personal": "个人信息", 
            "preference": "用户偏好习惯",
            "task": "任务需求",
            "technical": "技术相关"
        }
        
    def load_summaries(self):
        """加载总结文件"""
        if os.path.exists(self.summary_file):
            try:
                with open(self.summary_file, 'r', encoding='utf-8') as f:
                    self.summaries = json.load(f)
                print(f"已加载总结文件: {self.summary_file}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载总结文件失败: {e}")
                self.summaries = {}
        else:
            print(f"总结文件不存在，将创建: {self.summary_file}")
            self.summaries = {}
            
    def save_summaries(self):
        """保存总结到文件"""
        try:
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                json.dump(self.summaries, f, ensure_ascii=False, indent=2)
            print(f"总结已保存到: {self.summary_file}")
        except IOError as e:
            print(f"保存总结文件失败: {e}")
            
    def generate_category_summary(self, category: str, memories: List[Dict[str, Any]]) -> str:
        """为特定分类生成总结性prompt"""
        if not memories:
            return ""
            
        # 获取该分类的所有记忆内容
        category_memories = [m for m in memories if m.get("category") == category]
        
        if not category_memories:
            return ""
            
        # 提取内容并去重
        contents = []
        seen = set()
        for memory in category_memories:
            content = memory.get("content", "").strip()
            if content and content not in seen:
                seen.add(content)
                contents.append(content)
                
        if not contents:
            return ""
            
        # 生成总结性prompt
        category_name = self.categories.get(category, category)
        
        # 如果内容较少，直接连接
        if len(contents) <= 3:
            summary = f"{category_name}：{'；'.join(contents)}"
        else:
            # 内容较多时，取最近的一些内容
            recent_contents = contents[-3:]  # 取最近3条
            summary = f"{category_name}（最近记录）：{'；'.join(recent_contents)}"
            
        return summary
        
    def update_summaries(self, user_id: str = "default"):
        """更新所有分类的总结性prompt"""
        memories = self.memory_manager.get_user_memories(user_id)
        
        if not memories:
            print("没有记忆数据，无法生成总结")
            return
            
        # 确保用户总结字典存在
        if user_id not in self.summaries:
            self.summaries[user_id] = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "summaries": {}
            }
            
        # 为每个分类生成总结
        updated = False
        for category in self.categories:
            summary = self.generate_category_summary(category, memories)
            
            if summary:
                self.summaries[user_id]["summaries"][category] = {
                    "content": summary,
                    "last_updated": datetime.now().isoformat(),
                    "category_name": self.categories[category],
                    "memory_count": len([m for m in memories if m.get("category") == category])
                }
                updated = True
                
        if updated:
            self.summaries[user_id]["last_updated"] = datetime.now().isoformat()
            self.save_summaries()
            print(f"已更新用户 {user_id} 的总结性prompt")
            
    def get_summary_prompt(self, user_id: str = "default") -> str:
        """获取总结性prompt字符串，用于注入到system prompt"""
        if user_id not in self.summaries:
            return ""
            
        summaries = self.summaries[user_id].get("summaries", {})
        if not summaries:
            return ""
            
        # 生成喵喵副脑格式的prompt
        summary_parts = []
        for category, data in summaries.items():
            content = data.get("content", "")
            if content:
                summary_parts.append(content)
                
        if not summary_parts:
            return ""
            
        full_summary = "；".join(summary_parts)
        
        # 生成喵喵副脑格式的标签
        return f"\n\n### 喵喵副脑：\n{full_summary}\n"
        
    def get_summary_for_category(self, user_id: str = "default", category: str = None) -> Optional[str]:
        """获取特定分类的总结"""
        if user_id not in self.summaries or not category:
            return None
            
        summaries = self.summaries[user_id].get("summaries", {})
        if category in summaries:
            return summaries[category].get("content", "")
        return None
        
    def clear_summaries(self, user_id: str = "default"):
        """清除用户的总结"""
        if user_id in self.summaries:
            del self.summaries[user_id]
            self.save_summaries()


# 单例模式
_summary_manager_instance = None

def get_summary_manager():
    """获取总结管理器单例"""
    global _summary_manager_instance
    if _summary_manager_instance is None:
        _summary_manager_instance = SummaryManager()
    return _summary_manager_instance