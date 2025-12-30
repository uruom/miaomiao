# tools/file_tools.py
from typing import Dict, Any
import json
import os
from pathlib import Path

from chat_test2.model_message import Tool


class ReadFileTool(Tool):
    """读取文件工具"""

    def __init__(self):
        super().__init__(
            name="read_file",
            description="读取指定文件的内容",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要读取的文件路径"},
                    "max_lines": {"type": "integer", "description": "最大读取行数（可选，默认读取全部）", "minimum": 1, "maximum": 1000},
                    "encoding": {"type": "string", "description": "文件编码（可选，默认utf-8）", "enum": ["utf-8", "gbk", "gb2312", "ascii"]}
                },
                "required": ["file_path"]
            }
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            # 添加参数类型检查
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
                
            file_path = arguments.get("file_path", "")
            max_lines = arguments.get("max_lines", 0)  # 0表示读取全部
            encoding = arguments.get("encoding", "utf-8")

            # 安全检查
            safe_path = self._validate_path(file_path)

            # 检查文件是否存在
            if not safe_path.exists():
                return json.dumps({"error": f"文件不存在: {file_path}"})

            # 读取文件
            with open(safe_path, 'r', encoding=encoding, errors='ignore') as f:
                if max_lines > 0:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            break
                        lines.append(line)
                    content = ''.join(lines)
                else:
                    content = f.read()

            file_size = os.path.getsize(safe_path)
            lines_read = content.count('\n') + 1 if content else 0

            return json.dumps({
                "file_path": str(safe_path),
                "file_size": file_size,
                "lines_read": lines_read,
                "content": content
            })
        except Exception as e:
            return json.dumps({"error": f"读取文件失败: {str(e)}"})

    def _validate_path(self, file_path):
        """路径安全检查"""
        path_obj = Path(file_path)
        for part in path_obj.parts:
            if part == "..":
                raise ValueError("路径安全限制：不能包含'..'")
        safe_path = path_obj.resolve()
        current_dir = Path.cwd().resolve()
        try:
            safe_path.relative_to(current_dir)
        except ValueError:
            raise ValueError("路径安全限制：只能在当前工作目录内操作")
        return safe_path


class ListDirectoryTool(Tool):
    """列出目录工具"""

    def __init__(self):
        super().__init__(
            name="list_directory",
            description="列出指定目录下的文件和子目录",
            parameters={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "要浏览的目录路径（可选，默认为当前目录）"},
                    "show_hidden": {"type": "boolean", "description": "是否显示隐藏文件（可选，默认false）"},
                    "file_pattern": {"type": "string", "description": "文件匹配模式（可选，如*.py）"},
                    "max_items": {"type": "integer", "description": "最大显示项目数（可选，默认50）", "minimum": 1, "maximum": 200}
                },
                "required": []
            }
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            # 添加参数类型检查
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
                
            directory_path = arguments.get("directory_path", ".")
            show_hidden = arguments.get("show_hidden", False)
            file_pattern = arguments.get("file_pattern", "")
            max_items = arguments.get("max_items", 200)

            # 安全检查
            safe_path = self._validate_path(directory_path)

            # 检查路径是否存在
            if not safe_path.exists():
                return json.dumps({"error": f"目录不存在: {directory_path}"})

            # 检查是否是目录
            if not safe_path.is_dir():
                return json.dumps({"error": f"不是目录: {directory_path}"})

            # 列出文件和目录
            items = []
            count = 0
            
            for item in safe_path.iterdir():
                if count >= max_items:
                    break
                    
                # 过滤隐藏文件
                if not show_hidden and item.name.startswith('.'):
                    continue
                    
                # 过滤文件模式
                if file_pattern and not item.match(file_pattern):
                    continue
                    
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": item.stat().st_mtime
                }
                items.append(item_info)
                count += 1

            return json.dumps({
                "directory": str(safe_path),
                "total_items": len(items),
                "items": items
            })
        except Exception as e:
            return json.dumps({"error": f"列出目录失败: {str(e)}"})

    def _validate_path(self, directory_path):
        """路径安全检查"""
        path_obj = Path(directory_path)
        for part in path_obj.parts:
            if part == "..":
                raise ValueError("路径安全限制：不能包含'..'")
        safe_path = path_obj.resolve()
        current_dir = Path.cwd().resolve()
        try:
            safe_path.relative_to(current_dir)
        except ValueError:
            raise ValueError("路径安全限制：只能在当前工作目录内操作")
        return safe_path