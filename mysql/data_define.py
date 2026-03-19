#定义数据类
class Record:
    def __init__(self,date,order_id,money,year):
        # 订单日期
        self.date = date
        # 订单ID
        self.order_id = order_id
        # 订单金额
        self.money = float(money)
        # 订单年份
        self.year = year
    def __str__(self):
        #返回字符串
        return f"{self.date}{self.order_id}{self.money}{self.year}"
