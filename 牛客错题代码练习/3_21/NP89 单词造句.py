# 描述
# 牛牛在和牛妹做一个游戏，牛牛给定了牛妹一些单词字符串，他想让牛妹把这些单词拼接成以空格间隔开的句子，很可惜牛妹Python没有学好，你能使用join函数帮帮她吗？
# 输入描述：
# 多行输入多个字符串，每行一个单词，最后一个输入为0时结束。
# 输出描述：
# 输出多个单词组成的句子。
name_list = []
while True:
    name = input()
    if name == "0":
        break
    name_list.append(name)
print(" ".join(name_list))