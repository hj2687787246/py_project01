import socket

# 创建socket对象
socket_server = socket.socket()
# 绑定ip和端口
socket_server.bind(("localhost",8888))
# 监听端口
# listen方法内接受一个整数传参，表示接受的链接数量
socket_server.listen(1)
# 等带客户端链接 accept是一个阻塞方法，如果没有接收到客户端的链接，就不往下执行
conn,address = socket_server.accept()

print(f"接收到了客户端的链接，地址是：{address}")
while True:
    # 接收数据 recv接受的参数是缓冲区大小，一般给到1024就行
    # 接收到的数据是bytes类型，需要decode转换成字符串类型
    data:str = conn.recv(1024).decode("UTF-8")
    print(f"客户端发来的消息是：{data}")
    # 发送回复消息 encode将当前字符串编码转换成bytes类型
    msg = input("请输入你要和客户端回复的消息：").encode("UTF-8")
    if msg == 'exit':
        break
    print(msg)
    # 发送数据
    conn.send(msg)
# 关闭链接
conn.close()
socket_server.close()