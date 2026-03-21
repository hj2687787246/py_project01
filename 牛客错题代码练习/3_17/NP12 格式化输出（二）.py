# 输入描述：
# 一行一个字符串表示名字。
# 输出描述：
# 请分别按全小写、全大写和首字母大写的方式对name进行格式化输出（注：每种格式独占一行）。
# 错误原因：不记得方法

name = input()
# 全小写
print(name.lower())
# 全大写
print(name.upper())
# 首字母大写
print(name.capitalize())
# 每个单词首字母大写
print(name.title())