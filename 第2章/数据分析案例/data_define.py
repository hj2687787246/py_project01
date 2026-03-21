#定义数据类
class Record:
    def __init__(self,date,order_id,money,province):
        # 订单日期
        self.data = date
        # 订单ID
        self.order_id = order_id
        # 订单金额
        self.money = float(money)
        # 订单省份
        self.province = province
    def __str__(self):
        #返回字符串
        return f"{self.data}{self.order_id}{self.money}{self.province}"
