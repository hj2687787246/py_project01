# # 定义类 ----不推荐
# class Car:
#     pass
#
# # 创建对象
# c1 = Car()
# # 动态的为对象添加属性
# c1.color = "red"
# c1.brand= "BAW"
# c1.name = "X5"
# c1.price = 500000
#
# print(c1)
# print(c1.color)
# #将对象中的所有属性以字典的形式输出出来
# print(c1.__dict__)

# # 定义类
# class Car:
#     # __init__ 方法是调用初始化的方法，会在对象创建时自动调用，可以在该方法中为对象设置对应的属性
#     # self: 是第一个参数，表示当前所创建出来的实力对象，类似java的this
#     def __init__(self, c_color,c_brand, c_name, c_price):
#         self.color = c_color
#         self.brand = c_brand
#         self.name = c_name
#         self.price = c_price
#         print("Car 类型的对象初始化完毕，对象属性已经添加完毕")
#
# #创建对象
# c1 = Car("红色","BWM","包吗","500000")
# print(c1.__dict__)
#
# c2 = Car("白色","E500","奔驰","800000")
# print(c2.__dict__)
# c2.price = 1000
# print(c2.price)
# print(c2.__dict__)

class Car:
    #类属性 所有容器共有的
    well = 4
    # __init__ 方法是调用初始化的方法，会在对象创建时自动调用，可以在该方法中为对象设置对应的属性
    # self: 是第一个参数，表示当前所创建出来的实力对象，类似java的this
    def __init__(self, c_color,c_brand, c_name, c_price):
        #实例属性
        self.color = c_color
        self.brand = c_brand
        self.name = c_name
        self.price = c_price
        print("Car 类型的对象初始化完毕，对象属性已经添加完毕")

    #定义实例方法
    def running(self):
        print(f"{self.brand}{self.name}正在高速行驶中~~")

    def total_cost(self,discount,rate):
        """
        计算提车总费用，包括车的价格，税费
        :param discount: 折扣
        :param rate: 税率
        :return: 总费用
        """
        total_cost = self.price * rate + self.price * discount
        return total_cost


# 测试
c1 = Car("红色","BMW","x5",800000)
c1.running()

total = c1.total_cost(discount=9.5,rate=1)
print(total)
