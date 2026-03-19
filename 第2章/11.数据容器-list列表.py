# #列表操作
# #定义
# msg = [56,54,87,123,45,87,"A","hello",True]
#
# #判断类型
# print(type(msg))
# print(msg[0],msg[-1])
#
# #修改
# msg[1]= msg[1] - 3
#
# #遍历
# for i in msg:
#     print(i)
#
# #删除
# del msg[-1]
# print(msg)

msg = ["A","B","C","D","E","F","G","H","I","J"]
#切片[开始：结尾：步长]
msg1 = msg[2:5:1]
print(type(msg1))
print(msg1)
#步长为2
msg2 = msg[::2]
print(msg2)
#反向打印
msg3 = msg[::-1]
print(msg3)

#定义一个列表scores = [85, 92, 78, 92, 65, 88]
# - 往尾部加 90，在第 3 个位置插 80；
# - 删除 65，统计 92 出现的次数；
# - 升序排序后反转，最终输出列表。
scores = [85,92,78,92,65,88]
#在列表末尾添加元素
scores.append(90)
#在指定下标插入元素
scores.insert(2,80)
#删除指定元素65
scores.remove(65)
#统计指定元素92
scores.count(92)
#升序
scores.sort()
#反转列表
scores.reverse()
print(scores)

#案例1，将用户输入的10个数字，存储到一个列表中，并将列表中的数字进行排序，
#输出其中的最小值、最大值和平均值。

# #1.定义列表
# num_list = []
# #2.用户输入数字，并保存
# for i in range(10):
#     num_list.append(float(input(f"请输入第{i + 1}个数字：")))
# print(num_list)
# #3.列表排序 reverse=True表示降序
# num_list.sort(reverse=True)
# #4.输出结果
# max_num = num_list[0]
# min_num = num_list[-1]
# avg_num = sum(num_list) / len(num_list)
# # :2f 表示保留两位小数点
# print(f"最大值为：{max_num}，最小值为{min_num}，平均值为{avg_num:.2f}")

# #案例2（简化）：合并两个列表中的元素，并对合并的结果进行去重处理（去除列表中的重复元素）
# num_list1 = [1,2,3,4,5,6,7,8,9]
# num_list2 = [10,11,12,5,14,9,16,17,6,19,20]
#
# #直接合并列表
# num_list = num_list1 + num_list2
# # 解包:将列表这类容器解开成一个个独立的元素
# # 组包：将多个值合并到一个容器
# # num_list = [*num_list1,num_list2]
# print("合并后的列表：",num_list)
#
# #去重
# #去重记录后的列表
# new_list = []
# for num in num_list:
#     #in 运算符判断元素是否存在于列表中 元素 in 列表
#     #not 运算符取反
#     if num not in new_list:
#         new_list.append(num)
# print("去重后的列表",new_list)

#案例3：生成1-20的平方列表
#列表推导式[要插入列表的数据 for i in 列表]
num_list = [i ** 2 for i in range(1,21)]
# for i in range(1,21):
#     num_list.append(i ** 2)
print(num_list)

#案例4：从一个数字列表中提取所有偶数，并计算其平方，组成一个新的列表
num_list1 = [1,56,48,789,54,32,65,47,12,65,87]
#列表推导式[要插入列表的数据 for i in 列表 条件表达式]
new_list = [i ** 2 for i in num_list1 if i % 2 == 0]
print(new_list)
