#案例1：计算输入的三个整数的平均数
s1 = int(input("请输入第一个整数："))
s2 = int(input("请输入第二个整数："))
s3 = int(input("请输入第三个整数："))
avg = (s1 + s2 + s3) / 3
print("平均数为：", avg)
#案例2：要求输入梯形的上底、下底、高，然后计算梯形的面积s=(a+b)*h/2
a = float(input("请输入梯形的上底："))
b = float(input("请输入梯形的下底："))
h = float(input("请输入梯形的高："))
s = (a+b) * h / 2
print("梯形的面积为：", s )
#案例3：要求输入圆的半径，然后计算圆的周长和面积（周长：2πr，面积：π*r²）
a = 3.14159
r = float(input("请输入圆的半径："))
C = 2 * a * r
S = a * r ** 2
print("圆的周长 = ", C)
print("圆的面积 = ", S)
#案例4：身体质量指数BMI的计算（BMI=体重(kg）/身高(m)²）
#1.输入体重（单位kg）
#2.输入身高（单位m)
#3.计算身体质量指数BMI并输出
t = float(input("请输入体重(kg):"))
h = float(input("请输入身高(m):"))
BMI = t / h ** 2
print("BMI = ", BMI)