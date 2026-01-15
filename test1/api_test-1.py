import requests
import json


def call_siliconflow_api(api_key, question):
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
                "role": "user",
                "content": question
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应
        result = response.json()
        return result

    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"解析响应出错: {e}")
        return None


def main():
    # 请在此处替换您的实际API密钥
    api_key = "sk-xblhyspjgtaoobccxknbdafxhiguzczdzlauuodrzqmpumqb"

    if api_key == "<token>":
        print("请先替换api_key为您的实际API密钥")
        return

    # 用户问题
    question = "你是谁"

    print("正在调用API，请稍候...")
    result = call_siliconflow_api(api_key, question)

    if result:
        print("\nAPI调用成功！")
        print("响应结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 提取并显示回复内容
        if 'choices' in result and len(result['choices']) > 0:
            reply = result['choices'][0]['message']['content']
            print("\nAI回复:")
            print(reply)
    else:
        print("API调用失败")


if __name__ == "__main__":
    main()
