# NP73 查字典
# 描述
# 正在学习英语的牛妹笔记本上准备了这样一个字典：
# {'a': ['apple', 'abandon', 'ant'], 'b': ['banana', 'bee', 'become'], 'c': ['cat', 'come'], 'd': 'down'}。
# 请你创建这样一个字典，对于牛妹输入的字母，查询有哪些单词？
# 输入描述：
# 输入一个字母，必定在上述字典中。
# 输出描述：
# 同一行中依次输出每个单词，单词之间以空格间隔。
# 错误原因：牛客网不支持mathc - case
str_dict = {'a': ['apple', 'abandon', 'ant'], 'b': ['banana', 'bee', 'become'], 'c': ['cat', 'come'], 'd': 'down'}
in_str = input()
for i in str_dict:
    if in_str == i:
        for j in str_dict[i]:
            print(j,end=" ")

