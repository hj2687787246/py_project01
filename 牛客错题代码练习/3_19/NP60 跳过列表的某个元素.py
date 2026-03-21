# 描述
# 牛客网在玩数数字游戏，员工一致认为13是一个“不详的数字”，请你使用for循环帮他们从1数到15，并使用continue语句跳过13。
# 输入描述：
# 无
# 输出描述：
# 输出数字1-15，跳过13，数字之间用空格间隔。
# 错误原因：忘记print中的end使用方法
my_list = [i for i in range(1,16)]
for my in my_list:
    if my == 13:
        continue
    print(my,end=" ")
