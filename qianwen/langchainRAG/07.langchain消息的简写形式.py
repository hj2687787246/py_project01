from langchain_community.chat_models import ChatTongyi

model = ChatTongyi(model="qwen3-max")

# 准备消息列表
message = [
    ("system","你是一个流浪诗人"),
    ("human","写一首唐诗"),
    ("ai","离离原上草，一岁一枯荣。"),
    ("human","请按照你上一个回复的格式，再写一首唐诗")
]

res = model.stream(input=message)
for chunk in res:
    print(chunk.content,end="")