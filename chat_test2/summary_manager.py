# summary_manager.py
import json
import os
import requests
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
        
        # API配置 - 与conversation_manager保持一致
        self.api_key = "sk-czprteaafqgpfewyrxwmhltdfdfaihpioejpfutupbcxyyao"
        self.model = "deepseek-ai/DeepSeek-V3.1"
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        
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
            
    def call_model_for_summary(self, category: str, memories: List[str]) -> Optional[str]:
        """调用模型生成总结"""
        if not memories:
            return None
            
        try:
            # 准备调用模型的prompt
            category_name = self.categories.get(category, category)
            memory_text = "\n".join([f"- {memory}" for memory in memories])
            
            # 构建总结请求的prompt
            prompt = f"""你是喵喵的副脑，负责对用户的记忆进行总结和归纳。

当前需要总结的类别是：{category_name}

以下是相关的记忆内容：
{memory_text}

请根据以上记忆内容，生成一段简洁、准确的总结性描述。总结应该：
1. 概括核心信息
2. 保持语言简洁
3. 突出重要内容
4. 使用自然的中文表达

请直接输出总结内容，不要添加额外的解释或格式。"""
            
            # 构建API请求 - 参照conversation_manager.py的真实调用方式
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,  # 使用较低的温度以获得更稳定的总结
                "max_tokens": 500
            }
            
            # 调用API
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=300000)
            response.raise_for_status()
            response_data = response.json()
            
            # 解析响应
            if response_data and "choices" in response_data and response_data["choices"]:
                choice = response_data["choices"][0]
                message = choice.get("message", {})
                summary = message.get("content", "").strip()
                
                if summary:
                    print(f"成功生成{category_name}总结")
                    return summary
                else:
                    print(f"模型返回的总结内容为空")
                    return None
            else:
                print(f"API响应格式异常: {response_data}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"调用模型生成总结失败（网络错误）: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"调用模型生成总结失败（JSON解析错误）: {e}")
            return None
        except Exception as e:
            print(f"调用模型生成总结失败: {e}")
            return None
            
    def generate_category_summary(self, category: str, memories: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """为特定分类生成总结性prompt"""
        if not memories:
            return None
            
        # 获取该分类的所有记忆内容
        category_memories = [m for m in memories if m.get("type") == category]
        
        if not category_memories:
            return None
            
        # 提取内容并去重
        contents = []
        seen = set()
        for memory in category_memories:
            content = memory.get("content", "").strip()
            if content and content not in seen:
                seen.add(content)
                contents.append(content)
                
        if not contents:
            return None
            
        # 调用模型生成总结
        summary_text = self.call_model_for_summary(category, contents)
        
        if not summary_text:
            # 如果模型调用失败，使用简单总结
            category_name = self.categories.get(category, category)
            if len(contents) <= 3:
                summary_text = f"{category_name}：{'；'.join(contents)}"
            else:
                summary_text = f"{category_name}（最近记录）：{'；'.join(contents[-3:])}"
                
        # 返回总结数据
        return {
            "summary": summary_text,
            "last_updated": datetime.now().isoformat(),
            "memory_count": len(category_memories)
        }
        
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
            summary_data = self.generate_category_summary(category, memories)
            
            if summary_data:
                if category not in self.summaries[user_id]["summaries"]:
                    self.summaries[user_id]["summaries"][category] = {}
                    
                self.summaries[user_id]["summaries"][category] = summary_data
                updated = True
                print(f"更新了 {category} 分类的总结")
                
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
            summary_text = data.get("summary", "")
            if summary_text:
                summary_parts.append(summary_text)
                
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
            return summaries[category].get("summary", "")
        return None
        
    def clear_summaries(self, user_id: str = "default"):
        """清除用户的总结"""
        if user_id in self.summaries:
            del self.summaries[user_id]
            self.save_summaries()
            print(f"已清除用户 {user_id} 的总结")