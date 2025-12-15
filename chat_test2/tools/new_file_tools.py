# tools/new_file_tools.py
from typing import Dict, Any
import json
import os
from pathlib import Path

from chat_test2.model_message import Tool


class CreateFileTool(Tool):
    """创建文件工具"""

    def __init__(self):
        super().__init__(
            name="create_file",
            description="创建新文件或覆盖现有文件",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要创建的文件路径"},
                    "content": {"type": "string", "description": "文件内容"},
                    "encoding": {"type": "string", "description": "文件编码（可选，默认utf-8）",
                                 "enum": ["utf-8", "gbk", "gb2312", "ascii"]}
                },
                "required": ["file_path"]
            }
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            file_path = arguments.get("file_path", "")
            content = arguments.get("content", "")
            encoding = arguments.get("encoding", "utf-8")

            # 安全检查
            safe_path = self._validate_path(file_path)

            # 创建目录（如果不存在）
            safe_path.parent.mkdir(parents=True, exist_ok=True)

            with open(safe_path, 'w', encoding=encoding) as f:
                f.write(content)

            return json.dumps({"status": "success", "file_path": str(safe_path), "size": len(content)})
        except Exception as e:
            return json.dumps({"error": f"创建文件失败: {str(e)}"})

    def _validate_path(self, file_path):
        """路径安全检查"""
        if ".." in file_path:
            raise ValueError("路径安全限制：不能包含'..'")
        safe_path = Path(file_path).resolve()
        current_dir = Path.cwd().resolve()
        if not str(safe_path).startswith(str(current_dir)):
            raise ValueError("路径安全限制：只能在当前工作目录内操作")
        return safe_path


class ModifyFileTool(Tool):
    """修改文件工具"""

    def __init__(self):
        super().__init__(
            name="modify_file",
            description="修改文件内容（覆盖写入）",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要修改的文件路径"},
                    "content": {"type": "string", "description": "新的文件内容"},
                    "encoding": {"type": "string", "description": "文件编码（可选，默认utf-8）",
                                 "enum": ["utf-8", "gbk", "gb2312", "ascii"]}
                },
                "required": ["file_path", "content"]
            }
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            file_path = arguments.get("file_path", "")
            content = arguments.get("content", "")
            encoding = arguments.get("encoding", "utf-8")
            # 安全检查
            safe_path = self._validate_path(file_path)
            # 检查文件是否存在
            if not safe_path.exists():
                return json.dumps({"error": f"文件不存在: {file_path}"})
            # 写入文件
            with open(safe_path, 'w', encoding=encoding) as f:
                f.write(content)
            return json.dumps({"status": "success", "file_path": str(safe_path), "size": len(content)})
        except Exception as e:
            return json.dumps({"error": f"修改文件失败: {str(e)}"})

    def _validate_path(self, file_path):
        """路径安全检查"""
        if ".." in file_path:
            raise ValueError("路径安全限制：不能包含'..'")
        safe_path = Path(file_path).resolve()
        current_dir = Path.cwd().resolve()
        if not str(safe_path).startswith(str(current_dir)):
            raise ValueError("路径安全限制：只能在当前工作目录内操作")
        return safe_path

class DeleteFileTool(Tool):
    """删除文件工具"""

    def __init__(self):
        super().__init__(
            name="delete_file",
            description="删除指定文件",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要删除的文件路径"}
                },
                "required": ["file_path"]
            }
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            file_path = arguments.get("file_path", "")
            # 安全检查
            safe_path = self._validate_path(file_path)
            # 检查文件是否存在
            if not safe_path.exists():
                return json.dumps({"error": f"文件不存在: {file_path}"})
            # 删除文件
            safe_path.unlink()
            return json.dumps({"status": "success", "file_path": str(safe_path)})
        except Exception as e:
            return json.dumps({"error": f"删除文件失败: {str(e)}"})

    def _validate_path(self, file_path):
        """路径安全检查"""
        if ".." in file_path:
            raise ValueError("路径安全限制：不能包含'..'")
        safe_path = Path(file_path).resolve()
        current_dir = Path.cwd().resolve()
        if not str(safe_path).startswith(str(current_dir)):
            raise ValueError("路径安全限制：只能在当前工作目录内操作")
        return safe_path


class InsertFileTool(Tool):
    """插入内容到文件工具"""

    def __init__(self):
        super().__init__(
            name="insert_file",
            description="在文件指定位置插入内容",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "要插入的内容"},
                    "position": {"type": "integer", "description": "插入位置（行号，可选，默认末尾）", "minimum": 0},
                    "encoding": {"type": "string", "description": "文件编码（可选，默认utf-8）",
                                 "enum": ["utf-8", "gbk", "gb2312", "ascii"]}
                },
                "required": ["file_path", "content"]
            }
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            file_path = arguments.get("file_path", "")
            content = arguments.get("content", "")
            position = arguments.get("position", -1)  # -1表示末尾
            encoding = arguments.get("encoding", "utf-8")
            # 安全检查
            safe_path = self._validate_path(file_path)
            # 检查文件是否存在
            if not safe_path.exists():
                return json.dumps({"error": f"文件不存在: {file_path}"})
            # 读取原文件内容
            with open(safe_path, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
            # 处理插入位置
            if position < 0 or position >= len(lines):
                # 插入到末尾
                lines.append(content + '\n')
            else:
                # 插入到指定位置
                lines.insert(position, content + '\n')
            # 写回文件
            with open(safe_path, 'w', encoding=encoding) as f:
                f.writelines(lines)
            return json.dumps({
                "status": "success",
                "file_path": str(safe_path),
                "inserted_at": position if position >= 0 else len(lines) - 1,
                "new_size": sum(len(line) for line in lines)
            })
        except Exception as e:
            return json.dumps({"error": f"插入内容失败: {str(e)}"})

    def _validate_path(self, file_path):
        """路径安全检查"""
        if ".." in file_path:
            raise ValueError("路径安全限制：不能包含'..'")
        safe_path = Path(file_path).resolve()
        current_dir = Path.cwd().resolve()
        if not str(safe_path).startswith(str(current_dir)):
            raise ValueError("路径安全限制：只能在当前工作目录内操作")
        return safe_path