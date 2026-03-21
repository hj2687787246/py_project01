#1．需求1：根据用户输入的数字，判断该数字是奇数还是偶数。
num = int(input("请输入数字："))
if num % 2 == 0:
    print(f"{num}为偶数")
else:
    print(f"{num}为奇数")
#2，需求2：根据用户输入的年龄，判断该用户是否已经成年（>=18，成年；否则，未成年）。
age = int(input("请输入年龄:"))
if age >= 18:
    print("成年")
else:
    print("未成年")
#3.需求3：根据用户输入的数字，判断该数字是正数还是负数（不考虑0）。
num = float(input("请输入数字:"))
if num > 0:
    print(f"{num}为正数")
else:
    print(f"{num}为负数")
#4。需求4：根据用户输入的考试分数，判断该分数是否及格了（大于等于60就是及格了）。
num = int(input("请输入分数:"))
if num >= 60:
    print("及格")
else:
    print("不及格")

#if...elif...else案例：根据用户输入的数字，判断数字是正数，还是负数，还是0
num = int(input("请输入数字："))
if num > 0:
    print("正数")
elif num < 0:
    print("负数")
else:
    print("0")

# 根据输入用户名、密码进行登录系统。
# 用户名、密码为admin/666888或root/547527或zhangsan/123456，则输出登录成功
# 否则就提示用户名或密码错误
username = input("请输入用户名：")
password = int(input("请输入密码："))
if username == "admin" and password == 666888:
    print("登录成功！")
elif username == "root" and password == 547527:
    print("登录成功！")
elif username == "zhangsan" and password == 123456:
    print("登录成功！")
else:
    print("账号或密码错误，登录失败！")

# 1，根据输入的考试成绩，判断成绩等级。大于等于85分为优秀，60-85分为及格，否则就是不及格
score = float(input("请输入考试成绩："))
if score >= 85:
    print("优秀")
elif 60 <= score <= 85:
    print("及格")
else:
    print("不及格")
# 2，购物折扣计算：根据输入的购物车的商品总额，以及如下的折扣规则，计算实际应付的金额。
# 金额>=500：8折 300<= 金额く500：9折100<= 金额く300：95折 金额く100：无折扣
sum= float(input("输入购物车商品总额："))
if sum >= 500:
    print(f"需花费：{sum*0.8}元")
elif sum >= 300:
    print(f"需花费：{sum*0.9}元")
elif 300 > sum > 100:
    print(f"需花费：{sum*0.95}元")
else:
    print(f"需花费：{sum}元")