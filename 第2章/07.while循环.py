#打印十遍hello
i = 0
while i < 10:
    print("hello")
    i += 1
else:
    print("循环结束")
#while计算1-100之间所有偶数的累加之和
total = 0 #记录累加之和
i = 1 #循环开始数字

while i <= 100:
    if i % 2 == 0:
        total += i
    i += 1
print("计算完成，累加之和为：",total)