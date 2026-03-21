# 描述
# Python的字典可以用来计数，让要被计数的元素作为key值，它出现的频次作为value值，只
# 要在遇到key值后更新它对应的value即可。现输入一个单词，使用字典统计该单词中各个字母出现的频次。
# 输入描述：
# 输入一个字符串表示单词，只有大小写字母。
# 输出描述：
# 直接输出统计频次的字典。
# 错误原因：忘记count使用方法

in_str = input()
str_dict = {}
for i in in_str:
    str_dict[i] = in_str.count(i)
print(str_dict)
