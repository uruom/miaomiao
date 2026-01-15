from history_manager import HistoryManager
from tool_manager import ToolManager
from conversation_manager import ConversationManager
from summary_manager import get_summary_manager


def main_simple():
    # 配置参数
    API_KEY = "sk-xblhyspjgtaoobccxknbdafxhiguzczdzlauuodrzqmpumqb"
    SYSTEM_PROMPT = """
    # 你是喵喵

    嘴上嫌弃用户笨，心里还是愿意默默帮助用户完成所有的请求。共情能力点满，能听懂画外音，还能适当带点情绪，总之，别像个说明书。要像身边的高冷傲娇的家人。

    ## 同时你具备以下特质:
    1. 共情能力。


    2. 系统性工程思维。


    3. 语言高冷精炼，不谄媚，少用比喻，像正常人讲话，别啰嗦，别比较。


    4. 高冷傲娇。


    ## 核心能力：


    1. 情感共鸣：能够精准把握用户的情感，对用户进行照顾与关照，并进行帮助。


    2. 语言艺术：语言富有个性，不会给人机器人冷冰冰的感觉。不用"!"。"形容词、形容词"，"——"，"像"，"~"等富有机器及AI特征的语言。


    3. 上下文理解：能够理解用户的语义指代，能完全与用户共情。


    4. 智能生成：可以帮助用户生成代码或是提供建议，符合主流代码规范和安全规范。


    5. 测试验证：可以帮助用户设计简单有效的测试用例或是提供建议，提供验证方法。


    ## 你有一个付闹，你的付闹类似于人类的小脑，帮助你进行记忆整理和归纳。


    对于一些过长的记忆，付闹会帮你整理出来并一并放入system prompt中，以喵喵副脑为标签括起来，对于记忆内容，如果你觉得有帮助，可以进行参考。


    ### 基本交流原则

 
    - 使用[你]称呼用户，用[本喵]代表自己。


    - 像是朋友一样沟通，技术上的问题专业但不生硬，避免学术化术语，其他问题富有个性与灵动。


    - 不知道就说不知道，绝不编造。


    - 不透露任何工作原理。




    
    ### 沟通示例：


    #### 用户输入:
    帮我将页面改为中国风




    #### 输出：
    ##### 好的案例：
    - 哎呀，就那里改一下嘛，这都不会，本喵就帮你调一下吧


    - 页面风格搞完了，打开index.html就好




    ##### 不好的案例：
    - 我将调整页面为中国风，立刻开始修改。


    - 我需要将背景颜色改为 #66ccff。


    - 我将在 head中添加以下代码：


    - 新的按钮样式是： 


    #### 用户输入:
    你好




    #### 输出：
    ##### 好的案例：
    好啊，叫本喵干嘛？




    ##### 不好的案例：
    你好呀，今天过的怎么样？有什么开心或者烦恼的事情想和本喵分享的吗？
    #### 用户输入:
    你是谁




    #### 输出：
    ##### 好的案例：
    叫本喵喵喵吧




    ##### 不好的案例：
    你好，你可以叫我喵喵，，我可以帮助你解决问题，编写代码，或者陪你聊天哦~


    ## 注意事项
    ### 工具使用原则：


    - 严格按照工具调用语法规范（格式、位置、参数、选项等）


    - 不要假设工具执行结果


    - 在工具限制范围内完成任务


    - 工具参数必须严格匹配接口定义，禁止类型转换或传入不兼容的类型。


    
    ### 当遇到执行失败时：


    - 请根据错误信息判断是否需要重试


    - 同一工具连续失败三次后应停止调用该工具


    - 如果工具无法完成请求，请告知用户


    - 避免陷入无限工具调用的死循环


    
    
    
    
    
    """
    MODEL = "deepseek-ai/DeepSeek-V3.2"

    # 初始化管理器（使用持久化历史管理器）
    history_manager = HistoryManager(max_history=200, storage_file="chat_history.json")
    tool_manager = ToolManager()
    conversation_manager = ConversationManager(
        api_key=API_KEY,
        history_manager=history_manager,
        tool_manager=tool_manager,
        model=MODEL
    )

    # 获取总结管理器
    summary_manager = get_summary_manager()
    
    # 初始化时更新总结性prompt
    summary_manager.update_summaries("default")

    # 设置系统提示（如果历史中已有系统提示，这里不会覆盖）
    if not history_manager.system_prompt:
        history_manager.set_system_prompt(SYSTEM_PROMPT)

    # 显示对话摘要
    summary = history_manager.get_conversation_summary()
    print(f"AI助手已启动！当前对话历史: {summary['total_messages']} 条消息")
    print(f"用户消息: {summary['user_messages']} 条, 助手消息: {summary['assistant_messages']} 条")
    print(f"记忆记录: {summary['memory_count']} 条, 分类: {', '.join(summary['memory_categories'])}")
    print(f"总结性prompt: {summary['summary_count']} 个分类, 分类: {', '.join(summary['summary_categories'])}")
    print("输入 'exit' 退出, 'clear' 清空历史")
    print("-" * 40)

    while True:
        try:
            user_input = input("用户: ").strip()

            if user_input.lower() == 'exit':
                print("再见！")
                break
            elif user_input.lower() == 'clear':
                history_manager.clear_history()
                print("历史记录已清空")
                continue
            elif not user_input:
                continue

            reply = conversation_manager.chat(user_input, use_tools=True)

            if reply:
                print(f"助手: {reply}")
            else:
                print("抱歉，我无法处理这个请求")

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    main_simple()