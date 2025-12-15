import requests
import json
import os
import time
from typing import Dict, Any, List
import re


def call_siliconflow_api(api_key: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    调用SiliconFlow API接口
    """
    url = "https://api.siliconflow.cn/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-ai/DeepSeek-V3.1",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4000
    }
    print(f"payload---{payload}")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"解析响应出错: {e}")
        return None


def summarize_content(api_key: str, content: str, summary_type: str = "chapter") -> str:
    """
    总结内容，减少token使用
    """
    if summary_type == "chapter":
        system_prompt = """你是一个专业的小说编辑。请用200字左右总结这一章的主要内容，保留关键情节、人物发展和重要对话。
        总结应该包含：
        1. 主要事件发展
        2. 人物关系变化
        3. 关键转折点
        4. 为后续埋下的伏笔"""
    else:
        system_prompt = """你是一个专业的小说编辑。请用300字左右总结这些章节的总体进展，突出故事的主线发展和重要变化。"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请总结以下内容：\n\n{content}"}
    ]

    result = call_siliconflow_api(api_key, messages)
    if result and 'choices' in result and result['choices']:
        return result['choices'][0]['message']['content']
    return "总结生成失败"


def save_outputs(full_response: Dict[str, Any], content: str, base_filename: str):
    """保存完整的JSON响应和提取的内容到单独的文件"""
    # 保存完整JSON响应
    json_filename = f"{base_filename}_full.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(full_response, f, indent=2, ensure_ascii=False)

    # 保存提取的内容（易读格式）
    content_filename = f"{base_filename}_content.txt"
    with open(content_filename, 'w', encoding='utf-8') as f:
        f.write(content)

    return json_filename, content_filename


def generate_outline(api_key: str, novel_theme: str) -> Dict[str, Any]:
    """生成小说大纲"""
    system_prompt = """你是一个专业的小说作家。请根据用户提供的主题，创作一个完整的小说大纲。
    大纲应该包含以下要素：
    1. 故事背景设定
    2. 主要人物介绍
    3. 故事的主要冲突
    4. 情节发展脉络（开端、发展、高潮、结局）
    5. 主题思想

    请用中文回复，输出格式为清晰的Markdown格式。"""

    print("正在生成小说大纲...")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": novel_theme}
    ]

    result = call_siliconflow_api(api_key, messages)

    if result:
        # 提取模型返回的内容
        content = ""
        if 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content']

        # 保存文件
        timestamp = int(time.time())
        base_filename = f"novel_outline_{timestamp}"
        json_path, txt_path = save_outputs(result, content, base_filename)

        return {
            "content": content,
            "json_path": json_path,
            "txt_path": txt_path,
            "timestamp": timestamp
        }
    return None


def generate_chapter(api_key: str, chapter_data: Dict[str, Any], current_chapter: int) -> Dict[str, Any]:
    """
    生成单个章节，包含记忆管理
    """
    # 构建上下文信息
    context_messages = []

    # 系统提示
    system_prompt = """你是一个专业的小说作家。请根据提供的故事大纲和前文内容，继续创作下一章。

    要求：
    1. 保持故事连贯性和一致性
    2. 文笔优美，情节生动
    3. 注重人物性格的延续性
    4. 每章约1000-1500字
    5. 结尾要留有悬念或为下一章埋下伏笔

    请用中文回复，输出格式为清晰的Markdown格式。"""

    context_messages.append({"role": "system", "content": system_prompt})

    # 添加大纲
    context_messages.append({
        "role": "user",
        "content": f"故事大纲：\n{chapter_data['outline']}"
    })

    # 添加故事摘要（记忆）
    if chapter_data.get('story_summary'):
        context_messages.append({
            "role": "user",
            "content": f"前文摘要：\n{chapter_data['story_summary']}"
        })

    # 添加最近2章的内容（保持连贯性）
    recent_chapters = chapter_data.get('recent_chapters', [])
    for i, chap in enumerate(recent_chapters[-2:], 1):  # 只取最近2章
        context_messages.append({
            "role": "user",
            "content": f"第{chap['chapter']}章内容：\n{chap['content']}"
        })

    # 添加本章创作指令
    context_messages.append({
        "role": "user",
        "content": f"请基于以上内容，创作第{current_chapter}章。"
    })

    print(f"正在生成第{current_chapter}章内容...")
    result = call_siliconflow_api(api_key, context_messages)

    if result:
        # 提取模型返回的内容
        content = ""
        if 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content']

        # 保存文件
        timestamp = int(time.time())
        base_filename = f"novel_chapter_{current_chapter}_{timestamp}"
        json_path, txt_path = save_outputs(result, content, base_filename)

        return {
            "chapter": current_chapter,
            "content": content,
            "json_path": json_path,
            "txt_path": txt_path,
            "timestamp": timestamp,
            "full_response": result
        }
    return None


