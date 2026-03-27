from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

model = ChatTongyi(model="qwen3-max")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "以我提供的已知参考资料为主，简介和专业的回答用户问题，参考资料：{context}"),
        ("user", "用户问题：{input}")
    ]
)

def print_prompt(prompt):
    print(prompt.to_string())
    print("=" * 20)
    return prompt

# 创建向量存储
vector_store = InMemoryVectorStore(embedding=DashScopeEmbeddings(model="text-embedding-v4"))

# 准备一下资料 向量库的数据
# add_texts 传入一个list[str]
# 存储向量
vector_store.add_texts(
    ["减肥就是要少吃多练", "在减脂期间吃东西很重要，清淡少油控制卡路里摄入并运动起来", "跑步是很好的运动哦"])

input_text = "怎么减肥？"


# result = vector_store.similarity_search(input_text, 2)
# 检索向量库 设置检索条数 返回一个Runnable接口的子类实例对象给到retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 2}) # langchain中向量存储对象，有一个方法：as_retriever，可以返回一个Runnable接口的子类实例对象


# 将向量数据库返回的list[Document对象]转换为字典
def format_func(docs: list[Document]):
    if not docs:
        return "无相关参考资料"

    formatted_str = "["
    for doc in docs:
        formatted_str += doc.page_content
    formatted_str += "]"

    return formatted_str


# chain
"""
retriever:
    - 输入：用户的提问    str
    - 输出：向量库的检索结果  list[Document]

prompt:
    - 输入：用户的提问 + 向量库的检索结果  dict
    - 输出：完整的提示词    PromptValue
"""

chain = (
        # invoke运行时，将input_text同时放入 RunnablePassthrough()  retriever 中去
        # retriever收到提示词，返回向量库检索到的结果，通过format_func方法转换为dict，
        # 将用户的提问 + 向量库的检索结果给到用户提示词，组成成完整的提示词PromptValue给到 model
        # 然后把model AIMessage 通过 StrOutputParser() 转换为字符串
        {"input": RunnablePassthrough(),"context": retriever | format_func} | prompt | print_prompt | model | StrOutputParser()
)
res = chain.invoke(input_text)
print(res)
