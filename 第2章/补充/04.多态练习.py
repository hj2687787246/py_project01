# 定义一个抽象类，作为顶层设计类
class Animal:
    def eat(self):
        # 吃
        pass
    def drink(self):
        # 喝
        pass
    def run(self):
        # 跑
        pass
    def sleep(self):
        # 睡觉
        pass

class Cat(Animal):
    def eat(self):
        print("吃猫饭")

    def drink(self):
        print("猫喝水")

    def run(self):
        print("猫跑步")

    def sleep(self):
        print("猫睡觉")

class Dog(Animal):
    def eat(self):
        print("吃狗粮")

    def drink(self):
        print("狗喝水")

    def run(self):
        print("狗跑步")

    def sleep(self):
        print("狗睡觉")

def eat(al:Animal):
    al.eat()
def drink(al:Animal):
    al.drink()
def run(al:Animal):
    al.run()
def sleep(al:Animal):
    al.sleep()

# 创建对象
cat = Cat()
dog = Dog()
# 调用方法 传入对象进行调用 实现多态
eat(cat)
drink(dog)

