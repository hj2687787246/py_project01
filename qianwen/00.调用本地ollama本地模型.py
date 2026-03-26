import sys  # 导入 sys，用于在检测失败时退出程序。
from openai import OpenAI  # 导入 OpenAI 客户端，用 OpenAI 兼容方式调用 Ollama。
import requests  # 导入 requests，用来先检查本地 Ollama 服务和模型列表。

OLLAMA_BASE_URL = "http://localhost:11434"  # 这是 Ollama 本地服务的基础地址，默认端口是 11434。
MODEL_NAME = "deepseek-r1:1.5b"  # 这里指定你本地已经下载好的模型名称。

try:  # 先进入异常捕获，避免服务未启动时程序直接报一大串错误。
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)  # 请求 Ollama 的模型列表接口，确认服务是否正常。
    response.raise_for_status()  # 如果 HTTP 状态码不是 200，这里会直接抛出异常。
except requests.RequestException as exc:  # 捕获 requests 相关的网络异常。
    print("无法连接到本地 Ollama 服务，请先确认 Ollama 已启动。")  # 提示用户先启动 Ollama。
    print(f"详细错误：{exc}")  # 打印具体错误，方便排查端口或服务问题。
    sys.exit(1)  # 非正常退出程序，状态码 1 表示执行失败。

models_data = response.json()  # 把接口返回的 JSON 转成 Python 字典。
model_names = [model["name"] for model in models_data.get("models", [])]  # 从返回结果里提取所有模型名称。

if MODEL_NAME not in model_names:  # 如果目标模型不在已安装模型列表中，就给出明确提示。
    print(f"本地没有找到模型：{MODEL_NAME}")  # 提示缺少目标模型。
    print("你可以先在终端执行：")  # 告诉用户下一步该做什么。
    print(f"ollama pull {MODEL_NAME}")  # 给出对应的模型下载命令。
    print("当前已安装的模型有：")  # 输出当前本地已有模型，帮助核对名称是否写错。
    for name in model_names:  # 遍历所有已安装模型名称。
        print(f"- {name}")  # 每行打印一个模型名。
    sys.exit(1)  # 模型不存在时直接退出，避免后面继续调用失败。

client = OpenAI(  # 创建 OpenAI 客户端实例，但实际连到的是 Ollama 的兼容接口。
    base_url=f"{OLLAMA_BASE_URL}/v1",  # OpenAI SDK 访问 Ollama 时要加上 /v1 路径。
    api_key="ollama",  # Ollama 本地通常不会校验 key，这里填任意非空字符串即可。
)

completion = client.chat.completions.create(  # 发起一次聊天补全请求。
    model=MODEL_NAME,  # 指定要调用的本地模型。
    messages=[  # messages 是对话消息列表。
        {"role": "system", "content": "你是一个温柔可爱的 AI 助手。"},  # system 用来设定助手的人设和行为。
        {"role": "user", "content": "12个苹果要分给3个人，怎么分？"},  # user 是用户实际输入的问题。
    ],
    stream=True,  # 开启流式输出，这样模型生成一点就会返回一点。
)

for chunk in completion:  # 循环读取流式返回的每一个数据块。
    delta = chunk.choices[0].delta  # 从当前数据块里取出本次新增的文本片段。
    if getattr(delta, "content", None):  # 有些分片没有正文内容，所以先判断 content 是否存在。
        print(delta.content, end="", flush=True)  # 如果有内容就直接打印，并立即刷新到终端。

print()  # 最后补一个换行，避免命令行提示符紧贴在输出文本后面。
