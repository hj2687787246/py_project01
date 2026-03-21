# # 字典 -- key不能重复（如果重复，后面的值会覆盖前面的值）、key必须是不可变类型（str、int、float、tuple）、key是可修改的
# # 定义字典
#
# dict1 = {"name":"何杰","age":28,"iphone":7,"id":4396,"email":"1814518742"}
# print(dict1)
# print(type(dict1))
#
# name = dict1.get("name")
# print(name)
#
# print(dict1)
# print(type(dict1))
#
# # 访问字典 添加
# dict1["age"] = 11
# dict1["name"] = "轻轻松松"
# dict1["iphone"] = "17628432244"
# print(dict1)
#
# # 删除 pop会返回删除key对应的value
# d = dict1.pop("email")
# print(d)
#
# del dict1["id"]
# print(dict1)
#
# # 修改 存在添加的key就改为更新修改
# dict1["name"] = "何杰"
# print(dict1)
#
# #查询
# print(dict1["name"]) #获取对应key的value
# print(dict1.get("name")) #获取对应key的value
# print(dict1.keys()) #获取所有key
# print(dict1.values()) #获取所有value
# print(dict1.items()) #获取所有键值对
#
# #遍历
#
# # 通过下标获取键值对
# for item in dict1.items():
#     print(item[0],item[1])
#
# # 解包方式
# for key,value in dict1.items():
#     print(key,value)
#
# # k 为遍历的key值 dict[k]为value
# for k in dict1.keys():
#     print(k,dict1[k])
#
#
#
# 1，添加购物车：用户根据提示录入商品名称、以及该商品的价格、数量，保存该商品信息到购物车。
# 2，修改购物车：要求用户输入要修改的购物车商品名称，然后再提示输入该商品的价格、数量，输入完成后修改该商品信息。
# 3．删除购物车：要求用户输入要删除的购物车名称，根据名称删除购物车中的商品。
# 4．查询购物车：将购物车中的商品信息展示出来，格式为："商品名称：xX×，商品价格：×××，商品数量：x××"。
# 5．退出购物车
menu= """
**************************************
*             1.添加购物车             *
*             2.修改购物车             *
*             3.删除购物车             *
*             4.查询购物车             *
*             5.退出购物车             *
**************************************
"""
print("欢迎进入xx商场~")
shopping_cart = {}
while True:
    print(menu)
    choice = int(input("请输入操作："))
    match choice:
        #添加
        case 1:
            goods_name = input("请输入商品名称：")
            if goods_name in shopping_cart:
                print("购物车已存在该商品！")
                continue
            goods_price = float(input("请输入商品价格："))
            goods_num = int(input("请输入商品数量："))
            #添加商品
            shopping_cart[goods_name] = {"price":goods_price,"num":goods_num}
            print(f"商品{goods_name}添加成功！")
        #修改
        case 2:
            goods_name = input("请输入商品名称：")
            if goods_name not in shopping_cart:
                print("购物车不存在该商品！")
                continue
            goods_price = float(input("请输入商品价格："))
            goods_num = int(input("请输入商品数量："))
            #修改商品
            shopping_cart[goods_name] = {"price":goods_price,"num":goods_num}
            print(f"商品{goods_name}修改成功！")
        #删除
        case 3:
            goods_name = input("请输入商品名称：")
            if goods_name not in shopping_cart:
                print("购物车不存在该商品！")
                continue
            #删除商品
            del shopping_cart[goods_name]
            print(f"商品{goods_name}删除成功！")
        #查询
        case 4:
            #商品名称为key，所以遍历出来的都是商品名称
            for goods_name in shopping_cart.keys():
                #根据遍历出来的key去拿值
                goods_info = shopping_cart[goods_name]
                print(f"商品名称：{goods_name} 商品价格：{goods_info["price"]} 商品数量：{goods_info["num"]}")
        #退出
        case 5:
            print("退出成功~")
            break