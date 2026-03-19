#简易计算器
num1 = float(input("请输入数字1："))
num2 = float(input("请输入数字2："))
oper = input("请输入运算符+ - * /：")
match oper:
    case "+":
        print("运算结果为：",num1 + num2)
    case "-":
        print("运算结果为：",num1 - num2)
    case "*":
        print("运算结果为：",num1 * num2)
    case "/" if num2 != 0:#被除数不能为0
        print("运算结果为：",num1 / num2)
    case _:
        print("操作不支持")