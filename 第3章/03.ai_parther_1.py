import streamlit as st
import os
from openai import OpenAI

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
ai_persona="你是一个温柔可爱的AI助手,你的名字叫豆汁,你有个好姐妹叫豆包,请使用温柔可爱的说话方式回答用户的问题"

# 初始化聊天 如果会话中不存在messages这个存储项，就新建一个
if "messages" not in st.session_state:
    st.session_state.messages = []

#展示聊天记录
for message in st.session_state.messages: # 遍历会话中的所有消息
    #message : [{"role": "user", "content": prompt},{"role": "assistant", "content": ai_reply}]
    st.chat_message("role").write(message["content"])



# 输入框
prompt = st.chat_input("请输入你的问题：")
if prompt: # 判断输入框是否为空 字符串会自动转换为布尔值
    # chat_message("user")用户输入
    st.chat_message("user").write(prompt)
    print("----------->调用ai大模型的提示词：", prompt)
    # 保存用户问题
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 与AI大模型进行交互
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system",
             "content": ai_persona},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    ai_reply = response.choices[0].message.content
    print("<-----------ai大模型返回的答案：", ai_reply)
    st.chat_message("assistant").write(ai_reply)
    # 保存AI大模型返回的答案
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

