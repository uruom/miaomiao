# conversation_manager.py
from typing import Dict, Any, List, Optional
import requests
import json
from model_message import Message, AssistantMessage, ToolCall
from history_manager import HistoryManager
from tool_manager import ToolManager


class ConversationManager:
    """对话管理器"""

    def __init__(self, api_key: str, history_manager: HistoryManager,
                 tool_manager: ToolManager, model: str = "deepseek-ai/DeepSeek-V3.1"):
        self.api_key = api_key
        self.model = model
        self.history_manager = history_manager
        self.tool_manager = tool_manager
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"

    def call_api(self, use_tools: bool = True) -> Optional[Dict[str, Any]]:
        """调用API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": self.history_manager.get_context_messages(),
            "temperature": 0.7,
            "max_tokens": 12000
        }

        # 如果有工具且启用工具调用，添加工具参数
        if use_tools and self.tool_manager.has_tools():
            payload["tools"] = self.tool_manager.get_available_tools()
            payload["tool_choice"] = "auto"

        print(f"API请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=300000)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求出错: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"响应解析出错: {e}")
            return None

    def parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析API响应"""
        if not response_data:
            return {"error": "API响应为空"}

        try:
            choice = response_data["choices"][0]
            message = choice["message"]
            finish_reason = choice.get("finish_reason", "unknown")

            result = {
                "content": message.get("content", ""),
                "finish_reason": finish_reason,
                "tool_calls": [],
                "usage": response_data.get("usage", {})
            }

            # 解析工具调用
            if "tool_calls" in message and message["tool_calls"]:
                tool_calls = []
                for tc_data in message["tool_calls"]:
                    tool_call = ToolCall(
                        id=tc_data["id"],
                        name=tc_data["function"]["name"],
                        arguments=json.loads(tc_data["function"]["arguments"])
                    )
                    tool_calls.append(tool_call)
                result["tool_calls"] = tool_calls

            print(f"result:{result}")
            return result

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            error_msg = f"响应解析失败: {e}"
            print(f"{error_msg}\n原始响应: {response_data}")
            return {"error": error_msg}

    def process_tool_calls(self, tool_calls: List[ToolCall]) -> bool:
        """处理工具调用"""
        if not tool_calls:
            return True

        all_success = True
        for tool_call in tool_calls:
            print(f"执行工具调用: {tool_call.name}")
            tool_message = self.tool_manager.execute_tool(tool_call)
            self.history_manager.add_tool_message(tool_message.content, tool_call.id)

            # 检查工具执行是否成功
            try:
                result_data = json.loads(tool_message.content)
                if "error" in result_data:
                    print(f"工具执行失败: {result_data['error']}")
                    all_success = False
                else:
                    print(f"工具执行成功: {result_data}")
            except:
                print("工具执行结果解析失败")
                all_success = False

        return all_success

    def chat(self, user_input: str, use_tools: bool = True) -> Optional[str]:
        """处理用户输入并获取回复"""
        # 添加用户消息到历史
        self.history_manager.add_user_message(user_input)

        max_iterations = 50  # 防止无限循环
        final_reply = None

        for iteration in range(max_iterations):
            print(f"\n--- 第{iteration + 1}轮处理 ---")

            # 调用API
            response_data = self.call_api(use_tools=use_tools)
            if not response_data:
                return "抱歉，API调用失败"

            # 解析响应
            result = self.parse_response(response_data)
            if "error" in result:
                return f"处理响应时出错: {result['error']}"

            # 添加助手回复到历史
            assistant_message = AssistantMessage(
                role="assistant",
                content=result["content"],
                tool_calls=result["tool_calls"]
            )
            self.history_manager.add_message(assistant_message)

            # 如果有工具调用，处理它们
            if result["tool_calls"]:
                success = self.process_tool_calls(result["tool_calls"])
                # if not success:
                #     return "工具执行失败"

                # 如果有工具调用，继续下一轮处理
                continue
            else:
                # 没有工具调用，返回最终回复
                final_reply = result["content"]
                break

        return final_reply
