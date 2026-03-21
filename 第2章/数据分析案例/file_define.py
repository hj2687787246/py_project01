# 导入
import json
from pathlib import Path

from data_define import Record
# 读写文件类

class FileReader:
    def read_date(self)-> list[Record]:
        # 读取文件的数据，读到的每一条数据都转换为Record对象，将它们都封装到List内返回即可
        pass
# 读取csv文件
class CsvReader(FileReader):
    def __init__(self,path):
        self.path = path

    # 实现父类方法
    def read_date(self) -> list[Record]:
        # 创建一个列表以存储record
        record_list:list[Record] = []
        with open(self.path,"r",encoding="utf-8") as f:
            for line_index, line in enumerate(f):
                # 原始数据中第一行为标题
                if line_index == 0:
                    continue
                line = line.strip()
                if not line:
                    continue
                date_list = line.split(",")
                if len(date_list) < 4:
                    continue
                record_list.append(Record(date_list[0],date_list[1],date_list[2],date_list[3]))
        return record_list

class JsonReader(FileReader):
    def __init__(self,path):
        self.path = path

    def read_date(self) -> list[Record]:
        # 创建一个列表存储record
        record_list = []
        with open(self.path,"r",encoding="utf-8") as f:
            date_dict = json.load(f)
            for date in date_dict:
                record_list.append(Record(date["订单日期"],date["订单ID"],date["订单金额"],date["销售年份"]))
        return record_list
if __name__ == '__main__':
    # 创建对象传入地址
    base_dir = Path(__file__).resolve().parent
    csvReader = CsvReader(str(base_dir / "resource" / "order_data.cvs"))
    record_list1 =  csvReader.read_date()
    for r in record_list1:
        print(r)
    # 创建对象传入地址
    jsonReader = JsonReader(str(base_dir / "resource" / "order_data.json"))
    record_list2 = jsonReader.read_date()
    for r in record_list2:
        print(r)

