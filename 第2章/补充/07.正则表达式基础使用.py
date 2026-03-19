import re

s ='python itheima python itheima Python itheima'

result = re.match("python",s)
print(result)
# 获取匹配的索引
print(result.span())
# 获取匹配的字符串
print(result.group())

result1 = re.search("Python",s)
print(result1)
# 获取匹配的索引
print(result1.span())
# 获取匹配的字符串
print(result1.group())

result2 = re.findall("python",s)
# 返回匹配的列表
print(result2)

