# langchain_ollama
from langchain_ollama import OllamaLLM

model = OllamaLLM(model="deepseek-r1:1.5b")
# 调用 invoke 向模型提问。
res = model.invoke(input="你是谁，能做什么")
print(res)