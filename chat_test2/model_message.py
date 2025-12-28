# base_classes.py
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import time
import json


class MessageType(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """消息基类"""
    role: str
    content: str
    timestamp: float = None
    message_id: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.message_id is None:
            self.message_id = f"msg_{int(self.timestamp * 1000)}"

    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(
            role=data["role"],
            content=data["content"]
        )


@dataclass
class ToolCall:
    """工具调用类"""
    id: str
    name: str
    arguments: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": "function",
            "function": {
                "name": self.name,
                "arguments": json.dumps(self.arguments, ensure_ascii=False)
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolCall':
        try:
            if "function" in data:
                arguments_str = data["function"]["arguments"]
                # 如果arguments已经是字典，直接使用
                if isinstance(arguments_str, dict):
                    arguments = arguments_str
                else:
                    # 如果是字符串，尝试解析
                    arguments = json.loads(arguments_str) if arguments_str else {}
                return cls(
                    id=data["id"],
                    name=data["function"]["name"],
                    arguments=arguments
                )
            else:
                # 兼容旧格式
                return cls(
                    id=data["id"],
                    name=data.get("name", ""),
                    arguments=data.get("arguments", {})
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"ToolCall反序列化错误: {e}, data: {data}")
            return cls(
                id=data.get("id", "unknown"),
                name=data.get("name", "unknown"),
                arguments={}
            )

@dataclass
class ToolMessage(Message):
    """工具消息类"""
    tool_call_id: str = None

    def to_dict(self) -> Dict[str, Any]:
        return {"role": "tool", "content": self.content, "tool_call_id": self.tool_call_id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolMessage':
        return cls(
            role=data["role"],
            content=data["content"],
            tool_call_id=data.get("tool_call_id")
        )


@dataclass
class AssistantMessage(Message):
    """助手消息类（支持工具调用）"""
    tool_calls: List[ToolCall] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"role": "assistant", "content": self.content}
        if self.tool_calls:
            result["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssistantMessage':
        tool_calls = None
        if "tool_calls" in data:
            tool_calls = []
            for tc_data in data["tool_calls"]:
                tool_calls.append(ToolCall.from_dict(tc_data))
        return cls(
            role=data["role"],
            content=data["content"],
            tool_calls=tool_calls
        )

@dataclass
class Tool:
    """工具基类"""
    name: str
    description: str
    parameters: Dict[str, Any]

    def execute(self, arguments: Dict[str, Any]) -> str:
        raise NotImplementedError("子类必须实现execute方法")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
