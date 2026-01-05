"""核心引擎 - 协调所有模块工作"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class StoryConfig:
    """故事配置"""
    title: str = ""
    genre: str = ""
    style: str = ""
    word_count: int = 0
    characters: list = None
    settings: dict = None
    
    def __post_init__(self):
        if self.characters is None:
            self.characters = []
        if self.settings is None:
            self.settings = {}


class StoryEngine:
    """故事引擎 - 主控制器"""
    
    def __init__(self, project_path: str = "write_project"):
        self.project_path = project_path
        self.config = StoryConfig()
        
        # 创建项目目录
        self._create_project_structure()
        
        # 初始化模块（后续完善）
        self.modules = {}
        self.current_stage = "init"
        
    def _create_project_structure(self):
        """创建项目目录结构"""
        directories = [
            "data",
            "data/characters",
            "data/items", 
            "data/locations",
            "data/environments",
            "output",
            "output/outlines",
            "output/details",
            "output/frames",
            "output/chapters",
            "logs",
            "cache"
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(self.project_path, directory), exist_ok=True)
            
        # 创建配置文件
        config_file = os.path.join(self.project_path, "project_config.json")
        if not os.path.exists(config_file):
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "project_name": "Auto Story",
                    "created_at": datetime.now().isoformat(),
                    "version": "0.1.0",
                    "stages_completed": []
                }, f, indent=2, ensure_ascii=False)
    
    def set_config(self, **kwargs):
        """设置故事配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # 保存配置
        config_file = os.path.join(self.project_path, "story_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
    
    def load_config(self, config_file: str = "story_config.json"):
        """加载故事配置"""
        file_path = os.path.join(self.project_path, config_file)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                self.config = StoryConfig(**config_data)
    
    def get_status(self) -> Dict[str, Any]:
        """获取项目状态"""
        return {
            "project_path": self.project_path,
            "current_stage": self.current_stage,
            "config": asdict(self.config),
            "directory_exists": os.path.exists(self.project_path)
        }
    
    def start_processing(self):
        """开始处理流程"""
        self.current_stage = "outline"
        self._log_progress("开始故事生成流程")
    
    def _log_progress(self, message: str):
        """记录进度日志"""
        log_file = os.path.join(self.project_path, "logs", "progress.log")
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"进度: {message}")


def test_engine():
    """测试引擎功能"""
    engine = StoryEngine("test_project")
    engine.set_config(
        title="测试故事",
        genre="奇幻",
        word_count=5000
    )
    
    status = engine.get_status()
    print("引擎状态:", status)
    return engine


if __name__ == "__main__":
    test_engine()