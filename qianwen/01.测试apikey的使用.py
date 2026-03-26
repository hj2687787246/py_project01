from openai import OpenAI

client = OpenAI(
    # 如果没有配置环境变量，请替换为你的百炼 API Key：api_key="sk-xxx"
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

messages = [{"role": "user", "content": "你是谁？"}]

completion = client.chat.completions.create(
    model="qwen3-max",
    messages=messages,
    extra_body={"enable_thinking": False},
    stream=True,
)

for chunk in completion:
    delta = chunk.choices[0].delta
    if getattr(delta, "content", None):
        print(delta.content, end="", flush=True)
