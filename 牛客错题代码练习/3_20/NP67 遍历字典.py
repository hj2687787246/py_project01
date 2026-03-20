# 描述
# 创建一个依次包含键-值对'<': 'less than'和'==': 'equal'的字典operators_dict，
# 先使用print()语句一行打印字符串'Here is the original dict:'，
# 再使用for循环遍历 已使用sorted()函数按升序进行临时排序的包含字典operators_dict的所有键的列表，
# 使用print()语句一行输出类似字符串'Operator < means greater than.'的语句；
#
# 对字典operators_dict增加键-值对'>': 'less greater'后，
# 输出一个换行，再使用print()语句一行打印字符串'The dict was changed to:'，
# 再次使用for循环遍历 已使用sorted()函数按升序进行临时排序的包含字典operators_dict的所有键的列表，
# 使用print()语句一行输出类似字符串'Operator < means greater than.'的语句，确认字典operators_dict确实新增了一对键-值对。
#
# 输入描述：
# 无
# 输出描述：
# 按题目描述进行输出即可（注意前后两个输出部分需以一个空行进行分隔）。
# 没错，解题时间太长
operators_dict= {'<': 'less than','==': 'equal'}
print('Here is the original dict:')
for i in sorted(operators_dict):
    print(f"Operator {i} means {operators_dict[i]} than.")
operators_dict['>'] = 'less greater'
print()
print('The dict was changed to:')
for i in sorted(operators_dict):
    print(f"Operator {i} means {operators_dict[i]} than.")