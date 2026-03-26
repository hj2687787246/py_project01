# 导入 OpenAI 客户端，用来调用兼容 OpenAI 协议的大模型接口。
import json

from openai import OpenAI

# 创建客户端对象。
# 这里使用的是阿里云百炼兼容 OpenAI 的接口地址。
# API Key 不在代码里写死，而是默认从环境变量中读取。
client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# schema 表示你希望模型从文本中抽取出来的字段。
schema = ['日期', '股票名称', '开盘价', '收盘价', '成交量']

# 示例数据。
# content 是原始金融文本。
# answers 是按照 schema 从文本中抽取出的结构化 JSON 结果。
examples_data = [
    {
        "content": "2025年3月18日，贵州茅台开盘价为1688.50元，收盘价报1712.00元，当日成交量为35210手。",
        "answers": {
            "日期": "2025年3月18日",
            "股票名称": "贵州茅台",
            "开盘价": "1688.50元",
            "收盘价": "1712.00元",
            "成交量": "35210手"
        }
    },
    {
        "content": "2025年4月2日，宁德时代早盘以196.30元开盘，最终收于201.85元，全天成交量达到128.6万手。",
        "answers": {
            "日期": "2025年4月2日",
            "股票名称": "宁德时代",
            "开盘价": "196.30元",
            "收盘价": "201.85元",
            "成交量": "128.6万手"
        }
    },
    {
        "content": "2025年5月12日，中国平安开盘价49.26元，收盘价48.91元，成交量为87.45万手。",
        "answers": {
            "日期": "2025年5月12日",
            "股票名称": "中国平安",
            "开盘价": "49.26元",
            "收盘价": "48.91元",
            "成交量": "87.45万手"
        }
    }
]

# 提问问题。
# 这里放待抽取的原始文本，后面你可以把它们逐条发给模型做信息抽取。
questions = [
    "2025年6月6日，招商银行开盘价为36.82元，收盘时报37.15元，全天成交量为56.3万手。",
    "2025年7月9日，比亚迪以285.00元开盘，收盘价升至292.48元，成交量达到102.7万手。",
    "2025年8月15日，中芯国际开盘价75.60元，收盘价78.12元，当日成交量为143.9万手。"
]

messages = [
    {"role":"system","content":f"你帮我完成信息抽取，我给你句子，你抽取{schema}信息，"
                               f"按JSON字符串输出，"
                               f"如果某些信息不存在，就用'原文未提及来代替'"}
]
for example in examples_data:
    messages.append(
        {"role": "user", "content": example["content"]}
    )
    messages.append(
        # json.dumps将python数据结构转为JSON字符串
        {"role": "assistant", "content": json.dumps(example["answers"],ensure_ascii=False)}
    )

for q in questions:
    response = client.chat.completions.create(
        model="qwen3-max",
        messages=messages + [{"role":"user","content": f"按照上述的示例，现在抽取这个句子的信息{q}"}]
    )

    # 打印原始文本，便于核对分类结果对应的是哪一条输入。
    print(f"文本：{q}")
    # 打印模型返回的分类结果。
    print(f"抽取：{response.choices[0].message.content}")
    # 打印分隔线，让多条结果看起来更清楚。
    print("-" * 50)