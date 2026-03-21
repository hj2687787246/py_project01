# #一、基础题（变量 / 输入输出 / 数据类型）
# # 定义 3 个变量：name（值为你的名字，字符串）、age（值为你的年龄，整数）、height（值为你的身高，比如 175.5，浮点数），然后打印：「我的名字是 XXX，年龄 XX 岁，身高 XX.X 厘米」。
# name = "何杰"
# age = 26
# height = 1.69
# print(f"我的名字是：{name},今年{age}岁，身高{height}米")
# # 写代码实现：接收用户输入的一个数字，把它转换成整数类型后，打印这个数字的 2 倍。（比如输入 5，输出 10）
# num = int(input("请输入一个整数："))
# print(num * 2)
# # 定义一个布尔变量 is_student（值为 True/False），用 if 判断：如果是 True，打印「我是学生」；否则打印「我不是学生」。
# is_student = True
# if is_student:
#     print("我是学生")
# else:
#     print("我不是学生")
# # 二、进阶题（条件判断 / 循环）
# # 写代码：接收用户输入的一个成绩（0-100），用 if-elif-else 判断等级：
# # 90 及以上：打印「优秀」
# # 80-89：打印「良好」
# # 60-79：打印「及格」
# # 60 以下：打印「不及格」
# num = int(input("请输入成绩："))
# if num >=90:
#     print("优秀")
# elif num >= 80:
#     print("良好")
# elif num >= 60:
#     print("及格")
# else:
#     print("不及格")
# # 用 for 循环打印 1 到 10 的所有数字（包含 10）。
# for i in range(1,11):
#     print(i)
# # 用 while 循环计算 1 到 100 的累加和（1+2+3+…+100），并打印结果。
# # 定义
# total = 0 #记录累加之和
# i = 1 #循环开始数字
# while i <=100:
#     total += i
#     i += 1
# print(total)
# # 三、综合题（列表 / 字典）
# # 定义一个列表 fruits = ["苹果", "香蕉", "橙子"]，完成：
# fruits = ["苹果", "香蕉", "橙子"]
# # 往列表末尾添加「葡萄」
# fruits.append("葡萄")
# # 修改第二个元素为「草莓」
# fruits[1] = "草莓"
# # 遍历列表，打印每个水果的名字。
# for i in fruits:
#     print(i)
#
# # 定义一个字典 student = {"name": "张三", "age": 20, "major": "计算机"}，完成：
# student = {"name":"张三","age":20,"major":"计算机"}
# # 打印学生的专业
# print(student["major"])
# # 往字典里添加键值对「score」: 85
# student["score"] = 85
# # 遍历字典，打印所有的键和值（格式：键：值）。
# for k,y in student.items():
#     print(f"{k}: {y}")

# 写 while 循环计算「2+4+6+…+20」的和（偶数累加），刻意提醒自己先定义初始变量：
# 定义初始变量
total,i = 0,1
while i <= 20:
    #条件为偶数
    if i % 2 == 0:
        total+=i
    i+=1
print(total)
# 初始字典
book = {"title":"Python入门", "price":29.9}
#新增
book["name"] = "小明"
#修改
book["price"] = 30.1
#删除
del book["title"]
print(book)
#删除之后返回值
# de = book.pop("title")
# print(de)
#遍历 打印所有key
for key in book.keys():
    print(key)
#打印所有value
for value in book.values():
    print(value)
#打印所有键值对
for key,value in book.items():
    print(f"{key}: {value}")
