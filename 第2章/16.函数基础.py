# # 函数定义
# def on_line():
#     print("helloworld")
# # 调用函数
# on_line()
#
# # 函数定义
# def rectangle_area(l,w):
#     #返回结果
#     return l*w
# print(rectangle_area(10,20))
#
# #函数定义
#
# def circle_area_len(r):
#     #添加函数说明
#     """
#     用于计算园的面积
#     :param r: 半径
#     :return: 周长，面积
#     """
#     #返回多个值封装到元组
#     return 3.14*r**2,3.14*r*r
# #查看说明文档
# help(circle_area_len)
#
# len_area = circle_area_len(10)
# print(type(len_area))
# print(len_area)
# #解包
# area,len = len_area
# print(area,len)

# 1．定义一个函数：根据传入的底和高计算三角形面积的函数（三角形面积=底*高/2）。
def funa(d,g):
    """
    计算三角形面积
    :param d: 底
    :param g: 高
    :return: 面积
    """
    return d*g/2
print(funa(3,4))

# 2。定义一个函数：计算传入的字符串中元音字母的个数（元音字母为aeiouAEIOU）。
def funb(str):
    # 定义初始化变量
    """
    统计存在元音字母的个数
    :param str:
    :return:
    """
    num = 0
    for i in str:
        if i in 'aeiouAEIOU':
            num += 1
    return num
print(funb('hello World HELLO WORLD aeiouAEIOU'))

# 3。定义一个函数：计算传入的班级学员高考成绩列表中成绩的最高分、最低分、平均分（保留1位小数），并返回。

def func(num_list):
    """
    计算学员最高分、最低分、平均分
    :param num_list: 成绩列表
    :return: 最高分、最低分、平均分(保留一位小数)
    """
    return max(num_list),min(num_list),round(sum(num_list) / len(num_list),1)

nums_list = [100,56,87,45,60,32]
#多个返回值返回元组类型
print(type(func(nums_list)))
#解包
max_num,min_num,avg_num, = func(nums_list)
print(f"最高分为：{max_num} 最低分为：{min_num}平均分为：{avg_num}")



