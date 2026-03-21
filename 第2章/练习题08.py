#1.写一个判断 BMI 等级的程序（偏瘦 < 18.5、正常 18.5-23.9、超重≥24）；
h = float(input("请输入身高："))
w = float(input("请输入体重："))
BMI = w / h ** 2
if BMI < 18.5:
    print("您偏瘦")
elif 18.5 <= BMI <= 23.9:
    print("您正常")
else:
    print("您超重")
#2.用 for 循环计算 1-50 的奇数和
total = 0
for i in range(1,51):
    if i % 2 == 1:
        total += i
print(total)
#3.定义一个混合类型列表，修改第 2 个元素，删除最后 1 个元素，遍历输出。
lst = [23,56,87,"ss","xx","hh",True]
print(lst)
lst[1] = lst[1] + 2
del lst[-1]
lst.append(False)
for item in lst:
    print(item)