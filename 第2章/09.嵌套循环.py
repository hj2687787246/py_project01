#打印一个长度为m，宽为n的长方形
m = int(input("请输入长方形的长度："))
n = int(input("请输入长方形的宽度："))
for j in range(n):# 控制行
    for i in range(m):# 控制列
        print("*",end=" ")# end:以什么结尾，不选择默认为换行/n
    print()# 没有end，默认换行/n
#打印一个乘法表
for i in range(1,10):# 外层循环控制行
    for j in range(1,i+1):# 内层循环控制列
        print(f"{j} x {i} = {j*i}",end="\t")# 以制表符结尾
    print()
# 根据输入直角边的边长，打印出等腰直角三角形
length = int(input("请输入直角边边长："))
for i in range(1,length+1):
    for j in range(1,i+1):
        print("*",end=" ")
    print()
# 根据输入数字，打印出对应的数字金字塔
length = int(input("请输入数字："))
for i in range(1,length+1):
    for j in range(1,i+1):
        print(j,end=" ")
    print()
# 打印出国际象棋盘
# 定义网格的行数和列数（可根据需要调整）
rows = 8    # 行数对应图片中的垂直高度
cols = 8    # 列数对应图片中的水平宽度

# 定义两种显示字符（□ 代表白色方块，■ 代表黑色方块，也可替换为其他字符）
white_block = "□"
black_block = "■"
# 循环打印每一行
for i in range(rows):
    # 初始化每行的字符串
    line = ""
    # 循环打印当前行的每一列
    for j in range(cols):
        # 核心逻辑：判断行列索引的奇偶性之和
        # 若 (行索引+列索引) 为偶数 → 黑方块；奇数 → 白方块（可反向调整）
        if (i + j) % 2 == 0:
            line += black_block + " "
        else:
            line += white_block + " "
    # 打印当前行
    print(line)