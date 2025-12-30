import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from model_message import Message, AssistantMessage, ToolMessage, MessageType
from memory_manager import get_memory_manager
from summary_manager import get_summary_manager


class HistoryManager:
    """历史管理器（带持久化功能）"""

    def __init__(self, max_history: int = 10, storage_file: str = "conversation_history.json"):
        self.max_history = max_history
        self.storage_file = storage_file
        self.conversation_history: List[Message] = []
        self.system_prompt: Optional[Message] = None
        self.memory_manager = get_memory_manager()
        self.summary_manager = get_summary_manager()
        self.load_conversation()

    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self.system_prompt = Message(role="system", content=prompt)
        # 如果系统消息已存在，更新它；否则添加到历史开头
        if self.conversation_history and self.conversation_history[0].role == "system":
            self.conversation_history[0] = self.system_prompt
        else:
            self.conversation_history.insert(0, self.system_prompt)
        self.save_conversation()

    def add_message(self, message: Message):
        """添加消息到历史"""
        # 防止重复添加系统消息
        if message.role == "system":
            if self.conversation_history and self.conversation_history[0].role == "system":
                self.conversation_history[0] = message
                self.system_prompt = message
            else:
                self.conversation_history.insert(0, message)
                self.system_prompt = message
        else:
            self.conversation_history.append(message)
            
            # 自动记录用户消息到记忆
            if message.role == "user":
                self.memory_manager.add_memory("default", message.content, "user")
                
                # 用户消息添加后，更新总结性prompt
                self.summary_manager.update_summaries("default")

        self._trim_history()
        self.save_conversation()

    def add_user_message(self, content: str):
        """添加用户消息"""
        message = Message(role="user", content=content)
        self.add_message(message)

    def add_assistant_message(self, content: str, tool_calls=None):
        """添加助手消息"""
        message = AssistantMessage(role="assistant", content=content, tool_calls=tool_calls)
        self.add_message(message)

    def add_tool_message(self, content: str, tool_call_id: str):
        """添加工具消息"""
        message = ToolMessage(role="tool", content=content, tool_call_id=tool_call_id)
        self.add_message(message)

    def _trim_history(self):
        """修剪历史记录，保留系统消息和最近的对话"""
        if len(self.conversation_history) <= self.max_history + 1:  # +1 为系统消息
            return
        # 保留系统消息和最近的历史记录
        system_msg = None
        if self.conversation_history and self.conversation_history[0].role == "system":
            system_msg = self.conversation_history[0]
            recent_messages = self.conversation_history[-(self.max_history):]
            self.conversation_history = [system_msg] + recent_messages
        else:
            self.conversation_history = self.conversation_history[-(self.max_history):]

    def get_context_messages(self) -> List[Dict[str, Any]]:
        """获取API调用所需的上下文消息"""
        # 获取总结性prompt
        summary_prompt = self.summary_manager.get_summary_prompt("default")
        
        # 如果有总结性prompt，添加到系统提示中
        if summary_prompt and self.system_prompt:
            # 检查是否已包含喵喵副脑
            if "喵喵副脑" not in self.system_prompt.content:
                enhanced_prompt = self.system_prompt.content + summary_prompt
                return [{"role": "system", "content": enhanced_prompt}] + [msg.to_dict() for msg in self.conversation_history[1:]]
            else:
                # 如果已包含，需要更新它
                # 这里我们可以简单地在每次对话前重新构建system prompt
                base_prompt = self.system_prompt.content
                # 移除旧的喵喵副脑部分（如果存在）
                if "### 喵喵副脑：" in base_prompt:
                    base_prompt = base_prompt.split("### 喵喵副脑：")[0].strip()
                
                enhanced_prompt = base_prompt + summary_prompt
                return [{"role": "system", "content": enhanced_prompt}] + [msg.to_dict() for msg in self.conversation_history[1:]]
        
        return [msg.to_dict() for msg in self.conversation_history]

    def clear_history(self, keep_system_prompt: bool = True):
        """清除历史记录"""
        if keep_system_prompt and self.system_prompt:
            self.conversation_history = [self.system_prompt]
        else:
            self.conversation_history = []
            self.system_prompt = None
        self.save_conversation()

    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        user_count = len([msg for msg in self.conversation_history if msg.role == "user"])
        assistant_count = len([msg for msg in self.conversation_history if msg.role == "assistant"])
        tool_count = len([msg for msg in self.conversation_history if msg.role == "tool"])
        
        # 获取记忆统计
        memories = self.memory_manager.get_user_memories("default")
        
        # 获取总结统计
        summaries = {}
        if "default" in self.summary_manager.summaries:
            summaries = self.summary_manager.summaries["default"].get("summaries", {})
        
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "tool_messages": tool_count,
            "memory_count": len(memories),
            "memory_categories": list(set([m["category"] for m in memories])),
            "summary_count": len(summaries),
            "summary_categories": list(summaries.keys()),
            "system_prompt": self.system_prompt.content if self.system_prompt else "无"
        }

    def get_recent_messages(self, count: int = 5) -> List[Message]:
        """获取最近的消息"""
        return self.conversation_history[-count:] if self.conversation_history else []

    def save_conversation(self):
        """保存对话到JSON文件"""
        try:
            # 只保存系统提示和对话历史，不重复保存system消息
            # 过滤掉conversation_history中的system消息，改用独立的system_prompt字段
            filtered_history = [msg for msg in self.conversation_history if msg.role != "system"]
            
            data = {
                "system_prompt": self.system_prompt.to_dict() if self.system_prompt else None,
                "conversation_history": [msg.to_dict() for msg in filtered_history],
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"对话已保存到 {self.storage_file}")
        except Exception as e:
            print(f"保存对话记录失败: {e}")

    def _fix_nested_json_content(self, content):
        """修复嵌套的JSON内容"""
        if isinstance(content, str):
            try:
                # 尝试解析一次
                parsed = json.loads(content)
                if isinstance(parsed, str):
                    # 如果解析后还是字符串，说明有双重转义
                    return self._fix_nested_json_content(parsed)
                else:
                    # 如果是其他类型，重新序列化为JSON字符串
                    return json.dumps(parsed, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                # 如果不是JSON，直接返回
                return content
        else:
            # 如果不是字符串，直接序列化
            return json.dumps(content, ensure_ascii=False)

    def load_conversation(self):
        """从JSON文件加载对话"""
        if not os.path.exists(self.storage_file):
            print("未找到历史记录文件，创建新的对话")
            return
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.conversation_history = []

            # 加载系统提示
            if data.get("system_prompt"):
                self.system_prompt = Message.from_dict(data["system_prompt"])
                self.conversation_history.append(self.system_prompt)

            # 加载对话历史（不包含system消息，因为已经处理过了）
            for msg_dict in data.get("conversation_history", []):
                if msg_dict["role"] == "system":
                    # 系统消息已在上面的处理，跳过重复
                    continue
                elif msg_dict["role"] == "assistant":
                    # 修复助手消息中的工具调用参数
                    if "tool_calls" in msg_dict and msg_dict["tool_calls"]:
                        for tool_call in msg_dict["tool_calls"]:
                            if "function" in tool_call:
                                # 确保arguments是字符串
                                if "arguments" in tool_call["function"]:
                                    args = tool_call["function"]["arguments"]
                                    if isinstance(args, dict):
                                        tool_call["function"]["arguments"] = json.dumps(args, ensure_ascii=False)
                    msg = AssistantMessage.from_dict(msg_dict)
                    self.conversation_history.append(msg)
                elif msg_dict["role"] == "tool":
                    # 修复工具消息中的嵌套JSON
                    if "content" in msg_dict:
                        msg_dict["content"] = self._fix_nested_json_content(msg_dict["content"])
                    msg = ToolMessage.from_dict(msg_dict)
                    self.conversation_history.append(msg)
                else:
                    msg = Message.from_dict(msg_dict)
                    self.conversation_history.append(msg)

            # 应用历史限制
            self._trim_history()
            print(f"已从 {self.storage_file} 加载 {len(self.conversation_history)} 条历史消息")
        except Exception as e:
            print(f"加载对话记录失败: {e}")
            # 如果加载失败，清除历史重新开始
            self.conversation_history = []
            self.system_prompt = None