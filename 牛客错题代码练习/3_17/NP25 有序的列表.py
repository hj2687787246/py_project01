# 描述
# 创建一个依次包含字符串'P'、'y'、't'、'h'、'o'和'n'的列表my_list，先使用sorted函数对列表my_list进行临时排序，第一行输出排序后的完整列表，第二行输出原始的列表。再使用sort函数对列表my_list进行降序排序，第三行输出排序后完整的列表。
# 输入描述：
# 无
# 输出描述：
# 第一行输出临时排序后的列表；
# 第二行输出原始的列表；
# 第三行输出完成降序排序后的列表。
# 错误原因：不知道sorted原理
my_list = ['P','y','t','h','o','n']
# sorted临时列表，不对原列表修改
temp_List = sorted(my_list)
print(temp_List)
print(my_list)
my_list.sort(reverse=True)
print(my_list)
