#if条件判断，如果密码正常，提示登录成功
# password = 123456
# is_password = input("请输入密码：")
# if int(is_password) == int(password):
#     print("登录成功")
# else:
#     print("密码错误")
# 需求：结合前面学习的输入输出及if条件判断的知识，完成B站登录功能的实现（正确账号和密码为18888888888/666888）
# username = 18888888888
# password = 666888
# in_username=int(input("请输入账号："))
# in_password=int(input("请输入密码："))
# if username == in_username and password == in_password:
#     print("密码输入正确，登录成功")
# else:
#     print("账号或密码输入错误，登录失败")

#案例1：根据用户输入的年份，判断这一年是闰年还是平年（非整百年份，且能被4整除的年份是闺年；整百年份（如1900、2000）必须被400整除才是闺年）
year = int(input("请输入年份："))
if (year %4 == 0 and year %100 != 0 )  or (year %400) == 0:
    print(f"{year}年是闰年！")
else:
    print(f"{year}年是平年！")

# 案例：三角形类型判断：根据输入的三个边的边长（正整数），判定是等边三角形、等腰三角形、普通三角形，还是不能构成三角形。
# 1，构成三角形的条件：两边之和大于第三边
# 2，三角形判定规则：
#   三个边都相等：等边三角形
#   两个边相等：等腰三角形
#   三个边都不相等：普通三角形

#1.接受输入的三个边
a = int(input("请输入第一条边长："))
b = int(input("请输入第二条边长："))
c = int(input("请输入第三条边长："))
#2.判断三角形类型
if a + b > c and a + c > b and b + c > a:
    if a==b and b==c and c==a:
        print("等边三角形")
    elif a==b or b==c or c==a:
        print("等腰三角形")
    else:
        print("普通三角形")
else:
    print(f"{a} {b} {c} 三条边不构成三角形")