# 常量(不会发生变化的数据，常量的名称为全部大写)
PI = 3.14159
NAME = "海马boy"
AGE = 21

#函数
def log_sep1():
    print("+" * 30)
def log_sep2():
    print("-" * 30)
def log_sep3():
    print("*" * 30)
def log_sep4():
    print("/" * 30)
# __name__内置变量，表示当前模块的名字(直接运行当前代码，__name__的值为"__name__")，当该模块被导入时，__name__的值就是模块名
# 执行当前文件，则会运行以下代码，如果被当成模块导入，如下代码不执行
print(__name__)
if __name__ == '__main__':
    log_sep1()
