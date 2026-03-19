# 手机类
class Phone:
    # 提供私有属性变量
    __is_5g_enable = True

    def __init__(self,brand,name,price):
        self.brand = brand
        self.name = name
        self.price = price

    def __check_5g_enable(self):
        if self.__is_5g_enable:
            print(self.brand,self.price,self.name)
            print("5G已启用")
        else:
            print("5G未启用")

    def call_by_5g(self):
        self.__check_5g_enable()
# 创建手机对象
phone = Phone("嘻嘻","哈哈",9999)
phone.call_by_5g()