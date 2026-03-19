# # 字符串 基本操作 ---->不可变的（无法修改的） 有序的 可迭代的
# s = "hello world"
#
# print(s[6])
#
# for i in s:
#     print(i)
#
# #切片
# print(s[-1:-7:-1])

# # 邮箱格式验证：用户输入一个邮箱，验证邮箱格式是否正确（包含一个@和至少一个。），如果输入正确，输出"邮箱格式正确"，否则输出"邮箱格式错误"。
# #1.用户输入邮箱
# email = input("请输入邮箱号：")
# #2.判断格式是否正确
# # if email.find("@") != -1 and email.count(".") >= 1:
# # in判断是否包含
# if email.find("@") != -1 and "." in email:
#     print("邮箱格式正确")
# else:
#     print("邮箱格式错误")

# 输入一个字符串，判断该字符串是否是回文（两边对称）。
# 黄山落叶松叶落山黄
# 上海自来水来自海上
#核心为原文本反转后是否与原文本相同
str_put = input("请输入一个字符串：")
new_str = str_put
if new_str == str_put[::-1]:
    print("是回文！")
else:
    print("不是回文！")

# 将用户输入的 10 个字符串，反转后全部转换为大写，然后记录在列表中，最后将列表内容，遍历输出出来。
str_num = input("请输入一个字符串：")
# ::-1直接反转
new_str_num = str_num[::-1]
#list 直接转换成列表，使用split()输入的文本如果没有分割会变成一个整体
list_str = list(new_str_num.upper())
print(list_str)
print(type(list_str))
for i in list_str:
    print(i)