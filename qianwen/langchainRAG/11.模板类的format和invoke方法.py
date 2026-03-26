from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate, ChatPromptTemplate

"""
PromptTemplate -> StringPromptTemplate -> BasePromptTemplate -> RunnableSerializable -> Runnable
FewShotPromptTemplate -> StringPromptTemplate -> BasePromptTemplate  -> RunnableSerializable -> Runnable
ChatPromptTemplate -> BaseChatPromptTemplate -> BasePromptTemplate  -> RunnableSerializable -> Runnable
"""

template = PromptTemplate.from_template("我的邻居是：{lastname}, 最喜欢：{hobby}")

res = template.format(lastname= "张小明", hobby= "钓鱼")
print(res, type(res))

res2 = template.invoke({"lastname": "周轮胎", "hobby": "唱歌"})
print(res2, type(res2))
print(res2.to_string(),type(res2.to_string()))