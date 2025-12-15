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
        return cls(
            id=data["id"],
            name=data["function"]["name"] if "function" in data else data.get("name", ""),
            arguments=json.loads(data["function"]["arguments"]) if "function" in data else data.get("arguments", {})
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
            # 需要实现 ToolCall 的 from_dict 方法或直接解析
            tool_calls = []
            for tc_data in data["tool_calls"]:
                # 简单实现，根据你的数据结构调整
                tool_calls.append(ToolCall(
                    id=tc_data["id"],
                    name=tc_data["function"]["name"] if "function" in tc_data else tc_data.get("name", ""),
                    arguments=tc_data["function"]["arguments"] if "function" in tc_data else tc_data.get("arguments",
                                                                                                         {})
                ))
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
