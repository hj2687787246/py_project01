# 需求1：将1-1000之间（含1000）所有的5的倍数的数字累加起来。
total = 0
for i in range(1,1001):
    if i % 5 == 0:
        total += i
print(total)
# 需求2：统计字符串"akiwksjakdiklowiqaamnvbamvaxnsjdsjkaaxkjd"字符串中有多少个a和k。
msg = "akiwksjakdiklowiqaamnvbamvaxnsjdsjkaaxkjd"
a = 0
k = 0
for i in msg:
    if i == "a":
        a += 1
    elif i == "k":
        k += 1
print(a,k)