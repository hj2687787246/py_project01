# 描述
# 请创建一个Coordinate类表示坐标系，属性有x和y表示横纵坐标，并为其创建初始化方法__init__。
# 请重载方法__str__为输出坐标'(x, y)'。
# 请重载方法__add__，更改Coordinate类的相加运算为横坐标与横坐标相加，纵坐标与纵坐标相加，返回结果也是Coordinate类。
# 现在输入两组横纵坐标x和y，请将其初始化为两个Coordinate类的实例c1和c2，并将坐标相加后输出结果。
# 输入描述：
# 第一行输入两个整数x1与y1，以空格间隔。
# 第二行输入两个整数x2与y2，以空格间隔。
# 输出描述：
# 输出相加后的坐标。

class Coordinate:
    def __init__(self,x:int,y:int):
        self.x = x
        self.y = y

    def __str__(self):

        return f"({self.x},{self.y})"

    def __add__(self, other):

        return self.x+other.x,self.y+other.y
x1,y1 = [int(i) for i in input().split()]
x2,y2 = [int(i) for i in input().split()]
c1 = Coordinate(x1,y1)
c2 = Coordinate(x2,y2)
print(c1+c2)