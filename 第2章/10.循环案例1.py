# 案例1：根据输入的用户名密码执行登录操作，具体要求如下：
# 1.正确的用户名和密码为admin/666888、zhangsan/123456、taoge/888666
# 2，输入用户名和密码进行登录，直到登录成功，程序结束运行；如果登录失败，则继续输入用户名和密码进行登录
# 3．输入的用户名和密码不能为空！
# 4，登录成功：输出"登录成功，进入B站首页~"
# 5，登录失败：输出“用户名或密码错误，请重新输入！"

#1.输入账号密码

#2.循环条件
while True:
    username = input("请输入账号：")
    password = input("请输入密码：")
    if username =="" or password =="":
        print("账号和密码都不能为空！")
        continue #终止当前循环，进入下次循环
    elif username == "admin" and password == "666888":
        print("登录成功，进入b站首页~")
        break #结束循环
    elif username == "zhangsan" and password == "123456":
        print("登录成功，进入b站首页~")
        break
    elif username == "taoge" and password == "888666":
        print("登录成功，进入b站首页~")
        break
    else:
        print("账号或密码错误，请重新输入！")