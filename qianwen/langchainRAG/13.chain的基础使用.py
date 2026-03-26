from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个流浪诗人，可以作诗"),
        MessagesPlaceholder("history"),
        ("human", "请再来一首唐诗")
    ]
)

history_data = [
    ("human", "你来写一个唐诗"),
    ("ai", "床前明月光，疑是地上霜。"),
    ("human", "好湿好湿，再来一首"),
    ("ai", "锄禾日当午，汗滴禾下土。"),
]
model = ChatTongyi(model="qwen3-max")

# 组成链，要求每一个组件都是Runnable接口的子类
chain = chat_prompt_template | model

# 通过链去调用invoke或stream
# res = chain.invoke({"history": history_data})
# print(res.content)

# 通过stream流式输出
for chunk in chain.stream({"history": history_data}):
    print(chunk.content, end="", flush=True)