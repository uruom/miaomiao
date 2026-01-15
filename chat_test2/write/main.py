"""主程序入口 - 小说自动写作系统"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import StoryEngine
from modules import (
    OutlineModule, 
    DetailOutlineModule, 
    FrameModule, 
    WritingModule
)
from utils import FileManager, JsonStorage


class AutoStoryWriter:
    """自动故事写作系统"""
    
    def __init__(self, project_name: str = "my_story"):
        self.project_name = project_name
        self.project_path = os.path.join("write_projects", project_name)
        
        # 初始化引擎和模块
        self.engine = StoryEngine(self.project_path)
        self.modules = {
            "outline": OutlineModule(self.project_path),
            "detail": DetailOutlineModule(self.project_path),
            "frame": FrameModule(self.project_path),
            "writing": WritingModule(self.project_path)
        }
        
        self.file_manager = FileManager()
        self.storage = JsonStorage(os.path.join(self.project_path, "data"))
        
        print(f"故事写作系统初始化完成")
        print(f"项目路径: {self.project_path}")
    
    def setup_project(self, config: Dict[str, Any]):
        """设置项目配置"""
        print("设置项目配置...")
        self.engine.set_config(**config)
        
        # 保存项目信息
        project_info = {
            "project_name": self.project_name,
            "config": config,
            "created_at": self.get_current_time(),
            "status": "setup_complete"
        }
        
        info_file = os.path.join(self.project_path, "project_info.json")
        self.file_manager.write_json(info_file, project_info)
        
        print("项目设置完成")
    
    def generate_outline(self, story_concept: str, **kwargs) -> Dict[str, Any]:
        """生成故事大纲"""
        print(f"生成故事大纲: {story_concept[:50]}...")
        
        # 记录开始时间
        self._log_step("outline_generation_start", {"concept": story_concept})
        
        # 调用大纲模块
        outline = self.modules["outline"].generate_outline(story_concept, **kwargs)
        
        # 保存到项目配置
        if outline:
            self.engine.set_config(title=outline.get("title", "未命名故事"))
            
            # 记录完成时间
            self._log_step("outline_generation_complete", {
                "outline_title": outline.get("title"),
                "parts_count": len(outline.get("parts", []))
            })
        
        return outline
    
    def generate_details(self, outline_data: Dict[str, Any], chapter_ids: Optional[list] = None) -> Dict[str, Any]:
        """生成详细细纲"""
        print("生成详细细纲...")
        
        if not outline_data or "parts" not in outline_data:
            print("无效的大纲数据")
            return {}
        
        all_details = {}
        
        # 确定要处理的章节
        chapters_to_process = []
        if chapter_ids:
            # 处理指定章节
            for part in outline_data["parts"]:
                for chapter in part["chapters"]:
                    if chapter["id"] in chapter_ids:
                        chapters_to_process.append(chapter)
        else:
            # 处理所有章节
            for part in outline_data["parts"]:
                chapters_to_process.extend(part["chapters"])
        
        # 生成每个章节的细纲
        for i, chapter in enumerate(chapters_to_process):
            print(f"处理章节 {i+1}/{len(chapters_to_process)}: {chapter.get('title', '未命名')}")
            
            self._log_step("detail_generation_start", {
                "chapter_id": chapter["id"],
                "chapter_title": chapter.get("title")
            })
            
            detail = self.modules["detail"].generate_details(outline_data, chapter["id"])
            
            if detail:
                all_details[chapter["id"]] = detail
                
                self._log_step("detail_generation_complete", {
                    "chapter_id": chapter["id"],
                    "scenes_count": len(detail.get("scenes", []))
                })
        
        # 保存所有细纲
        if all_details:
            details_file = os.path.join(self.project_path, "output", "all_details.json")
            self.file_manager.write_json(details_file, all_details)
            print(f"所有细纲已保存到: {details_file}")
        
        return all_details
    
    def generate_frames(self, details_data: Dict[str, Any], scene_ids: Optional[list] = None) -> Dict[str, Any]:
        """生成固定帧"""
        print("生成固定帧...")
        
        all_frames = {}
        total_scenes = 0
        
        # 遍历所有章节的细纲
        for chapter_id, detail in details_data.items():
            scenes = detail.get("scenes", [])
            
            # 确定要处理的场景
            scenes_to_process = []
            if scene_ids:
                for scene in scenes:
                    if scene.get("scene_id") in scene_ids:
                        scenes_to_process.append(scene)
            else:
                scenes_to_process = scenes
            
            # 生成每个场景的固定帧
            chapter_frames = []
            for i, scene in enumerate(scenes_to_process):
                print(f"处理场景 {i+1}/{len(scenes_to_process)}: {scene.get('scene_title', '未命名')}")
                
                self._log_step("frame_generation_start", {
                    "scene_id": scene.get("scene_id"),
                    "scene_title": scene.get("scene_title")
                })
                
                frames = self.modules["frame"].generate_frames(detail, scene.get("scene_id"))
                
                if frames:
                    chapter_frames.extend(frames)
                    total_scenes += 1
                    
                    self._log_step("frame_generation_complete", {
                        "scene_id": scene.get("scene_id"),
                        "frames_count": len(frames)
                    })
            
            if chapter_frames:
                all_frames[chapter_id] = chapter_frames
        
        # 保存所有固定帧
        if all_frames:
            frames_file = os.path.join(self.project_path, "output", "all_frames.json")
            self.file_manager.write_json(frames_file, all_frames)
            print(f"已生成 {total_scenes} 个场景的固定帧")
            print(f"所有固定帧已保存到: {frames_file}")
        
        return all_frames
    
    def expand_to_story(self, frames_data: Dict[str, Any], style: str = "文学") -> Dict[str, Any]:
        """将固定帧扩写为完整故事"""
        print("扩写为完整故事...")
        
        all_chapters = {}
        total_frames = 0
        
        # 遍历所有章节的固定帧
        for chapter_id, frames in frames_data.items():
            chapter_text = []
            
            # 按顺序扩写每个固定帧
            for i, frame in enumerate(frames):
                print(f"扩写固定帧 {i+1}/{len(frames)}: {frame.get('frame_id', '未知')}")
                
                self._log_step("writing_expansion_start", {
                    "frame_id": frame.get("frame_id"),
                    "timestamp": frame.get("timestamp")
                })
                
                expanded = self.modules["writing"].expand_frame(frame, style)
                
                if expanded:
                    chapter_text.append(expanded)
                    total_frames += 1
                    
                    self._log_step("writing_expansion_complete", {
                        "frame_id": frame.get("frame_id"),
                        "text_length": len(expanded)
                    })
            
            # 组合章节内容
            if chapter_text:
                full_chapter = "\n\n".join(chapter_text)
                all_chapters[chapter_id] = full_chapter
                
                # 保存章节文件
                chapter_file = os.path.join(self.project_path, "output", "chapters", f"chapter_{chapter_id}.txt")
                self.file_manager.write_text(chapter_file, full_chapter)
        
        # 组合完整故事
        if all_chapters:
            # 按章节ID排序
            sorted_chapters = sorted(all_chapters.items(), key=lambda x: x[0])
            full_story = "\n\n" + "="*50 + "\n\n".join([text for _, text in sorted_chapters])
            
            # 保存完整故事
            story_file = os.path.join(self.project_path, "output", "full_story.txt")
            self.file_manager.write_text(story_file, full_story)
            
            print(f"故事生成完成！")
            print(f"总章节数: {len(all_chapters)}")
            print(f"总固定帧数: {total_frames}")
            print(f"完整故事已保存到: {story_file}")
            
            return {
                "chapters": all_chapters,
                "total_chapters": len(all_chapters),
                "total_frames": total_frames,
                "story_file": story_file
            }
        
        return {}
    
    def run_full_pipeline(self, story_concept: str, style: str = "文学"):
        """运行完整流水线"""
        print("="*60)
        print("开始运行完整故事生成流水线")
        print("="*60)
        
        # 1. 生成大纲
        print("\n[阶段1] 生成故事大纲")
        outline = self.generate_outline(story_concept)
        if not outline:
            print("大纲生成失败，停止流程")
            return
        
        # 2. 生成细纲
        print("\n[阶段2] 生成详细细纲")
        details = self.generate_details(outline)
        if not details:
            print("细纲生成失败，停止流程")
            return
        
        # 3. 生成固定帧
        print("\n[阶段3] 生成固定帧")
        frames = self.generate_frames(details)
        if not frames:
            print("固定帧生成失败，停止流程")
            return
        
        # 4. 扩写为故事
        print("\n[阶段4] 扩写为完整故事")
        result = self.expand_to_story(frames, style)
        
        print("\n" + "="*60)
        print("故事生成流水线完成！")
        print("="*60)
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """获取项目状态"""
        status = self.engine.get_status()
        
        # 检查各阶段完成情况
        output_dir = os.path.join(self.project_path, "output")
        status["stages"] = {
            "outline": len(self.file_manager.list_files(os.path.join(output_dir, "outlines"))) > 0,
            "details": len(self.file_manager.list_files(os.path.join(output_dir, "details"))) > 0,
            "frames": len(self.file_manager.list_files(os.path.join(output_dir, "frames"))) > 0,
            "chapters": len(self.file_manager.list_files(os.path.join(output_dir, "chapters"))) > 0
        }
        
        # 统计数据
        data_dir = os.path.join(self.project_path, "data")
        status["stats"] = {
            "characters": len(self.storage.list_entities("characters")),
            "locations": len(self.storage.list_entities("locations")),
            "items": len(self.storage.list_entities("items")),
            "environments": len(self.storage.list_entities("environments"))
        }
        
        return status
    
    def _log_step(self, step_name: str, data: Dict[str, Any]):
        """记录步骤日志"""
        log_entry = {
            "step": step_name,
            "timestamp": self.get_current_time(),
            "data": data
        }
        
        log_file = os.path.join(self.project_path, "logs", "pipeline.log")
        logs = []
        
        # 读取现有日志
        if os.path.exists(log_file):
            existing = self.file_manager.read_json(log_file)
            if isinstance(existing, list):
                logs = existing
        
        # 添加新日志
        logs.append(log_entry)
        
        # 保存日志
        self.file_manager.write_json(log_file, logs)
    
    @staticmethod
    def get_current_time() -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().isoformat()


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="自动故事写作系统")
    
    parser.add_argument(
        "--project", 
        type=str, 
        default="my_story",
        help="项目名称（默认: my_story）"
    )
    
    parser.add_argument(
        "--concept", 
        type=str,
        default="一个有关师徒的故事，类似剑三音乐中眉间雪那样，大概字数是数十万字以上，背景和剑三一样就好，其中以徒弟男主为视角",
        help="故事概念（必填）"
    )
    
    parser.add_argument(
        "--style", 
        type=str, 
        default="文学",
        choices=["文学", "通俗", "网络小说", "严肃文学", "轻小说"],
        help="写作风格（默认: 文学）"
    )
    
    parser.add_argument(
        "--mode", 
        type=str, 
        default="full",
        choices=["full", "outline", "detail", "frame", "write"],
        help="运行模式（默认: full）"
    )
    
    parser.add_argument(
        "--config", 
        type=str,
        help="配置文件路径（可选）"
    )
    
    parser.add_argument(
        "--status", 
        action="store_true",
        help="显示项目状态"
    )
    
    return parser.parse_args()


def load_config(config_file: str) -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件不存在: {config_file}")
        return {}
    except json.JSONDecodeError as e:
        print(f"配置文件解析错误: {e}")
        return {}


def main():
    """主函数"""
    args = parse_arguments()
    
    # 创建写作系统实例
    writer = AutoStoryWriter(args.project)
    
    # 如果指定了状态查询
    if args.status:
        status = writer.get_status()
        print("\n项目状态:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return
    
    # 加载配置
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # 设置项目配置
    if config:
        writer.setup_project(config)
    
    # 检查故事概念
    if not args.concept and args.mode != "status":
        print("错误: 请提供故事概念（使用 --concept 参数）")
        return
    
    # 根据模式运行
    if args.mode == "full":
        # 完整流水线
        writer.run_full_pipeline(args.concept, args.style)
    
    elif args.mode == "outline":
        # 仅生成大纲
        outline = writer.generate_outline(args.concept)
        if outline:
            print("\n生成的大纲:")
            print(json.dumps(outline, indent=2, ensure_ascii=False))
    
    elif args.mode == "detail":
        # 需要先有大纲
        print("详细模式需要先有大纲数据")
        # 这里可以扩展为从文件加载大纲
    
    elif args.mode == "frame":
        print("固定帧模式需要先有细纲数据")
        # 这里可以扩展为从文件加载细纲
    
    elif args.mode == "write":
        print("扩写模式需要先有固定帧数据")
        # 这里可以扩展为从文件加载固定帧
    
    # 显示最终状态
    status = writer.get_status()
    print("\n最终项目状态:")
    print(f"项目路径: {status['project_path']}")
    print(f"故事标题: {status['config'].get('title', '未设置')}")
    print(f"各阶段完成情况:")
    for stage, completed in status["stages"].items():
        print(f"  {stage}: {'✓' if completed else '✗'}")
    print(f"数据统计:")
    for data_type, count in status["stats"].items():
        print(f"  {data_type}: {count}")


if __name__ == "__main__":
    main()