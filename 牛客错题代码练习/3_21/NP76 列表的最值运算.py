# 描述
# 牛牛给了牛妹一个一串无规则的数字，牛妹将其转换成列表后，使用max和min函数快速的找到了这些数字的最值，你能用Python代码实现一下吗？
# 输入描述：
# 输入一行多个整数，数字之间以空格间隔。
# 输出描述：
# 输出这些数字的zui zhi
# 没错，只是忘记列表推导式

int_list = [int(i) for i in input().split()]
print(min(int_list))
print(max(int_list))