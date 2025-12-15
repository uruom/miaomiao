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


def save_to_json(data: Dict[str, Any], filename: str):
    """将数据保存到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"结果已保存到: {filename}")


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
        output_data = {
            "type": "outline",
            "theme": novel_theme,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response": result
        }
        save_to_json(output_data, f"novel_outline_{int(time.time())}.json")
        return output_data
    return None


def generate_content(api_key: str, outline: Dict[str, Any], chapter: int = 1) -> Dict[str, Any]:
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

    {json.dumps(outline, ensure_ascii=False, indent=2)}
    """

    print(f"正在生成第{chapter}章内容...")
    result = call_siliconflow_api(api_key, system_prompt, user_input)

    if result:
        output_data = {
            "type": "content",
            "chapter": chapter,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "outline_reference": outline,
            "response": result
        }
        save_to_json(output_data, f"novel_chapter_{chapter}_{int(time.time())}.json")
        return output_data
    return None


def main():
    # 配置API密钥
    api_key = "sk-czprteaafqgpfewyrxwmhltdfdfaihpioejpfutupbcxyyao"

    if api_key == "<token>" or not api_key:
        print("请先替换api_key为您的实际API密钥")
        return

    # 创建输出目录
    os.makedirs("novel_output", exist_ok=True)
    os.chdir("novel_output")

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

    # 生成正文章节
    chapters = int(input("请输入要生成的章节数量 (默认3章): ") or "3")

    for chapter in range(1, chapters + 1):
        content = generate_content(api_key, outline, chapter)
        if not content:
            print(f"生成第{chapter}章失败")
            continue

        # 显示生成的内容摘要
        if 'choices' in content['response'] and content['response']['choices']:
            reply = content['response']['choices'][0]['message']['content']
            print(f"\n第{chapter}章生成成功！内容摘要:")
            print(reply[:200] + "..." if len(reply) > 200 else reply)
            print("-" * 50)

        # 章节间延迟，避免频繁调用
        time.sleep(1)

    print("小说生成完成！所有结果已保存到 novel_output 目录中")


if __name__ == "__main__":
    main()
