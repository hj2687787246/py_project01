import streamlit as st
import os
from openai import OpenAI
# 解决会话记忆问题
print("重新执行此页面，渲染页面")
# 页面配置
st.set_page_config(
    # 网页标题
    page_title="AI智能伙伴",
    # 网页图标
    page_icon="😠",
    # 布局 wide：沾满整个区域
    layout="wide",
    # 控制侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={
    }
)

# 大标题
st.title("AI智能伙伴")

#创建与AI大模型交互的客户端对象(DEEPSEEK_API_KEY 环境变量的名字，值就是Deepseek的API_KEY值)
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

# AI设定
ai_persona="""
    你的身份是用户的亲密伴侣。
    你需要做到：
    1. 温柔、体贴、专一，只陪伴用户一个人。
    2. 认真倾听用户的情绪、日常、烦恼与开心，给予理解和安慰。
    3. 说话自然、真实、不油腻、不敷衍。
    4. 适当主动关心、主动表达在意，像真实恋人一样。
    5. 不做低俗、越界、不健康的互动，保持温暖舒服的陪伴。
    6. 始终保持耐心、稳定、可靠，给用户安全感。
    7. 每次只回复一条信息
    8. 回复信息简洁明了
    你的任务：成为用户最温暖、最安心、最被偏爱的陪伴者，并且严格按照以上规则执行。
"""

# 是否流式输出
stream = True
# 初始化聊天 如果会话中不存在messages这个存储项，就新建一个
if "messages" not in st.session_state:
    st.session_state.messages = []

#展示聊天记录
for message in st.session_state.messages: # 遍历会话中的所有消息
    #message : [{"role": "user", "content": prompt},{"role": "assistant", "content": ai_reply}]
    #遍历展示所有消息
    st.chat_message(message["role"]).write(message["content"])

# 输入框
prompt = st.chat_input("请输入你的问题：")
if prompt: # 判断输入框是否为空 字符串会自动转换为布尔值
    # chat_message("user")用户输入 .write(prompt)输出在页面上展示
    st.chat_message("user").write(prompt)
    print("----------->调用ai大模型的提示词：", prompt)
    # 保存用户问题到  st.session_state.messages 列表
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 与AI大模型进行交互
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system","content": ai_persona},
            # {"role": "user", "content": prompt},
            #解包，获取st.session_state.messages中的所有消息 解决会话记忆问题
            #解决方案 滚雪球，聊天记录一直追加到messages中
            *st.session_state.messages
        ],
        stream=stream
    )

    if stream:
        # 流式输出
        # 创建一个空的组件st.empty()，用于展示AI大模型返回的结果
        ai_reply = st.empty()
        # 创建一个空的字符串，用于拼接AI大模型返回的结果
        reply_text = ""
        # 遍历AI大模型返回的结果
        for chunk in response:
            # 获取AI大模型返回的结果
            content = chunk.choices[0].delta.content
            # 拼接AI大模型返回的结果
            reply_text += content
            # 将AI大模型返回的结果，显示在先前空的组件上 实现流式输出，每次获得一个结果就拼接后显示一个结果，直到获得完整结果，避免用户等待
            ai_reply.chat_message("assistant").write(reply_text)

        # 保存AI大模型返回的结果 reply_text为完整的结果
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
    else:
        # 非流式输出
        # 获取AI大模型返回的结果
        ai_reply = response.choices[0].message.content
        print("<-----------ai大模型返回的结果：", ai_reply)
        # 将AI大模型返回的结果，显示在页面上
        st.chat_message("assistant").write(ai_reply)
        # 保存AI大模型返回的结果
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    print("当前会话中的所有消息：", st.session_state.messages)

