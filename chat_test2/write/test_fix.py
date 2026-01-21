import json
from modules import FrameModule

# 创建一个模拟的固定帧响应数据，包含可能的列表格式
mock_response = """这是一个测试响应，包含JSON数据：

[{"frame_id": "frame_1_1", "description": "测试帧描述", "characters": ["角色1", "角色2"], "dialogue": "测试对话内容", "actions": ["动作1", "动作2"]}]"""

# 测试修复后的_parse_frames_response方法
frame_module = FrameModule()

# 模拟场景数据
mock_scene = {'scene_id': 'scene_1_1', 'scene_title': '测试场景'}

try:
    result = frame_module._parse_frames_response(mock_response, mock_scene)
    print('测试成功！解析结果：')
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(f'测试失败，错误：{e}')
    print(f'错误类型：{type(e).__name__}')