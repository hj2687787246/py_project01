from langchain_community.llms.tongyi import Tongyi
from requests import exceptions as requests_exceptions

# 不用 qwen3-max，因为 qwen3-max 是聊天模型，qwen-max 是大语言模型。
model = Tongyi(model="qwen-max")

try:
    # 调用 invoke 向模型提问。
    res = model.invoke(input="你是谁，能做什么")
    print(res)
except requests_exceptions.RequestException as exc:
    print("调用通义千问失败：当前环境无法连接 dashscope.aliyuncs.com。")
    print(f"原始错误: {exc}")
