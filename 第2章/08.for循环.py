#遍历字符串
msg = input("请输入需要遍历的字符串：")
for s in msg: # s 遍历出来的元素 msg需要遍历的数据
    print(s)
else:
    print("遍历结束")
#计算1-100之间所有奇数之和
total = 0
msg = range(1,101)
for n in msg:
    if n % 2 == 1:
        total += n
print("遍历结束，奇数之和为：",total)
#简化
total = 0
for i in range(1,101,2):
    if i % 2 == 1:
        total += i
print("遍历结束，奇数之和为：",total)
#计算100-500之间所有3的倍数之和
total = 0
msg = range(100,501)
for n in msg:
    if n % 3 == 0:
        total += n
print("遍历结束，倍数之和为：", total)
#简化
total = 0
for i in range(100,501):
    if i % 3 == 0:
        total += i
print("遍历结束，倍数之和为：", total)