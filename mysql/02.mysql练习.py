
from data_define import Record
from file_define import CsvReader,JsonReader
from pathlib import Path
from pymysql import Connection
import pymysql
def insert_many():
    # 2. 构造批量插入的SQL和参数列表
    sql = """
          INSERT INTO orders(order_time, order_ID, order_price, order_year)
          VALUES (%s, %s, %s, %s) \
          """
    # 把所有数据转换成参数元组的列表
    params_list = [(data.date, data.order_id, data.money, data.year) for data in all_data]
    # 3. 批量执行（核心优化点）
    cursor.executemany(sql, params_list)
    connection.commit()
    print(f"成功批量插入 {len(params_list)} 条订单数据")

base_dir = Path(__file__ ).resolve().parent

csvReader = CsvReader(str(base_dir / "resource" / "order_data.cvs"))
jsonReader = JsonReader(str(base_dir / "resource" / "order_data.json"))

csv_data:list[Record] = csvReader.read_date()
json_data:list[Record] = jsonReader.read_date()
all_data = csv_data + json_data




with Connection(
    host="localhost",
    port=3306,
    user="root",
    password="hejie@2244"
) as connection:
    cursor = connection.cursor()
    cursor.execute("create database test_goods charset=utf8")
    connection.select_db("test_goods")
    cursor.execute("create table orders(order_time varchar(20),order_ID varchar(20),order_price float,order_year varchar(4))")

    try:
        # 批量插入数据
        insert_many()
    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"批量插入失败: {str(e)}")
        raise
    # 提交
    connection.commit()


