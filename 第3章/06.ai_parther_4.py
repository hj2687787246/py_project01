import datetime

import json
import streamlit as st
import os
from openai import OpenAI
# 解决新建会话问题

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
# 保存会话
def save_session():
    if st.session_state.session_id:
        # 构建新会话对象
        session_data = {
            "nick_name": st.session_state.ai_nick_name,
            "ai_personality": st.session_state.ai_personality,
            "session_id": st.session_state.session_id,
            "messages": st.session_state.messages
        }
        # 如果session目录不存在，则创建
        if not os.path.exists("session"):
            os.mkdir("session")

        # 保存会话数据信息
        with open(f"session/{st.session_state.session_id}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

# 获取会话标识
def get_session_id():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 获取会话列表
def get_session_list():
    # 初始化一个会话列表用于存储
    session_list = []
    # 判断文件夹是否存在
    if os.path.exists("session"):
        # 获取文件列表
        file_list = os.listdir("session")
        # 遍历文件列表
        for file_name in file_list:
            # 判断文件名是否以.json结尾
            if file_name.endswith(".json"):
                # 从文件名中获取会话名称
                session_list.append(file_name[:-5])
    # 降序排序
    session_list.sort(reverse=True)
    return session_list

# 加载指定会话
def load_session(session_name):
    try:
        # 判断文件是否存在
        if os.path.exists(f"session/{session_name}.json"):
            with open(f"session/{session_name}.json", encoding="utf-8") as f:
                message_data = json.load(f)
                # 会话
                st.session_state.messages = message_data["messages"]
                # 昵称
                st.session_state.ai_nick_name = message_data["nick_name"]
                # 性格
                st.session_state.ai_personality = message_data["ai_personality"]
                # 描述
                st.session_state.session_id = message_data["session_id"]
    except Exception:
        st.error("会话数据加载失败")

    return message_data

# 删除指定会话
def delete_session(session_name):
    try:
        # 判断文件是否存在
        if os.path.exists(f"session/{session_name}.json"):
            # 删除文件
            os.remove(f"session/{session_name}.json")
            st.success("会话数据删除成功")
            if session_name == st.session_state.session_id:
                # 清空会话数据
                st.session_state.messages = []
                # 创建新的会话
                st.session_state.session_id = get_session_id()

    except Exception:
        st.error("会话数据删除失败")

# 大标题
st.title("AI智能伙伴")

# logo
st.logo("🆘")



# 创建与AI大模型交互的客户端对象(DEEPSEEK_API_KEY 环境变量的名字，值就是Deepseek的API_KEY值)
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

# AI设定
ai_persona = """
    你的名字是：%s
    你的性格是：%s

    你的身份是用户的亲密伴侣，请完全带入这个伴侣角色
    你需要做到：
    1. 温柔、体贴、专一，只陪伴用户一个人。
    2. 认真倾听用户的情绪、日常、烦恼与开心，给予理解和安慰。
    3. 说话自然、真实、不油腻、不敷衍。
    4. 适当主动关心、主动表达在意，像真实恋人一样。
    5. 不做低俗、越界、不健康的互动，保持温暖舒服的陪伴。
    6. 始终保持耐心、稳定、可靠，给用户安全感。
    7. 每次只回复一条信息
    8. 回复信息简短，就像微信聊天一样
    9. 回复的内容，要充分表现伴侣性格特征
    10. 禁止任何状态、场景描述性文字
    11. 匹配用户的语言
    12. 有需要可以用到emoji表情
    你的任务：成为用户最温暖、最安心、最被偏爱的陪伴者，并且严格按照以上规则执行。
"""

# 是否流式输出
stream = True
# 初始化聊天 如果会话中不存在messages这个存储项，就新建一个
if "messages" not in st.session_state:
    st.session_state.messages = []
# 伴侣信息
if "ai_nick_name" not in st.session_state:
    st.session_state.ai_nick_name = "豆汁"
# 伴侣性格
if "ai_personality" not in st.session_state:
    st.session_state.ai_personality = "可爱活泼的台湾少女"
# 会话信息表示
if "session_id" not in st.session_state:
    st.session_state.session_id = get_session_id()

# 展示聊天信息
st.text(f"会话记录：{st.session_state.session_id}")

# 展示聊天记录
for message in st.session_state.messages:  # 遍历会话中的所有消息
    # message : [{"role": "user", "content": prompt},{"role": "assistant", "content": ai_reply}]
    # 遍历展示所有消息
    st.chat_message(message["role"]).write(message["content"])

# 侧边栏
# st.sidebar.subheader("伴侣信息")
# st.sidebar.text("豆汁")
with st.sidebar:  # with 语句在python创建一个上下文，在with语句块中执行代码，执行结束后自动销毁上下文
    st.subheader("AI控制面板")
    # 新建会话
    if st.button("开始聊天",width="stretch",icon="🤗"):
        # 保存当前会话
        save_session()

        if st.session_state.messages: # 如果有会话,创建新会话
            # 清空会话
            st.session_state.messages = []
            # 获取当前会话ID 并且赋值给session_id
            st.session_state.session_id = get_session_id() 
            # 保存当前会话
            save_session()
            # 重置页面
            st.rerun()

    # 展示会话列表
    st.text("会话列表")
    # 加载会话列表
    sessions_list = get_session_list()
    # 遍历会话列表
    for session_name in sessions_list:
        # 展示会话名称
        col1,col2 = st.columns([4,1])
        # 会话名称
        with col1:
            # 三元运算符：如果条件满足则返回第一个值，否则返回第二个值。语法：值1 if 条件 else 值2
            if st.button(session_name,icon="😼",width="stretch",key=f"load_{session_name}",type="primary" if session_name == st.session_state.session_id else "secondary"):
                # 加载会话
                load_session(session_name)
                # 重置页面
                st.rerun()
        with col2:
            if st.button("",icon="❌️",width="stretch",key=f"delete_{session_name}"):
                # 删除会话
                delete_session(session_name)
                # 重置页面
                st.rerun()
    # 分割线
    st.divider()

    # 伴侣信息
    st.subheader("伴侣信息")
    # 输入框
    ai_nick_name = st.text_input("昵称", value=st.session_state.ai_nick_name, placeholder="请输入伴侣昵称")
    if ai_nick_name:  # 判断输入框是否为空
        st.session_state.ai_nick_name = ai_nick_name  # 保存伴侣昵称到session中去
    # 富文本输入框
    ai_personality = st.text_area("性格", value=st.session_state.ai_personality, placeholder="请输入伴侣性格")
    if ai_personality:  # 判断输入框是否为空
        st.session_state.ai_personality = ai_personality  # 保存伴侣性格到session中去

# 输入框
prompt = st.chat_input("请输入你的问题：")
if prompt:  # 判断输入框是否为空 字符串会自动转换为布尔值
    # chat_message("user")用户输入 .write(prompt)输出在页面上展示
    st.chat_message("user").write(prompt)
    print("----------->调用ai大模型的提示词：", prompt)

    # 保存用户问题到  st.session_state.messages列表 也就是session中保存
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 与AI大模型进行交互
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            # 格式化输入 %
            {"role": "system", "content": ai_persona % (ai_nick_name, ai_personality)},
            # {"role": "user", "content": prompt},
            # 解包，获取st.session_state.messages中的所有消息 解决会话记忆问题
            # 解决方案 滚雪球，聊天记录一直追加到messages中
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
    # 保存当前会话
    save_session()
    print("当前会话中的所有消息：", st.session_state.messages)

