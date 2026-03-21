# # 元组基本操作 - tuple 元素可以重复，有序，不可修改
# # 定义 ()
# t = (1,6,87,841,31,54,32)
# print(type(t))
#
# print(t[0])
# print(t[-1])
#
# #切片
#
# print(t[2:5])
# print(t[::-1])
#
# #定义单个元组需要在元素后加，号
# s = (100)
# print(type(s))
#
# s = (100,)
# print(type(s))

students = (
    ("张三", 95, 98, 92),
    ("李四", 88, 90, 85),
    ("王五", 92, 96, 94),
    ("赵六", 85, 82, 88),
    ("钱七", 98, 95, 96),
    ("孙八", 78, 80, 76),
    ("周九", 91, 89, 93),
    ("吴十", 89, 92, 90)
)
print(students)
# 1，计算每个学生的总分、各科平均分，然后一并输出出来。
# for i in students:
#     total = i[1] + i[2] + i[3]
#     avg = total / 3
#     # :.1f 表示保留一位小数点的浮点类型
#     print(f"{i[0]}的总分为：{total}\t平均分为：{avg:.1f}")
#方法2：
for name,chinese,math,english in students:
    total = chinese + math + english
    avg = total / 3
    # :.1f 表示保留一位小数点的浮点类型
    print(f"{name}的总分为：{total}\t平均分为：{avg:.1f}")
# 2．统计各科成绩的最低分、最高分、平均分，并输出。
# 获取各科成绩的列表
chinese_list = [i[1] for i in students]
math_list = [i[2] for i in students]
english_list = [i[3] for i in students]
print(f"语文成绩的最低分为：{min(chinese_list)}\t最高分为：{max(chinese_list)}\t平均分为：{sum(chinese_list) / len(chinese_list):.1f}\t")
print(f"数学成绩的最低分为：{min(math_list)}\t最高分为：{max(math_list)}\t平均分为：{sum(math_list) / len(math_list):.1f}\t")
print(f"英语成绩的最低分为：{min(english_list)}\t最高分为：{max(english_list)}\t平均分为：{sum(english_list) / len(english_list):.1f}\t")
# 3.查找成绩优秀（平均分大于90）的学生，并输出。
superb = []
for name,chinese,math,english in students:
    total = chinese + math + english
    avg = total / 3
    if avg > 90:
        superb.append(name)
        superb.append(avg)
print(f"平均分大于90的学生分别是：",superb)
