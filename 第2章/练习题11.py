# 练习 1：把 “学生成绩统计” 从元组改成字典（10 分钟）
# 原元组写法：students = (("张三", 95, 98), ("李四", 88, 90))
# 改字典写法：students = {"张三": {"语文":95, "数学":98}, "李四": {"语文":88, "数学":90}}
# 👉 只做 2 件事：
# 写代码遍历字典，打印每个学生的语文成绩；

# （这个练习能吃透字典的「增删改 + 嵌套 + 遍历」，是购物车系统的核心用法）
#原元组
students_tuple = (("张三", 95, 98), ("李四", 88, 90))
#空字典
students_dict = {}
#遍历元组
for stu in students_tuple:
    #拆解元组
    name = stu[0]
    chinese = stu[1]
    math = stu[2]
    students_dict[name] = {"语文":chinese,"数学":math}
print(students_dict)

#打印每个同学的语文成绩
for key,value in students_dict.items():
    print(f"{key}的语文成绩为：{value["语文"]}")

# 给 “张三” 新增一个 “英语” 成绩（92），再删除 “李四” 的数学成绩。
students_dict["张三"]["英语"] = 92
print(students_dict)

del students_dict["李四"]["数学"]
print(students_dict)

# 给「王五」新增英语成绩 94；
students_dict["王五"]["英语"] = 94
print(students_dict)
# 打印「李四」的语文成绩；
print(students_dict["李四"]["语文"])
# 删除「张三」的数学成绩。
del students_dict["张三"]["数学"]
print(students_dict)
#练习 2：用集合给列表去重（5 分钟）
# 随便写一个重复的列表：nums = [1,2,2,3,3,3,4,5,5]
nums = [1,2,2,3,3,3,4,5,5]
nums_set = set(nums)
print(nums_set)
print(type(nums_set))
nums_list = list(nums_set)
print(nums_list)
print(type(nums_list))
