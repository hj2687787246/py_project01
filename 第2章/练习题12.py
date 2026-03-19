# 1，定义一个函数，根据传入的分数，计算对应的分数等级并返回。
# 分数 >=90:A
# 分数>=75:B
# 分数>=60:C
# 分数く60:D
def funa(score):
    """
    计算分数等级
    :param score: 分数
    :return: 等级
    """
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    else:
        return "D"
print(funa(66))
# 2．定义一个函数，用于判断一个字符串是否是回文串，返回bool值。
# 把字符串反转，如果和原字符串相同，就是回文串。（如："level"，"radar"，"黄山落叶松叶落山黄")
def funb(str):
    """
    判断是否为回文串
    :param str: 字符串
    :return: 结果
    """
    #获取反转后的字符串 [::-1]为反转
    new_str = str[::-1]
    if new_str == str:
        return "是回文！"
    return "不是回文！"
print(funb("6667"))
# 3．定义一个函数：完成时间转换功能，将传入的秒转换为小时、分钟、秒。
def func(int_time):
    hour = int_time // 3600
    #获得剩下不足1小时的时间
    remaining_seconds = int_time % 3600
    minute = remaining_seconds // 60
    secs = remaining_seconds % 60
    #返回元组
    return hour, minute, secs
h,m,s = func(6666)
print(f"时间为：{h}:{m}:{s}")

# 4，定义一个函数：根据传入的三角形三个边的边长，判定三角形的类型（等边、等腰、普通，或者不能构成三角形）。
def fund(a,b,c):
    """
    判断三角形类型
    :param a: 边长
    :param b: 边长
    :param c: 边长
    :return: 结果
    """
    if a==b and b==c:
        return "等边三角形"
    elif a==b or b==c or c==b:
        return "等腰三角形"
    elif a+b > c and b+c >a and c+a >b:
        return "普通三角形"
    else:
        return "不能构成三角形"
print(fund(3,2,1))