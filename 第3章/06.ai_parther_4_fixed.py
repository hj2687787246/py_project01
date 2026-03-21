import datetime
import json
import os
from pathlib import Path

import streamlit as st
from openai import OpenAI


print("重新执行此页面，渲染页面")

st.set_page_config(
    page_title="AI智能伙伴",
    page_icon="😠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

# 修改点：使用脚本所在目录构造会话目录，避免依赖启动时的工作目录。
BASE_DIR = Path(__file__).resolve().parent
SESSION_DIR = BASE_DIR / "session"


def save_session():
    if st.session_state.session_id:
        session_data = {
            "nick_name": st.session_state.ai_nick_name,
            "ai_personality": st.session_state.ai_personality,
            "session_id": st.session_state.session_id,
            "messages": st.session_state.messages,
        }
        SESSION_DIR.mkdir(exist_ok=True)
        with open(SESSION_DIR / f"{st.session_state.session_id}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)


def get_session_id():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_session_list():
    session_list = []
    if SESSION_DIR.exists():
        for file_path in SESSION_DIR.iterdir():
            if file_path.suffix == ".json":
                session_list.append(file_path.stem)
    session_list.sort(reverse=True)
    return session_list


def load_session(session_name):
    # 修改点：给默认返回值，避免文件不存在或加载失败时 message_data 未定义。
    message_data = None
    try:
        session_file = SESSION_DIR / f"{session_name}.json"
        if session_file.exists():
            with open(session_file, encoding="utf-8") as f:
                message_data = json.load(f)
                st.session_state.messages = message_data.get("messages", [])
                st.session_state.ai_nick_name = message_data.get("nick_name", st.session_state.ai_nick_name)
                st.session_state.ai_personality = message_data.get(
                    "ai_personality", st.session_state.ai_personality
                )
                st.session_state.session_id = message_data.get("session_id", session_name)
        else:
            st.error("会话文件不存在")
    except Exception as exc:
        st.error(f"会话数据加载失败：{exc}")

    return message_data


def delete_session(session_name):
    try:
        session_file = SESSION_DIR / f"{session_name}.json"
        if session_file.exists():
            session_file.unlink()
            st.success("会话数据删除成功")
            if session_name == st.session_state.session_id:
                st.session_state.messages = []
                st.session_state.session_id = get_session_id()
    except Exception as exc:
        st.error(f"会话数据删除失败：{exc}")


st.title("AI智能伙伴")
st.logo("🆘")

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

ai_persona = """
    你的名字是：{nick_name}
    你的性格是：{personality}

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

stream = True
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ai_nick_name" not in st.session_state:
    st.session_state.ai_nick_name = "豆汁"
if "ai_personality" not in st.session_state:
    st.session_state.ai_personality = "可爱活泼的台湾少女"
if "session_id" not in st.session_state:
    st.session_state.session_id = get_session_id()

st.text(f"会话记录：{st.session_state.session_id}")

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

with st.sidebar:
    st.subheader("AI控制面板")
    if st.button("开始聊天", width="stretch", icon="🤗"):
        # 修改点：仅在当前会话有消息时保存旧会话并切到新会话，避免生成无意义的空会话文件。
        if st.session_state.messages:
            save_session()
            st.session_state.messages = []
            st.session_state.session_id = get_session_id()
            st.rerun()

    st.text("会话列表")
    sessions_list = get_session_list()
    for session_name in sessions_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                session_name,
                icon="😼",
                width="stretch",
                key=f"load_{session_name}",
                type="primary" if session_name == st.session_state.session_id else "secondary",
            ):
                load_session(session_name)
                st.rerun()
        with col2:
            if st.button("", icon="❌️", width="stretch", key=f"delete_{session_name}"):
                delete_session(session_name)
                st.rerun()

    st.divider()
    st.subheader("伴侣信息")
    ai_nick_name = st.text_input(
        "昵称",
        value=st.session_state.ai_nick_name,
        placeholder="请输入伴侣昵称",
    )
    if ai_nick_name:
        st.session_state.ai_nick_name = ai_nick_name

    ai_personality = st.text_area(
        "性格",
        value=st.session_state.ai_personality,
        placeholder="请输入伴侣性格",
    )
    if ai_personality:
        st.session_state.ai_personality = ai_personality

prompt = st.chat_input("请输入你的问题：")
if prompt:
    st.chat_message("user").write(prompt)
    print("----------->调用ai大模型的提示词：", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        if not os.environ.get("DEEPSEEK_API_KEY"):
            raise ValueError("未检测到 DEEPSEEK_API_KEY 环境变量")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                # 修改点：改用 format，避免后续模板中出现 % 时触发格式化问题。
                {
                    "role": "system",
                    "content": ai_persona.format(
                        nick_name=st.session_state.ai_nick_name,
                        personality=st.session_state.ai_personality,
                    ),
                },
                *st.session_state.messages,
            ],
            stream=stream,
        )

        if stream:
            ai_reply = st.empty()
            reply_text = ""
            for chunk in response:
                # 修改点：流式内容可能为空，先判空再拼接，避免 TypeError。
                content = chunk.choices[0].delta.content or ""
                if not content:
                    continue
                reply_text += content
                ai_reply.chat_message("assistant").write(reply_text)

            if reply_text:
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
            else:
                st.warning("模型没有返回可显示的内容")
        else:
            ai_reply = response.choices[0].message.content
            print("<-----------ai大模型返回的结果：", ai_reply)
            st.chat_message("assistant").write(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        save_session()
        print("当前会话中的所有消息：", st.session_state.messages)
    except Exception as exc:
        # 修改点：统一兜底接口调用异常，避免页面直接中断。
        st.error(f"调用模型失败：{exc}")
