from langchain_community.llms.tongyi import Tongyi
from langchain_ollama import OllamaLLM

# model = OllamaLLM(model="deepseek-r1:1.5b")
# res = model.stream(input="你是谁，能做什么")
# for chunk in res:
#     print(chunk, end="", flush=True)

model = Tongyi(model="qwen-max")
# 通过stream方法获得流式输出
res = model.stream(input="你是谁，能做什么")

for chunk in res:
    print(chunk,end="", flush=True)
