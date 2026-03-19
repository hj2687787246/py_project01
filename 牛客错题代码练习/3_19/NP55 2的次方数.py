# 描述
# 在Python中， * 代表乘法运算， ** 代表次方运算。
# 请创建一个空列表my_list，使用for循环、range()函数和append()函数令列表my_list包含底数2的 [1, 10] 次方，再使用一个 for 循环将这些次方数都打印出来（每个数字独占一行）。
# 输入描述：
# 无
# 输出描述：
# 按题目描述进行输出即可。
# 错误原因：不知道底数是啥
my_list = [i**2 for i in range(1,11)]
for my in my_list:
    print(my)