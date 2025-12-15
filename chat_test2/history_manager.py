import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from model_message import Message, AssistantMessage, ToolMessage, MessageType


class HistoryManager:
    """历史管理器（带持久化功能）"""

    def __init__(self, max_history: int = 10, storage_file: str = "conversation_history.json"):
        self.max_history = max_history
        self.storage_file = storage_file
        self.conversation_history: List[Message] = []
        self.system_prompt: Optional[Message] = None
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
        return [msg.to_dict() for msg in self.conversation_history]

    def clear_history(self, keep_system_prompt: bool = True):
        """清空历史记录"""
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
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "tool_messages": tool_count,
            "system_prompt": self.system_prompt.content if self.system_prompt else "无"
        }

    def get_recent_messages(self, count: int = 5) -> List[Message]:
        """获取最近的消息"""
        return self.conversation_history[-count:] if self.conversation_history else []

    def save_conversation(self):
        """保存对话到JSON文件"""
        try:
            # 只保存系统提示和对话历史
            data = {
                "system_prompt": self.system_prompt.to_dict() if self.system_prompt else None,
                "conversation_history": [msg.to_dict() for msg in self.conversation_history],
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"对话已保存到 {self.storage_file}")
        except Exception as e:
            print(f"保存对话记录失败: {e}")

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

            # 加载对话历史
            for msg_dict in data.get("conversation_history", []):
                if msg_dict["role"] == "system":
                    # 系统消息已在上面处理，跳过重复
                    continue
                elif msg_dict["role"] == "assistant":
                    msg = AssistantMessage.from_dict(msg_dict)
                    self.conversation_history.append(msg)
                elif msg_dict["role"] == "tool":
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
            # 如果加载失败，清空历史重新开始
            self.conversation_history = []
            self.system_prompt = None