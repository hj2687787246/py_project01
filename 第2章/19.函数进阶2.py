# # 函数参数类型
# # 加
# def add(x,y):
#     return x+y
# # 减
# def subtract(x,y):
#     return x-y
# # 乘
# def multiply(x,y):
#     return x*y
# # 除
# def divide(x,y):
#     return x/y
#
# # 计算 函数传参
# def calc(x,y,oper):
#     return oper(x,y)
#
# print(calc(2,3,add))
# print(calc(2,3,subtract))
# print(calc(2,3,multiply))
# print(calc(2,3,divide))
#
# # 匿名函数
# # 打印一个分割线
# # def out_line():
# #     print("______________________________________")
# # out_line()
# out_line = lambda : print("______________________________________")
# out_line()
# print(out_line)
# # 计算两个数之和
# def add(x,y):
#     return x+y
# print(add)
# print(add(2,3))
#
# add = lambda x,y: x+y
# print(add(2,3))
# print(add)
#
# # 3.按照每个元素的字符个数，从小到大排序
# data_list = ["C++", "C", "Python", "Jack", "PHP", "Java", "Go", "JavaScript", "Rust"]
# #排序 sort（key）为函数中的内置方法 item 代表列表中的每一个元素 len(item) 表示每个元素的长度 排序会按照长度来排序
# data_list.sort(key=lambda item: len(item))
# print(data_list)
# #从大到小
# data_list.sort(key=lambda item: len(item), reverse=True)
# print(data_list)

# # 计算n的阶乘 f(n) = n * f(n-1)
# # 递归调用（先层层递进，再逐层回归）：指的是在函数中自己调用自己的情况--一->一定得有终结点
# """
# jc(10) = 10 × jc(9) = 10 × 362880 = 3628800
# jc(9) = 9 × jc(8) = 9 × 40320 = 362880
# jc(8) = 8 × jc(7) = 8 × 5040 = 40320
# jc(7) = 7 × jc(6) = 7 × 720 = 5040
# jc(6) = 6 × jc(5) = 6 × 120 = 720
# jc(5) = 5 × jc(4) = 5 × 24 = 120
# jc(4) = 4 × jc(3) = 4 × 6 = 24
# jc(3) = 3 × jc(2) = 3 × 2 = 6
# jc(2) = 2 × jc(1) = 2 × 1 = 2
# jc(1) = 1
# """
# def jc(n):
#     if n == 1:
#         return 1
#     else:
#         return n * jc(n-1)
#
# print(jc(10))

#案例2：定义一个用于根据传入的一批商品信息（商品名、价格、数量）、优惠（优惠券、积分抵扣）、运费信息计算订单的总金额的函数。
# 具体规则如下：
# 1，优惠券需要商品金额满5000才可以使用，且优惠券金额不能超过商品总价。
# 2，积分抵扣需要商品总金额满5000才可以使用，100积分抵扣1元（且抵扣金额不能超过商品总价，积分只能整百抵扣）。

def calc_order_cost(*args, coupon=0, score=0, express=0.0):
    """
    根据传入的一批商品信息（商品名、价格、数量）、优惠（优惠券、积分抵扣）、运费信息计算订单的总金额
    parameters:
        args: 商品信息，支持元组/列表格式，如 ("鼠标",188,2) 或 ["键盘",388,1]
        coupon: 优惠券金额（默认0），仅商品总金额≥5000时可抵扣
        score: 积分数量（默认0），仅商品总金额≥5000时抵扣（100积分抵1元）
        express: 运费金额（默认0.0）
    return: 订单最终总金额（保留2位小数，符合金额格式）
    """
    # 1. 计算商品总金额（遍历args，累加 价格×数量）
    goods_total = sum([item[1] * item[2] for item in args])

    # 2. 扣减优惠券（仅商品总金额≥5000时抵扣，且抵扣后不小于0）
    if goods_total >= 5000 and coupon > 0:
        goods_total = max(goods_total - coupon, 0)

    # 3. 扣减积分抵扣（100积分抵1元，仅商品总金额≥5000时抵扣，抵扣后不小于0）
    score_deduct = score // 100  # 核心修正：100积分抵1元
    if goods_total >= 5000 and score_deduct > 0:
        goods_total = max(goods_total - score_deduct, 0)

    # 4. 添加运费（核心修正：运费是加不是减）
    order_total = goods_total + express

    # 5. 金额保留2位小数，符合实际业务场景
    return round(order_total, 2)


# 调用示例（保持你的入参不变）
calc = calc_order_cost(["鼠标", 188, 2], ["键盘", 388, 1], ["手机", 3888, 2], coupon=10, score=400, express=9.9)
print(calc)
calc = calc_order_cost(["鼠标",188,2],["键盘",388,1],["手机",3888,1])
print(calc)