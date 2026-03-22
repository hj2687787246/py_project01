import os
from pymysql import Connection

# # 创建链接对象
# connection = Connection(
#     host="localhost", # ip
#     port=3306,      # 端口
#     user="root",      # 账号
#     password="hejie@2244"# 密码
# )
# # 创建游标对象
# cursor = connection.cursor()
# # 非查询sql
# #cursor.execute("create database test charset utf8")
# # 选择数据库
# connection.select_db("test")
# # cursor.execute("insert into student values (1,'何杰'),(2,'李梦'),(3,'白小林')")
# cursor.execute("select * from student")
#
# # 提交事务，否则数据不会真正写入数据库
# # connection.commit()
# # 获取结果 结果为元组
# result = cursor.fetchall()
# print(result)
# # 关闭链接
# connection.close()

mysql_host = os.getenv("MYSQL_HOST", "localhost")
mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
mysql_user = os.getenv("MYSQL_USER", "root")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE", "test")

if not mysql_password:
    raise ValueError("缺少 MYSQL_PASSWORD 环境变量")

# 创建链接对象
with Connection(
    host=mysql_host,
    port=mysql_port,
    user=mysql_user,
    password=mysql_password
) as connection:
    # 创建游标对象
    cursor =  connection.cursor()
    # 选择数据库
    connection.select_db(mysql_database)
    # 查询sql
    cursor.execute("select * from student")
    # 获取结果
    result = cursor.fetchall()
    result_list = []
    for result in result:
        result_list.append({"id":result[0],"name":result[1]})

    print(result_list)
