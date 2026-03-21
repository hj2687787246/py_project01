# 创建csv文件 方式一
from csv import DictWriter

with open("./csv_data/01.csv","w",encoding="utf-8") as f:
    f.write("name,age,sex\n")
    f.write("小王,18,男\n")
    f.write("小张,19,女\n")

with open("./csv_data/01.csv","r",encoding="utf-8") as f:
    for line in f:
        print(line.strip())

# 创建csv文件 方式二
import csv
# newline="" 表述每行数据之间不添加换行符
with open("./csv_data/02.csv","w",encoding="utf-8",newline="") as f:
    # 创建csv写入对象 fieldnames 表头
    writer = csv.DictWriter(f,fieldnames=["name","age","sex"])
    # 写入表头
    writer.writeheader()
    # 写入数据
    writer.writerow({"name":"小王","age":18,"sex":"男"})
    writer.writerow({"name":"小张","age":19,"sex":"女"})
    writer.writerow({"name":"小王","age":18,"sex":"男"})
    writer.writerow({"name":"小张","age":19,"sex":"女"})

with open("./csv_data/02.csv","r",encoding="utf-8") as f:
    # 创建csv读取对象
    reader = csv.DictReader(f)
    # 读取数据
    for line in reader:
        print(line)

