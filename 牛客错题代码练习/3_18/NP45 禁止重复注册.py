# 描述
# 创建一个依次包含字符串'Niuniu'、'Niumei'、'GURR'和'LOLO'的列表current_users，
# 再创建一个依次包含字符串'GurR'、'Niu Ke Le'、'LoLo'和'Tuo Rui Chi'的列表new_users，
# 使用for循环遍历new_users，如果遍历到的新用户名在current_users中，
# 则使用print()语句一行输出类似字符串'The user name GurR has already been registered! Please change it and try again!'的语句，
# 否则使用print()语句一行输出类似字符串'Congratulations, the user name Niu Ke Le is available!'的语句。（注：用户名的比较不区分大小写）
# 输入描述：
# 无
# 输出描述：
# 按题目描述进行输出即可。
# The user name GurR has already been registered! Please change it and try again!
# Congratulations, the user name Niu Ke Le is available!
# The user name LoLo has already been registered! Please change it and try again!
# Congratulations, the user name Tuo Rui Chi is available!
# 错误原因：没看见原列表和新列表中名字大小写不一样

current_user = ['Niuniu','Niumei','GURR','LOLO']
new_current_user = []
for user in current_user:
    new_current_user.append(user.lower())
new_users = ['GurR','Niu Ke Le','LoLo','Tuo Rui Chi']
for user in new_users:
    if user.lower() in new_current_user:
        print(f"The user name {user} has already been registered! Please change it and try again!")
    else:
        print(f"Congratulations, the user name Tuo {user} is available!")

