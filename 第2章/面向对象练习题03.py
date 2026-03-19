# 采用面向对象的编程思想，开发一个购物车管理系统，实现商品信息的添加、修改、删除、查询功能。系统使用自定义对象存储商品数据，通过控制台菜单与用户交互。
# 0具体功能如下：
# 1．添加购物车：用户根据提示录入商品名称、以及该商品的价格、数量，保存该商品信息到购物车。
# 2．修改购物车：要求用户输入要修改的购物车商品名称，然后再提示输入该商品的价格、数量，输入完成后修改该商品信息。
# 3．删除购物车：要求用户输入要删除的购物车名称，根据名称删除购物车中的商品。
# 4．查询购物车：将购物车中的商品信息展示出来，格式为："商品名称：xxx，商品价格：xxx，商品数量：xxx"。
# 5．退出购物车

#创建商品类
class Goods:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f"商品名称：{self.name}，商品价格：{self.price}，商品数量：{self.quantity}"
    
#创建购物车类
class ShoppingCart:
    def __init__(self):
        self.cart = []
    
    #添加商品
    def add_gooods(self):
        name = input("请输入商品名称：")
        price = float(input("请输入商品价格："))
        quantity = int(input("请输入商品数量："))
        if price < 0 or quantity < 0:
            print("价格和数量不能为负数！")
            return
        if price == 0 or quantity == 0:
            print("价格和数量不能为零！")
            return
        if not name:
            print("商品名称不能为空！")
            return

        goods = Goods(name, price, quantity)
        self.cart.append(goods)
        print("添加成功！")
    
    #删除商品
    def delete_goods(self):
        name = input("请输入要删除的商品名称：")
        for goods in self.cart:
            if goods.name == name:
                self.cart.remove(goods)
                print("删除成功！")
                return
        print("没有找到该商品！")

    #修改商品
    def update_goods(self):
        name = input("请输入要修改的商品名称：")
        for goods in self.cart:
            if goods.name == name:
                price = float(input("请输入新的商品价格："))
                quantity = int(input("请输入新的商品数量："))
                if price < 0 or quantity < 0:
                    print("价格和数量不能为负数！")
                    return
                if price == 0 or quantity == 0:
                    print("价格和数量不能为零！")
                    return
                goods.price = price
                goods.quantity = quantity
                print("修改成功！")
                return
        print("没有找到该商品！")
    
    #查询购物车
    def query_cart(self):
        if not self.cart:
            print("购物车为空！")
            return
        for goods in self.cart:
            print(goods)
    
    #运行
    def run(self):
        while True:
            print("欢迎使用购物车管理系统！")
            print("1.添加商品")
            print("2.修改商品")
            print("3.删除商品")
            print("4.查询购物车")
            print("5.退出系统")
            choice = input("请输入您的选择：")
            try:
                match choice:
                    case 1:
                        self.add_gooods()
                    case 2:
                        self.update_goods()
                    case 3:
                        self.delete_goods()
                    case 4:
                        self.query_cart()
                    case 5:
                        print("bye~~")
                        break
                    case _:
                        print("指令错误，清重新输入")
            except ValueError as e:
                print("数字输入错误，请重新输入！错误信息：", e)
            except Exception as e:
                print("程序出现错误，请联系管理员！错误信息：",e)
            finally:
                print("资源释放")

#测试
if __name__ == '__main__':
    shopping_cart = ShoppingCart()
    shopping_cart.run()

    