def update_story_summary(api_key: str, current_summary: str, new_chapter_content: str, chapter_number: int) -> str:
    """
    更新故事摘要，融入新章节内容
    """
    if not current_summary:
        # 如果是第一个章节，直接总结
        return summarize_content(api_key, new_chapter_content, "chapter")

    # 合并现有摘要和新章节内容，然后重新总结
    combined_content = f"现有故事摘要：{current_summary}\n\n第{chapter_number}章内容：{new_chapter_content}"

    system_prompt = """你是一个专业的小说编辑。请将新的章节内容整合到现有的故事摘要中，创建一个更新的总体摘要。
    要求：
    1. 保持摘要简洁（300字以内）
    2. 突出主要情节发展
    3. 保留重要的人物关系和变化
    4. 体现故事的整体进展"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": combined_content}
    ]

    result = call_siliconflow_api(api_key, messages)
    if result and 'choices' in result and result['choices']:
        return result['choices'][0]['message']['content']

    return current_summary  # 如果总结失败，返回原摘要


def main():
    # 配置API密钥
    api_key = "sk-czprteaafqgpfewyrxwmhltdfdfaihpioejpfutupbcxyyao"

    if api_key == "<token>" or not api_key:
        print("请先替换api_key为您的实际API密钥")
        return

    # 创建输出目录
    output_dir = "novel_output"
    os.makedirs(output_dir, exist_ok=True)
    original_dir = os.getcwd()
    os.chdir(output_dir)

    try:
        # 用户输入小说主题
        novel_theme = input("请输入小说主题或创意: ").strip()
        if not novel_theme:
            novel_theme = "主角穿越到了1937年的南京，是地下工作人员，准备抗日"
            print(f"使用默认主题: {novel_theme}")

        # 生成大纲
        outline = generate_outline(api_key, novel_theme)
        if not outline:
            print("生成大纲失败")
            return

        print("\n" + "=" * 50)
        print("大纲生成完成！")
        print("=" * 50 + "\n")

        # 生成正文章节
        try:
            chapters = int(input("请输入要生成的章节数量 (默认3章): ") or "3")
        except ValueError:
            chapters = 3
            print(f"输入无效，使用默认值: {chapters}章")

        # 初始化故事状态
        story_state = {
            'outline': outline['content'],
            'story_summary': "",  # 总体故事摘要
            'recent_chapters': [],  # 最近章节内容（用于保持连贯性）
            'all_chapters': []  # 所有章节元数据
        }

        generated_chapters = []
        for chapter_num in range(1, chapters + 1):
            # 生成章节
            chapter_content = generate_chapter(api_key, story_state, chapter_num)
            if not chapter_content:
                print(f"生成第{chapter_num}章失败")
                continue

            generated_chapters.append(chapter_content)

            # 更新故事摘要
            new_summary = update_story_summary(
                api_key,
                story_state['story_summary'],
                chapter_content['content'],
                chapter_num
            )
            story_state['story_summary'] = new_summary

            # 更新最近章节列表（只保留最近2章的详细内容）
            story_state['recent_chapters'].append({
                'chapter': chapter_num,
                'content': chapter_content['content']
            })
            # 保持最近2章
            if len(story_state['recent_chapters']) > 2:
                story_state['recent_chapters'] = story_state['recent_chapters'][-2:]

            # 保存所有章节信息
            story_state['all_chapters'].append({
                'chapter': chapter_num,
                'json_path': chapter_content['json_path'],
                'txt_path': chapter_content['txt_path'],
                'timestamp': chapter_content['timestamp']
            })

            # 显示生成的内容摘要
            print(f"\n第{chapter_num}章生成成功！内容摘要:")
            preview = chapter_content['content'][:200] + "..." if len(chapter_content['content']) > 200 else \
            chapter_content['content']
            print(preview)
            print("-" * 50)

            # 保存当前故事状态（用于中断恢复）
            with open("story_state.json", 'w', encoding='utf-8') as f:
                json.dump(story_state, f, indent=2, ensure_ascii=False)

            # 章节间延迟，避免频繁调用
            time.sleep(2)

        # 生成最终汇总文件
        summary_data = {
            "project_info": {
                "theme": novel_theme,
                "total_chapters_requested": chapters,
                "generated_chapters": len(generated_chapters),
                "completion_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "final_story_summary": story_state['story_summary']
            },
            "files": {
                "outline": outline['txt_path'],
                "chapters": [f"第{chap['chapter']}章: {chap['txt_path']}" for chap in story_state['all_chapters']]
            }
        }

        with open("project_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        print(f"\n小说生成完成！共生成{len(generated_chapters)}章")
        print(f"最终故事摘要: {story_state['story_summary'][:100]}...")
        print(f"所有文件已保存到: {output_dir} 目录中")

    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    main()
