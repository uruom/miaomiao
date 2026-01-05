"""小说自动写作项目
包含四个核心模块：
1. 主体拆解为大纲
2. 大纲拆解为细纲
3. 细纲拆解为固定帧
4. 固定帧扩写为文章
"""

from .core import StoryEngine
from .modules import OutlineModule, DetailOutlineModule, FrameModule, WritingModule
from .utils import FileManager, ModelManager, JsonStorage

__all__ = [
    'StoryEngine',
    'OutlineModule', 
    'DetailOutlineModule',
    'FrameModule',
    'WritingModule',
    'FileManager',
    'ModelManager',
    'JsonStorage'
]

__version__ = '0.1.0'