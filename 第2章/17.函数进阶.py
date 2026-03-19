# 函数 -默认参数
def reg_str(name,age,gender="男",city="四川"):
    print(f"登录成功，姓名：{name}年龄：{age}性别：{gender}城市：{city}")
    return {"name":name,"age":age,"gender":gender,"city":city}

print(reg_str("何杰",18))
print(reg_str("李梦",17,"女","云南"))

# 不定长参数 - 基于位置
def calc_data(*args):
    """
    :param args: 不定长参数 基于位置 计算数据
    :return: 最小值、最大值、平均值
    """
    min_data = min(args)
    max_data = max(args)
    avg_data = sum(args)/len(args)

    return min_data,max_data,avg_data
print(calc_data(1,6,8,7,9,6,4))

def calc_data(*args,**kwargs):
    """

    :param args: 不定长参数 基于位置 计算数据
    :param kwargs: 不定长参数 基于关键字 计算数据
    :return: 最小值、最大值、平均值
    """
    min_data = min(args)
    max_data = max(args)
    avg_data = sum(args)/len(args)
    #如果round参数不为空，则将avg_data保留round小数
    if kwargs.get("round") is not None:
        avg_data = round(avg_data,kwargs.get("round"))
    if kwargs.get("print") :
        print(f"最小值为：{min_data}最大值为：{max_data}平均值为：{avg_data}")
    #基于位置参数返回元组
    print(args)
    print(type(args))
    #基于关键字参数返回的是字典
    print(kwargs)
    print(type(kwargs))
    return min_data,max_data,avg_data
print(calc_data(1,6,8,7,9,6,4,round=2))
print(calc_data(1,6,8,7,9,6,4,round=3,print=True))