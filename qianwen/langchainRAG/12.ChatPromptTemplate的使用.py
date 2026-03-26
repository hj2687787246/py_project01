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
# stringPromptValue to_string()
prompt_text = chat_prompt_template.invoke({"history": history_data}).to_string()

model = ChatTongyi(model="qwen3-max")

res = model.invoke(prompt_text)

print(res.content, type(res))