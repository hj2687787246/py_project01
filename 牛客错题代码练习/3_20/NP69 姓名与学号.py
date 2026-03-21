# 描述
# 创建一个依次包含键-值对{'name': 'Niuniu'和'Student ID': 1}的字典my_dict_1，
# 创建一个依次包含键-值对{'name': 'Niumei'和'Student ID': 2}的字典my_dict_2，
# 创建一个依次包含键-值对{'name': 'Niu Ke Le'和'Student ID': 3}的字典my_dict_3，
# 创建一个空列表dict_list，使用append()方法依次将字典my_dict_1、my_dict_2和my_dict_3添加到dict_list里，
# 使用for循环遍历dict_list，对于遍历到的字典，使用print()语句一行输出类似字符串"Niuniu's student id is 1."的语句以打印对应字典中的内容。
# 输入描述：
# 无
# 输出描述：
# 按题目描述进行输出即可。Niuniu's student id is 1.
# Niumei's student id is 2.
# Niu Ke Le's student id is 3.
# 多次参考提交结果，才写出来，中间想把列表转成字典，实际上列表遍历出的每个元素都是一个字典，使用key就能获取字典里面的value了
my_dict1 = {'name': 'Niuniu','Student ID': 1}
my_dict2 = {'name': 'Niumei','Student ID': 2}
my_dict3 = {'name': 'Niu Ke Le','Student ID': 3}
dict_list = [my_dict1,my_dict2,my_dict3]
for d in dict_list:
    print(f"{d['name']}'s student id is {d['Student ID']}.")