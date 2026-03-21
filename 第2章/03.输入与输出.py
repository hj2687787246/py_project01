#输入与输出
# name = input("Enter your name: ")
# age = input("Enter your age: ")
# print(name)
# print(age)

account_balance = 10000

password=  input("请输入密码:")
print(f"密码输入正常，您的密码为{password}")
amount = input("请输入取款金额:")
# 需要转换数据类型
print(f"您取出{amount}元，余额：{account_balance-int(amount)}")
