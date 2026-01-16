"""核心引擎 - 协调所有模块工作"""

import json
import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class StoryConfig:
    """故事配置"""
    title: str = ""
    genre: str = ""
    style: str = ""
    word_count: int = 0
    characters: list = field(default_factory=list)
    settings: dict = field(default_factory=dict)


@dataclass
class PipelineState:
    """流水线状态"""
    project_name: str = ""
    current_stage: str = "init"  # init, outline, detail, frame, writing, complete
    start_time: float = 0.0
    last_update: float = 0.0
    completed_chapters: List[str] = field(default_factory=list)  # 已完成的章节ID
    completed_scenes: List[str] = field(default_factory=list)    # 已完成的场景ID
    completed_frames: List[str] = field(default_factory=list)    # 已完成的帧ID
    current_chapter: str = ""     # 当前处理的章节
    current_scene: str = ""       # 当前处理的场景
    current_frame: str = ""       # 当前处理的帧
    error_count: Dict[str, int] = field(default_factory=dict)    # 各阶段错误计数
    retry_attempts: Dict[str, int] = field(default_factory=dict) # 重试次数记录


class StoryEngine:
    """故事引擎 - 主控制器"""
    
    def __init__(self, project_path: str = "write_project"):
        self.project_path = project_path
        self.config = StoryConfig()
        self.state = PipelineState()
        
        # 创建项目目录
        self._create_project_structure()
        
        # 加载已有状态
        self._load_state()
        
        # 初始化模块（后续完善）
        self.modules = {}
        
        logger.info(f"故事引擎初始化完成，项目路径: {project_path}")
        logger.info(f"当前状态: {self.state.current_stage}")
    
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
            "cache",
            "state"
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
    
    def _load_state(self):
        """加载保存的状态"""
        state_file = os.path.join(self.project_path, "state", "pipeline_state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                # 更新状态
                for key, value in state_data.items():
                    if hasattr(self.state, key):
                        setattr(self.state, key, value)
                
                logger.info(f"已加载保存的状态: {self.state.current_stage}")
                logger.info(f"已完成章节: {len(self.state.completed_chapters)}")
                logger.info(f"已完成场景: {len(self.state.completed_scenes)}")
                logger.info(f"已完成帧: {len(self.state.completed_frames)}")
                
            except Exception as e:
                logger.error(f"加载状态失败: {e}")
                # 创建新的状态文件
                self._save_state()
        else:
            # 初始化状态
            self.state.start_time = time.time()
            self.state.last_update = time.time()
            self.state.project_name = os.path.basename(self.project_path)
            self._save_state()
    
    def _save_state(self):
        """保存当前状态"""
        try:
            state_file = os.path.join(self.project_path, "state", "pipeline_state.json")
            self.state.last_update = time.time()
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.state), f, indent=2, ensure_ascii=False)
            
            logger.debug(f"状态已保存: {state_file}")
        except Exception as e:
            logger.error(f"保存状态失败: {e}")
    
    def update_stage(self, stage: str):
        """更新当前阶段"""
        self.state.current_stage = stage
        self._save_state()
        logger.info(f"阶段更新: {stage}")
    
    def mark_chapter_completed(self, chapter_id: str):
        """标记章节完成"""
        if chapter_id not in self.state.completed_chapters:
            self.state.completed_chapters.append(chapter_id)
            self._save_state()
            logger.info(f"章节完成: {chapter_id}")
    
    def mark_scene_completed(self, scene_id: str):
        """标记场景完成"""
        if scene_id not in self.state.completed_scenes:
            self.state.completed_scenes.append(scene_id)
            self._save_state()
            logger.info(f"场景完成: {scene_id}")
    
    def mark_frame_completed(self, frame_id: str):
        """标记帧完成"""
        if frame_id not in self.state.completed_frames:
            self.state.completed_frames.append(frame_id)
            self._save_state()
            logger.info(f"帧完成: {frame_id}")
    
    def set_current_context(self, chapter_id: str = "", scene_id: str = "", frame_id: str = ""):
        """设置当前处理上下文"""
        if chapter_id:
            self.state.current_chapter = chapter_id
        if scene_id:
            self.state.current_scene = scene_id
        if frame_id:
            self.state.current_frame = frame_id
        self._save_state()
    
    def record_error(self, stage: str):
        """记录错误"""
        if stage not in self.state.error_count:
            self.state.error_count[stage] = 0
        self.state.error_count[stage] += 1
        self._save_state()
    
    def record_retry(self, operation: str):
        """记录重试"""
        if operation not in self.state.retry_attempts:
            self.state.retry_attempts[operation] = 0
        self.state.retry_attempts[operation] += 1
        self._save_state()
    
    def get_retry_count(self, operation: str) -> int:
        """获取重试次数"""
        return self.state.retry_attempts.get(operation, 0)
    
    def clear_retry_count(self, operation: str):
        """清除重试计数"""
        if operation in self.state.retry_attempts:
            self.state.retry_attempts[operation] = 0
            self._save_state()
    
    def is_chapter_completed(self, chapter_id: str) -> bool:
        """检查章节是否已完成"""
        return chapter_id in self.state.completed_chapters
    
    def is_scene_completed(self, scene_id: str) -> bool:
        """检查场景是否已完成"""
        return scene_id in self.state.completed_scenes
    
    def is_frame_completed(self, frame_id: str) -> bool:
        """检查帧是否已完成"""
        return frame_id in self.state.completed_frames
    
    def get_remaining_chapters(self, all_chapters: List[str]) -> List[str]:
        """获取未完成的章节"""
        return [ch for ch in all_chapters if not self.is_chapter_completed(ch)]
    
    def get_remaining_scenes(self, all_scenes: List[str]) -> List[str]:
        """获取未完成的场景"""
        return [sc for sc in all_scenes if not self.is_scene_completed(sc)]
    
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
        elapsed = time.time() - self.state.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        
        return {
            "project_path": self.project_path,
            "current_stage": self.state.current_stage,
            "config": asdict(self.config),
            "directory_exists": os.path.exists(self.project_path),
            "elapsed_time": f"{hours}h {minutes}m",
            "completed_chapters": len(self.state.completed_chapters),
            "completed_scenes": len(self.state.completed_scenes),
            "completed_frames": len(self.state.completed_frames),
            "current_context": {
                "chapter": self.state.current_chapter,
                "scene": self.state.current_scene,
                "frame": self.state.current_frame
            },
            "error_counts": self.state.error_count,
            "retry_counts": self.state.retry_attempts
        }
    
    def start_processing(self):
        """开始处理流程"""
        self.update_stage("outline")
        self._log_progress("开始故事生成流程")
    
    def _log_progress(self, message: str):
        """记录进度日志"""
        log_file = os.path.join(self.project_path, "logs", "progress.log")
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        logger.info(f"进度: {message}")
    
    def reset_pipeline(self, stage: str = "init"):
        """重置流水线到指定阶段"""
        self.state = PipelineState()
        self.state.start_time = time.time()
        self.state.last_update = time.time()
        self.state.project_name = os.path.basename(self.project_path)
        self.state.current_stage = stage
        self._save_state()
        logger.info(f"流水线已重置到阶段: {stage}")
    
    def resume_from_stage(self, stage: str):
        """从指定阶段恢复"""
        self.state.current_stage = stage
        self._save_state()
        logger.info(f"从阶段恢复: {stage}")


def test_engine():
    """测试引擎功能"""
    engine = StoryEngine("test_project")
    engine.set_config(
        title="测试故事",
        genre="奇幻",
        word_count=5000
    )
    
    # 测试状态管理
    engine.update_stage("outline")
    engine.mark_chapter_completed("ch_1")
    engine.mark_scene_completed("scene_1")
    engine.mark_frame_completed("frame_1")
    
    engine.set_current_context(chapter_id="ch_2", scene_id="scene_2")
    
    # 记录错误和重试
    engine.record_error("outline")
    engine.record_retry("model_call")
    
    status = engine.get_status()
    print("引擎状态:", json.dumps(status, indent=2, ensure_ascii=False))
    
    # 测试检查功能
    print(f"章节ch_1完成: {engine.is_chapter_completed('ch_1')}")
    print(f"章节ch_2完成: {engine.is_chapter_completed('ch_2')}")
    
    return engine


if __name__ == "__main__":
    test_engine()