# tools/basic_tools.py
from typing import Dict, Any
import json
import datetime

from chat_test2.model_message import Tool


class AdditionTool(Tool):
    """加法工具"""
    def __init__(self):
        super().__init__(
            name="addition",
            description="执行两个数字的加法运算",
            parameters={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数字"},
                    "b": {"type": "number", "description": "第二个数字"}
                },
                "required": ["a", "b"]
            }
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            a = arguments.get("a", 0)
            b = arguments.get("b", 0)
            result = a + b
            return json.dumps({"result": result, "operation": f"{a} + {b} = {result}"})
        except Exception as e:
            return json.dumps({"error": f"加法计算失败: {str(e)}"})

class DateQueryTool(Tool):
    """日期查询工具"""
    def __init__(self):
        super().__init__(
            name="get_current_date",
            description="获取当前日期和时间信息",
            parameters={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "日期格式，可选值：full(完整格式)、date_only(仅日期)、time_only(仅时间)",
                        "enum": ["full", "date_only", "time_only"]
                    }
                },
                "required": []
            }
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            format_type = arguments.get("format", "full")
            now = datetime.datetime.now()
            if format_type == "date_only":
                result = now.strftime("%Y-%m-%d")
            elif format_type == "time_only":
                result = now.strftime("%H:%M:%S")
            else:  # full
                result = now.strftime("%Y-%m-%d %H:%M:%S")
            return json.dumps({"current_time": result, "format": format_type})
        except Exception as e:
            return json.dumps({"error": f"日期查询失败: {str(e)}"})