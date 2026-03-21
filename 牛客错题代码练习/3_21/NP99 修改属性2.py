# 描述
# 请为牛客网的员工创建一个Employee类，包括属性有姓名（name）、（salary），并设置初始化。同时该类包括一个方法printclass，
# 用于输出类似'NiuNiu‘s salary is 4000, and his age is 22'的语句。
# 请根据输入的信息为Employee类创建一个实例e，调用hasattr方法检验实例有没有属性age，
# 如果存在属性age直接调用printclass输出，否则使用setattr函数为其添加属性age，并设置值为输入后，再调用printclass输出。
# 输入描述：
# 三行分别依次输入姓名name、工资salary、年龄age，其中第一行为字符串，后两行为整型数字。
# 输出描述：
# 第一行输出e有没有属性age，True或者False；
# 第二行输出printclass打印信息。
# 不熟练，不知道hasattr，hasattr这两个函数，他不写题目上我根本不知道，写在上面还是做对了


class Employee:
    def __init__(self,name,salary):
        self.name = name
        self.salary = salary

    def printclass(self):
        print(f'{self.name}‘s salary is {self.salary}, and his age is {age}')
name = input()
salary = int(input())
e = Employee(name,salary)
age = int(input())
print(hasattr(e, "age"))
if not hasattr(e, "age"):
    setattr(e,"age",age)
e.printclass()

