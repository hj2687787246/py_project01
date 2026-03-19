
class __IPhone:
    IT = "QF"
    def __init__(self,brand:str,price:float):
        self.brand = brand
        self.price = price
    def call(self):
        print("打电话")
    def play(self):
        print("玩游戏")

class IPhoneX(__IPhone):
    # 继承父类 创建对象的时候需要传入参数
    def __init__(self, color, brand, price):
        super().__init__(brand, price)
        self.color = color

    def call(self):
        print(f"使用{self.brand}的电话")
    def play(self):
        print(f"使用{self.color}{self.brand}的玩游戏")
    def photo(self):
        print(f"使用{self.color}{self.brand}的拍照")

class IPhoneR(IPhoneX):
    IT = "HM"
    def photo(self):
        self.color = "黑色"
        print(f"父类的{super().IT}")
        print(f"子类的{self.IT}")
        print(f"使用{self.color}{self.brand}的拍照")

iPhoneR = IPhoneR("蓝色",  "好吃",8888)
iPhoneR.call()
iPhoneR.play()
iPhoneR.photo()
print(iPhoneR.IT)
