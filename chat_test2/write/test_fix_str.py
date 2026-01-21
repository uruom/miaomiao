import json
from modules import FrameModule

# 创建一个模拟的固定帧响应数据，包含字符串类型的帧
mock_response = """这是一个测试响应，包含JSON数据：

[
    {"frame_id": "frame_1_1", "description": "有效帧1"},
    "这是一个字符串帧，应该被跳过",
    {"frame_id": "frame_1_2", "description": "有效帧2"},
    ["嵌套列表中的字符串", {"frame_id": "frame_1_3", "description": "有效帧3"}]
]"""

# 测试修复后的_parse_frames_response方法
frame_module = FrameModule()

# 模拟场景数据
mock_scene = {'scene_id': 'scene_1_1', 'scene_title': '测试场景'}

try:
    result = frame_module._parse_frames_response(mock_response, mock_scene)
    print('测试成功！解析结果：')
    print(f'成功解析了 {len(result)} 个有效帧')
    for i, frame in enumerate(result):
        print(f"帧 {i+1}: {frame.get('frame_id', '未知')} - {frame.get('description', '无描述')}")
except Exception as e:
    print(f'测试失败，错误：{e}')
    print(f'错误类型：{type(e).__name__}')