# 牛牛在门头沟大学学习，一学年过去了，需要根据他的成绩计算他的平均绩点，假如绩点与等级的对应关系如下表所示。
# 请根据输入的等级和学分数，计算牛牛的均绩（每门课学分乘上单门课绩点，求和后对学分求均值）。
# A 4.0 B 3.0 C 2.0 D 1.0 F 0
# 输入描述：
# 第一行输入等级，接下来的一行输入学分。
# 依次类推，遇到等级为False则结束输入。
# 输出描述：
# 均绩保留两位小数。
# 示例1
# 输入：
# A
# 3
# B
# 4
# C
# 2
# False
# 输出：
# 3.11
# 说明：
# (34.0+43.0+2*2.0)/(3+4+2)=3.11
# 错误原因：没想到
dict_num = {"A":4.0,"B":3.0,"C":2.0,"D":1.0,"F":0}
sum_list = []
sum_list1 = []
while True:
    str_in = input()
    if str_in == "False":
        break
    else:
        sum_list.append(float(input())*dict_num[str_in])
        sum_list1.append(dict_num[str_in])

print("%.2f" % (sum(sum_list)/sum(sum_list1)))



