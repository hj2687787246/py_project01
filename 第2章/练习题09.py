# ===================== 题目1：合并列表+去重+排序 =====================
list1 = [5, 2, 8, 2, 9, 1]
list2 = [9, 3, 8, 7, 5, 10]
list3 = [1, 4, 6, 7, 9, 10, 11]
list4 = [11, 12, 3, 4, 6, 8]

# 请在这里编写题目1的代码
# 步骤提示：1.合并列表 2.去重 3.排序 4.输出
#1.合并列表
list5 = [*list1, *list2, *list3, *list4]
#2.去重
new_list = []
for i in list5:
# in 判断元素是否存在列表 not 取反
    if i not in new_list:
        new_list.append(i)
#3.排序
new_list.sort()
#4.输出
print(new_list)
# ===================== 题目2：筛选整除3/5+平方 =====================
num_list = [1, 3, 5, 7, 9, 10, 12, 14, 15, -3, -5, 0, 17, 20, 22]

# 请在这里编写题目2的代码
# 步骤提示：1.遍历列表 2.筛选能被3或5整除的元素 3.计算平方 4.组成新列表 5.输出
# 列表推导式 [要插入的数据 for i in 条件表达式]
new_list1 = [i ** 2 for i in num_list if i % 3 == 0 or i % 5 == 0]
# for i in num_list:
#     if i % 3 == 0 or i % 5 == 0:
#         new_list1.append(i ** 2)
print(new_list1)

# ===================== 题目3：提取正数 =====================
mix_num_list = [-5, 8, 0, -3.5, 9.2, 10, -1.8, 0.5, -100, 7]

# 请在这里编写题目3的代码
# 步骤提示：1.遍历列表 2.筛选>0的元素 3.组成新列表 4.输出

new_list2 = [i for i in mix_num_list if i >0]
# for i in mix_num_list:
#     if i > 0:
#         new_list2.append(i)
print(new_list2)