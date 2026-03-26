from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# 聊天模型需要用字符串解析器来解析转换为文本
parser = StrOutputParser()
model = ChatTongyi(model="qwen3-max")
prompt = PromptTemplate.from_template(
    "我邻居姓：{lastname}，刚生了{gender}，请取名，仅告知我名字即可"
)

# 组装提示词放进了prompt，将prompt输出给model，model的输出结果给到parser转换成str，
# 然后把str输入到model里面，再把结果输入给parser转换为str字符串
chain = prompt | model | parser | model | parser

res = chain.invoke({"lastname": "王","gender": "儿子"})
print(res)