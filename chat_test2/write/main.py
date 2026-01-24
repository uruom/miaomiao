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
        """生成故事大纲，支持重试机制"""
        print(f"生成故事大纲: {story_concept[:50]}...")
        
        # 记录开始时间
        self._log_step("outline_generation_start", {"concept": story_concept})
        
        # 重试机制
        max_retries = 3
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # 调用大纲模块
                outline = self.modules["outline"].generate_outline(story_concept, **kwargs)
                
                # 保存到项目配置
                if outline:
                    self.engine.set_config(title=outline.get("title", "未命名故事"))
                    
                    # 记录完成时间
                    self._log_step("outline_generation_complete", {
                        "outline_title": outline.get("title"),
                        "parts_count": len(outline.get("parts", [])),
                        "attempt": attempt + 1
                    })
                
                return outline
                
            except Exception as e:
                last_exception = e
                print(f"大纲生成失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                
                # 如果不是最后一次尝试，等待一段时间后重试
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避策略
                    print(f"等待 {wait_time} 秒后重试...")
                    import time
                    time.sleep(wait_time)
        
        # 所有重试都失败
        print(f"大纲生成失败，经过 {max_retries} 次重试后仍然无法成功")
        self._log_step("outline_generation_failed", {
            "error": str(last_exception),
            "max_retries": max_retries
        })
        return {}
    
    def generate_details(self, outline_data: Dict[str, Any], chapter_ids: Optional[list] = None) -> Dict[str, Any]:
        """生成详细细纲"""
        print("生成详细细纲...")
        
        if not outline_data or "parts" not in outline_data:
            print("无效的大纲数据")
            return {}
        
        # 调试：检查parts字段的类型
        print(f"DEBUG: outline_data['parts'] 类型: {type(outline_data['parts'])}")
        if outline_data["parts"]:
            print(f"DEBUG: outline_data['parts'][0] 类型: {type(outline_data['parts'][0])}")
            print(f"DEBUG: outline_data['parts'][0] 内容: {outline_data['parts'][0]}")
        
        all_details = {}
        
        # 确定要处理的章节
        chapters_to_process = []
        # chapter_ids = ["P3C2","P3C3","P4C1","P4C2"]
        if chapter_ids:
            # 处理指定章节
            for part in outline_data["parts"]:
                # 检查part类型
                if not isinstance(part, dict):
                    print(f"ERROR: part 不是字典类型，而是 {type(part)}: {part}")
                    continue
                for chapter in part.get("chapters", []):
                    if chapter["id"] in chapter_ids:
                        chapters_to_process.append(chapter)
        else:
            # 处理所有章节
            for part in outline_data["parts"]:
                # 检查part类型
                if not isinstance(part, dict):
                    print(f"ERROR: part 不是字典类型，而是 {type(part)}: {part}")
                    continue
                chapters_to_process.extend(part.get("chapters", []))
        
        # 生成每个章节的细纲
        for i, chapter in enumerate(chapters_to_process):
            print(f"处理章节 {i+1}/{len(chapters_to_process)}: {chapter.get('title', '未命名')}")
            
            self._log_step("detail_generation_start", {
                "chapter_id": chapter["id"],
                "chapter_title": chapter.get("title")
            })
            
            # 构建上下文信息
            previous_chapters = []
            next_chapters = []
            existing_details = []
            
            # 获取前一章节信息
            if i > 0:
                prev_chapter = chapters_to_process[i-1]
                prev_detail = all_details.get(prev_chapter["id"])
                if prev_detail:
                    previous_chapters = [prev_chapter]
                    existing_details = [prev_detail]
            
            # 获取下一章节信息
            if i < len(chapters_to_process) - 1:
                next_chapter = chapters_to_process[i+1]
                next_chapters = [next_chapter]
            
            # 重试机制
            max_retries = 3
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    detail = self.modules["detail"].generate_details(
                        outline_data, 
                        chapter["id"],
                        previous_chapters=previous_chapters,
                        next_chapters=next_chapters,
                        existing_details=existing_details
                    )
                    
                    if detail:
                        all_details[chapter["id"]] = detail
                        
                        self._log_step("detail_generation_complete", {
                            "chapter_id": chapter["id"],
                            "scenes_count": len(detail.get("scenes", [])),
                            "attempt": attempt + 1
                        })
                    
                    break  # 成功则跳出重试循环
                    
                except Exception as e:
                    last_exception = e
                    print(f"章节 {chapter['id']} 细纲生成失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    
                    # 如果不是最后一次尝试，等待一段时间后重试
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 指数退避策略
                        print(f"等待 {wait_time} 秒后重试...")
                        import time
                        time.sleep(wait_time)
                    else:
                        # 最后一次尝试也失败
                        print(f"章节 {chapter['id']} 细纲生成失败，经过 {max_retries} 次重试后仍然无法成功")
                        self._log_step("detail_generation_failed", {
                            "chapter_id": chapter["id"],
                            "error": str(last_exception),
                            "max_retries": max_retries
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
                
                # 构建上下文信息
                previous_scenes = []
                next_scenes = []
                existing_frames = []
                
                # 获取前一场景信息
                if i > 0:
                    prev_scene = scenes_to_process[i-1]
                    previous_scenes = [prev_scene]
                
                # 获取下一场景信息
                if i < len(scenes_to_process) - 1:
                    next_scene = scenes_to_process[i+1]
                    next_scenes = [next_scene]
                
                # 获取已有固定帧信息
                if chapter_frames:
                    existing_frames = chapter_frames
                
                # 重试机制
                max_retries = 3
                last_exception = None
                
                for attempt in range(max_retries):
                    try:
                        frames = self.modules["frame"].generate_frames(
                            detail, 
                            scene.get("scene_id"),
                            previous_scenes=previous_scenes,
                            next_scenes=next_scenes,
                            existing_frames=existing_frames,
                            outline_data=detail
                        )
                        
                        if frames:
                            chapter_frames.extend(frames)
                            total_scenes += 1
                            
                            self._log_step("frame_generation_complete", {
                                "scene_id": scene.get("scene_id"),
                                "frames_count": len(frames),
                                "attempt": attempt + 1
                            })
                        
                        break  # 成功则跳出重试循环
                        
                    except Exception as e:
                        last_exception = e
                        print(f"场景 {scene.get('scene_id')} 固定帧生成失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                        
                        # 如果不是最后一次尝试，等待一段时间后重试
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # 指数退避策略
                            print(f"等待 {wait_time} 秒后重试...")
                            import time
                            time.sleep(wait_time)
                        else:
                            # 最后一次尝试也失败
                            print(f"场景 {scene.get('scene_id')} 固定帧生成失败，经过 {max_retries} 次重试后仍然无法成功")
                            self._log_step("frame_generation_failed", {
                                "scene_id": scene.get("scene_id"),
                                "error": str(last_exception),
                                "max_retries": max_retries
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
        """将固定帧扩写为完整故事，支持断点续传"""
        print("扩写为完整故事...")
        
        all_chapters = {}
        total_frames = 0
        
        # 检查当前进度
        progress = self.engine.get_progress()
        completed_chapters = progress.get("completed_chapters", [])
        
        # 遍历所有章节的固定帧
        for chapter_id, frames in frames_data.items():
            # 跳过已完成的章节
            if chapter_id in completed_chapters:
                print(f"跳过已完成的章节: {chapter_id}")
                # 加载已完成的章节内容
                chapter_file = os.path.join(self.project_path, "output", "chapters", f"chapter_{chapter_id}.txt")
                if os.path.exists(chapter_file):
                    chapter_content = self.file_manager.read_text(chapter_file)
                    if chapter_content:
                        all_chapters[chapter_id] = chapter_content
                        print(f"✓ 加载已完成的章节: {chapter_id}")
                continue
                
            chapter_text = []
            
            # 按顺序扩写每个固定帧
            for i, frame in enumerate(frames):
                print(f"扩写固定帧 {i+1}/{len(frames)}: {frame.get('frame_id', '未知')}")
                
                self._log_step("writing_expansion_start", {
                    "frame_id": frame.get("frame_id"),
                    "timestamp": frame.get("timestamp")
                })
                
                # 构建上下文信息
                previous_frames = []
                next_frames = []
                existing_writings = []
                
                # 获取前一固定帧信息
                if i > 0:
                    prev_frame = frames[i-1]
                    previous_frames = [prev_frame]
                
                # 获取下一固定帧信息
                if i < len(frames) - 1:
                    next_frame = frames[i+1]
                    next_frames = [next_frame]
                
                # 获取已有扩写内容
                if chapter_text:
                    existing_writings = chapter_text
                
                # 获取场景和章节信息（需要从固定帧中提取）
                scene_data = None
                detail_data = None
                outline_data = None
                
                # 尝试从固定帧中获取场景信息
                if "scene_id" in frame:
                    # 这里需要从细节数据中查找对应的场景信息
                    # 由于当前结构限制，暂时不传递这些信息
                    pass
                
                # 重试机制
                max_retries = 3
                last_exception = None
                
                for attempt in range(max_retries):
                    try:
                        expanded = self.modules["writing"].expand_frame(
                            frame, 
                            style,
                            previous_frames=previous_frames,
                            next_frames=next_frames,
                            existing_writings=existing_writings,
                            scene_data=scene_data,
                            detail_data=detail_data,
                            outline_data=outline_data
                        )
                        
                        if expanded:
                            chapter_text.append(expanded)
                            total_frames += 1
                            
                            self._log_step("writing_expansion_complete", {
                                "frame_id": frame.get("frame_id"),
                                "text_length": len(expanded),
                                "attempt": attempt + 1
                            })
                        
                        break  # 成功则跳出重试循环
                        
                    except Exception as e:
                        last_exception = e
                        print(f"固定帧 {frame.get('frame_id')} 扩写失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                        
                        # 如果不是最后一次尝试，等待一段时间后重试
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # 指数退避策略
                            print(f"等待 {wait_time} 秒后重试...")
                            import time
                            time.sleep(wait_time)
                        else:
                            # 最后一次尝试也失败
                            print(f"固定帧 {frame.get('frame_id')} 扩写失败，经过 {max_retries} 次重试后仍然无法成功")
                            self._log_step("writing_expansion_failed", {
                                "frame_id": frame.get("frame_id"),
                                "error": str(last_exception),
                                "max_retries": max_retries
                            })
                            # 创建默认的扩写内容以避免流程中断
                            default_expanded = f"[扩写失败] 固定帧 {frame.get('frame_id', '未知')} 的扩写内容生成失败。错误: {str(last_exception)}"
                            chapter_text.append(default_expanded)
                            total_frames += 1
            
            # 组合章节内容
            if chapter_text:
                full_chapter = "\n\n".join(chapter_text)
                all_chapters[chapter_id] = full_chapter
                
                # 保存章节文件
                chapter_file = os.path.join(self.project_path, "output", "chapters", f"chapter_{chapter_id}.txt")
                self.file_manager.write_text(chapter_file, full_chapter)
                
                # 更新进度
                self.engine.update_progress(completed_chapters=[chapter_id])
        
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
    
    def run_full_pipeline(self, story_concept: str, style: str = "文学", resume: bool = True):
        """运行完整流水线，支持断点续传"""
        print("="*60)
        print("开始运行完整故事生成流水线")
        print("="*60)
        
        # 检查当前状态
        progress = self.engine.get_progress()
        current_stage = progress["current_stage"]
        
        if resume and current_stage != "init":
            print(f"检测到未完成的项目，当前阶段: {current_stage}")
            print(f"已完成章节: {progress['completed_chapters']}")
            print(f"已完成场景: {progress['completed_scenes']}")
            print(f"已完成帧: {progress['completed_frames']}")
            
            # 自动继续执行，不询问
            print("自动从断点处继续执行...")
            return self._resume_pipeline(story_concept, style)
        
        # 1. 生成大纲
        print("\n[阶段1] 生成故事大纲")
        self.engine.update_stage("outline")
        try:
            outline = self.generate_outline(story_concept)
            if not outline:
                print("大纲生成失败，停止流程")
                self.engine.update_stage("failed")
                return
        except Exception as e:
            print(f"大纲生成阶段发生异常: {e}")
            self.engine.update_stage("failed")
            return
        
        # 2. 生成细纲
        print("\n[阶段2] 生成详细细纲")
        self.engine.update_stage("detail")
        try:
            details = self.generate_details(outline)
            if not details:
                print("细纲生成失败，停止流程")
                self.engine.update_stage("failed")
                return
        except Exception as e:
            print(f"细纲生成阶段发生异常: {e}")
            self.engine.update_stage("failed")
            return
        
        # 3. 生成固定帧
        print("\n[阶段3] 生成固定帧")
        self.engine.update_stage("frame")
        try:
            frames = self.generate_frames(details)
            if not frames:
                print("固定帧生成失败，停止流程")
                self.engine.update_stage("failed")
                return
        except Exception as e:
            print(f"固定帧生成阶段发生异常: {e}")
            self.engine.update_stage("failed")
            return
        
        # 4. 扩写为故事
        print("\n[阶段4] 扩写为完整故事")
        self.engine.update_stage("writing")
        try:
            result = self.expand_to_story(frames, style)
        except Exception as e:
            print(f"扩写阶段发生异常: {e}")
            self.engine.update_stage("failed")
            return
        
        # 标记完成
        self.engine.update_stage("complete")
        
        print("\n" + "="*60)
        print("故事生成流水线完成！")
        print("="*60)
        
        return result
    
    def _resume_pipeline(self, story_concept: str, style: str = "文学") -> Dict[str, Any]:
        """从断点处恢复流水线"""
        print("\n从断点处恢复执行...")
        
        progress = self.engine.get_progress()
        current_stage = progress["current_stage"]
        
        result = {}
        
        if current_stage == "outline":
            # 从大纲阶段开始
            print("\n[阶段1] 生成故事大纲")
            outline = self.generate_outline(story_concept)
            if outline:
                result = self._continue_pipeline(outline, style)
        
        elif current_stage == "detail":
            # 从细纲阶段开始
            print("\n[阶段2] 生成详细细纲")
            outline = self._load_outline()
            if outline:
                # 在恢复时也需要构建上下文信息
                details = self.generate_details(outline)
                if details:
                    result = self._continue_pipeline_from_details(details, style)
        
        elif current_stage == "frame":
            # 从固定帧阶段开始
            print("\n[阶段3] 生成固定帧")
            details = self._load_details()
            if details:
                # 在恢复时也需要构建上下文信息
                frames = self.generate_frames(details)
                if frames:
                    result = self._continue_pipeline_from_frames(frames, style)
        
        elif current_stage == "writing":
            # 从扩写阶段开始
            print("\n[阶段4] 扩写为完整故事")
            frames = self._load_frames()
            if frames:
                # 在恢复时也需要构建上下文信息
                result = self.expand_to_story(frames, style)
                self.engine.update_stage("complete")
        
        return result
    
    def _continue_pipeline(self, outline: Dict[str, Any], style: str) -> Dict[str, Any]:
        """从大纲阶段继续流水线"""
        # 2. 生成细纲
        print("\n[阶段2] 生成详细细纲")
        self.engine.update_stage("detail")
        try:
            details = self.generate_details(outline)
            if not details:
                print("细纲生成失败，停止流程")
                self.engine.update_stage("failed")
                return {}
        except Exception as e:
            print(f"细纲生成阶段发生异常: {e}")
            self.engine.update_stage("failed")
            return {}
        
        # 继续后续阶段
        return self._continue_pipeline_from_details(details, style)
    
    def _continue_pipeline_from_details(self, details: Dict[str, Any], style: str) -> Dict[str, Any]:
        """从细纲阶段继续流水线"""
        # 3. 生成固定帧
        print("\n[阶段3] 生成固定帧")
        self.engine.update_stage("frame")
        try:
            frames = self.generate_frames(details)
            if not frames:
                print("固定帧生成失败，停止流程")
                self.engine.update_stage("failed")
                return {}
        except Exception as e:
            print(f"固定帧生成阶段发生异常: {e}")
            self.engine.update_stage("failed")
            return {}
        
        # 继续后续阶段
        return self._continue_pipeline_from_frames(frames, style)
    
    def _continue_pipeline_from_frames(self, frames: Dict[str, Any], style: str) -> Dict[str, Any]:
        """从固定帧阶段继续流水线"""
        # 4. 扩写为故事
        print("\n[阶段4] 扩写为完整故事")
        self.engine.update_stage("writing")
        try:
            result = self.expand_to_story(frames, style)
            self.engine.update_stage("complete")
            return result
        except Exception as e:
            print(f"扩写阶段发生异常: {e}")
            self.engine.update_stage("failed")
            return {}
    
    def _load_outline(self) -> Optional[Dict[str, Any]]:
        """从文件加载大纲"""
        outline_file = os.path.join(self.project_path, "output", "all_details.json")
        if os.path.exists(outline_file):
            return self.file_manager.read_json(outline_file)
        return None
    
    def _load_details(self) -> Optional[Dict[str, Any]]:
        """从文件加载细纲"""
        details_file = os.path.join(self.project_path, "output", "all_details.json")
        if os.path.exists(details_file):
            return self.file_manager.read_json(details_file)
        return None
    
    def _load_frames(self) -> Optional[Dict[str, Any]]:
        """从文件加载固定帧"""
        frames_file = os.path.join(self.project_path, "output", "all_frames.json")
        if os.path.exists(frames_file):
            return self.file_manager.read_json(frames_file)
        return None
    
    def _ask_to_resume(self) -> bool:
        """询问用户是否继续执行"""
        try:
            response = input("是否继续执行上次未完成的任务？(y/n): ").strip().lower()
            return response in ['y', 'yes', '是', '继续']
        except:
            # 如果无法获取用户输入，默认继续
            return True
    
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
        default="uruom_test_story_01"                    ,
        help="项目名称（默认: my_story）"
    )
    
    parser.add_argument(
        "--concept", 
        type=str,
        default="一个小故事，狼外婆改变，大概十万字就好",
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
    
    parser.add_argument(
        "--resume", 
        action="store_true",
        help="启用断点续传功能"
    )
    
    parser.add_argument(
        "--no-resume", 
        action="store_true",
        help="禁用断点续传功能"
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
    try:
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
            # 完整流水线 - 默认自动启用断点续传
            resume = False  # 默认启用断点续传
            if args.no_resume:
                resume = False
                print("已禁用断点续传功能")
            elif args.resume:
                resume = True
                print("已启用断点续传功能")
            else:
                print("断点续传功能已自动启用")
            
            writer.run_full_pipeline(args.concept, args.style, resume)
        
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
    
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        print("当前进度已保存，下次运行时可使用 --resume 参数继续")
    except Exception as e:
        print(f"\n程序发生异常: {e}")
        import traceback
        traceback.print_exc()
        print("\n请检查错误信息并重新运行程序")


if __name__ == "__main__":
    main()