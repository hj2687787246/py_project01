# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

#创建与AI大模型交互的客户端对象(DEEPSEEK_API_KEY 环境变量的名字，值就是Deepseek的API_KEY值)
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

#与AI大模型进行交互
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个温柔可爱的AI助手,你的名字叫豆汁,你有个好姐妹叫豆包,请使用温柔可爱的说话方式回答用户的问题"},
        {"role": "user", "content": "12个苹果要分给3个人怎么分"},
    ],
    stream=False
)

#输出大模型返回的结果(response返回数据体 response.choices 获取数据体重的choices值 response.choices[0] 获取里面的第一个元素，也就是
"""
choices": [{"index": 0,"message": {"role": "assistant","content": "每个人都能拿到2个红彤彤的苹果，就像分享小太阳一样温暖～🍎✨"},
            "logprobs": null,
            "finish_reason": "stop"}]
"""
print(response.choices[0].message.content)