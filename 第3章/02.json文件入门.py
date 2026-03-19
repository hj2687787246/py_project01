#创建一个对象
import json

user = {
    "name": "张三",
    "age": 18,
    "gender": "男",
    "address": "北京",
    "phone": "12345678901"
}
#写入一个json文件
with open('./resource/data.json', 'w', encoding='utf-8') as f:
    # 将对象转换为json格式写入json文件
    # ensure_ascii 设置为False，可以输出中文 默认为True会将非ascii码转换成ascii码
    # indent 缩进
    json.dump(user, f,ensure_ascii= False, indent=2)

#读取一个json文件
with open('./resource/data.json', 'r', encoding='utf-8') as f:
    # 将json文件转换为对象
    user = json.load(f)
    # 打印对象
    print(user)
    # 打印对象类型
    print(type(user))