# tool_manager.py
from typing import Dict, Any, List
from model_message import Tool, ToolCall, ToolMessage
import json
from tools import (
    AdditionTool, DateQueryTool, ReadFileTool, ListDirectoryTool,
    CreateFileTool, ModifyFileTool, DeleteFileTool, InsertFileTool
)

class ToolManager:
    """工具管理器"""
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """注册默认工具"""
        self.register_tool(AdditionTool())
        self.register_tool(DateQueryTool())
        self.register_tool(ReadFileTool())
        self.register_tool(ListDirectoryTool())
        self.register_tool(CreateFileTool())
        self.register_tool(ModifyFileTool())
        self.register_tool(DeleteFileTool())
        self.register_tool(InsertFileTool())

    def register_tool(self, tool: Tool):
        """注册新工具"""
        self.tools[tool.name] = tool
        print(f"工具注册成功: {tool.name}")

    def unregister_tool(self, tool_name: str):
        """注销工具"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            print(f"工具注销成功: {tool_name}")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return [tool.to_dict() for tool in self.tools.values()]

    def execute_tool(self, tool_call: ToolCall) -> ToolMessage:
        """执行工具调用"""
        tool_name = tool_call.name
        if tool_name not in self.tools:
            error_msg = json.dumps({"error": f"工具不存在: {tool_name}"})
            return ToolMessage(role="tool", content=error_msg, tool_call_id=tool_call.id)

        try:
            tool = self.tools[tool_name]
            result = tool.execute(tool_call.arguments)
            return ToolMessage(role="tool", content=result, tool_call_id=tool_call.id)
        except Exception as e:
            error_msg = json.dumps({"error": f"工具执行失败: {str(e)}"})
            return ToolMessage(role="tool", content=error_msg, tool_call_id=tool_call.id)

    def has_tools(self) -> bool:
        """检查是否有可用工具"""
        return len(self.tools) > 0