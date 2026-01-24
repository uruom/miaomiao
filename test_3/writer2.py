import requests
import json
import os
import time
from typing import Dict, Any


def call_siliconflow_api(api_key: str, system_prompt: str, user_input: str) -> Dict[str, Any]:
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
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }

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


def save_outputs(full_response: Dict[str, Any], content: str, base_filename: str):
    """保存完整的JSON响应和提取的内容到单独的文件"""
    # 保存完整JSON响应
    json_filename = f"{base_filename}_full.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(full_response, f, indent=2, ensure_ascii=False)
    print(f"完整响应已保存到: {json_filename}")

    # 保存提取的内容（易读格式）
    content_filename = f"{base_filename}_content.txt"
    with open(content_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"提取内容已保存到: {content_filename}")


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
    result = call_siliconflow_api(api_key, system_prompt, novel_theme)

    if result:
        # 提取模型返回的内容
        content = ""
        if 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content']

        # 准备输出数据
        output_data = {
            "type": "outline",
            "theme": novel_theme,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": result.get('model', 'unknown'),
            "usage": result.get('usage', {})
        }

        # 保存文件
        timestamp = int(time.time())
        base_filename = f"novel_outline_{timestamp}"
        save_outputs(result, content, base_filename)

        # 返回包含内容和元数据的结果
        return {
            "metadata": output_data,
            "content": content,
            "full_response": result
        }
    return None


def generate_content(api_key: str, outline_data: Dict[str, Any], chapter: int = 1) -> Dict[str, Any]:
    """生成小说正文"""
    system_prompt = """你是一个专业的小说作家。请根据提供的小说大纲，创作具体的小说正文内容。
    要求：
    1. 文笔优美，情节生动
    2. 保持与大纲的一致性
    3. 注重细节描写和人物刻画
    4. 每章内容约1000-1500字

    请用中文回复，输出格式为清晰的Markdown格式。"""

    user_input = f"""
    根据以下小说大纲，创作第{chapter}章的内容：

    {outline_data['content']}
    """

    print(f"正在生成第{chapter}章内容...")
    result = call_siliconflow_api(api_key, system_prompt, user_input)

    if result:
        # 提取模型返回的内容
        content = ""
        if 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content']

        # 准备输出数据
        output_data = {
            "type": "content",
            "chapter": chapter,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": result.get('model', 'unknown'),
            "usage": result.get('usage', {}),
            "outline_theme": outline_data['metadata']['theme']
        }

        # 保存文件
        timestamp = int(time.time())
        base_filename = f"novel_chapter_{chapter}_{timestamp}"
        save_outputs(result, content, base_filename)

        # 返回包含内容和元数据的结果
        return {
            "metadata": output_data,
            "content": content,
            "full_response": result
        }
    return None


def main():
    # 配置API密钥
    api_key = "sk-pdxifqjftnthcnfonzjerkeyiquovxfiupwovvxzhanzdujo"

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
            novel_theme = "男主作为一个程序员穿越到了一个玄幻小说中，他惊奇的发现所谓的修仙竟然只是编程"
            print(f"使用默认主题: {novel_theme}")

        # 生成大纲
        outline = generate_outline(api_key, novel_theme)
        if not outline:
            print("生成大纲失败")
            return

        # 显示大纲内容
        print("\n" + "=" * 50)
        print("大纲生成完成！内容预览:")
        print(outline['content'][:300] + "..." if len(outline['content']) > 300 else outline['content'])
        print("=" * 50 + "\n")

        # 生成正文章节
        try:
            chapters = int(input("请输入要生成的章节数量 (默认3章): ") or "3")
        except ValueError:
            chapters = 3
            print(f"输入无效，使用默认值: {chapters}章")

        generated_chapters = []
        for chapter in range(1, chapters + 1):
            content = generate_content(api_key, outline, chapter)
            if not content:
                print(f"生成第{chapter}章失败")
                continue

            generated_chapters.append(content)

            # 显示生成的内容摘要
            print(f"\n第{chapter}章生成成功！内容摘要:")
            print(content['content'][:200] + "..." if len(content['content']) > 200 else content['content'])
            print("-" * 50)

            # 章节间延迟，避免频繁调用
            time.sleep(1)

        # 生成汇总文件
        summary_data = {
            "project_summary": {
                "theme": novel_theme,
                "total_chapters": chapters,
                "generated_chapters": len(generated_chapters),
                "completion_time": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "files": {
                "outline": f"novel_outline_*.json and novel_outline_*.txt",
                "chapters": [f"novel_chapter_{i}_*.json and novel_chapter_{i}_*.txt" for i in range(1, chapters + 1)]
            }
        }

        with open("project_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        print(f"\n小说生成完成！共生成{len(generated_chapters)}章")
        print(f"所有文件已保存到: {output_dir} 目录中")
        print("包括:")
        print("- 完整JSON响应文件 (*_full.json)")
        print("- 提取的内容文本文件 (*_content.txt)")
        print("- 项目汇总文件 (project_summary.json)")

    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    main()
