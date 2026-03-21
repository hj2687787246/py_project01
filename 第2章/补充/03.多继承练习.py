class NFC:
    NFC_TYPE = "第五代"
    producer = "HM"
    def read_card(self):
        print("NFC读卡")

    def write_card(self):
        print("NFC写卡")

class HWX:
    def HWX(self):
        print("红外线系统已开启")

class KP:
    def KP(self):
        print("KP功能已经开启")

class My_iphone(NFC,HWX,KP):
    #不想新增功能了
    pass

my_iphone = My_iphone()
my_iphone.NFC_TYPE = "第七代"
my_iphone.KP()
my_iphone.HWX()
my_iphone.read_card()
my_iphone.write_card()
print(my_iphone.NFC_TYPE)