from langchain_community.embeddings import DashScopeEmbeddings
from langchain_ollama import OllamaEmbeddings

# 创建模型对象 不传model默认用的是 text-embeddings-v1
model = DashScopeEmbeddings()

# 不用invoke stream
# embed_query embed_documents
print(model.embed_query("我爱你"))
print(model.embed_documents(["我爱你","我恨你","我讨厌你","我喜欢你"]))

model = OllamaEmbeddings(model="deepseek-r1:1.5b")
print(model.embed_query("我爱你"))
print(model.embed_documents(["我爱你","我恨你","我讨厌你","我喜欢你"]))