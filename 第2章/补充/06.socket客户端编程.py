import socket
# 创建socket对象
socket_client = socket.socket()
# 连接服务端
socket_client.connect(("localhost",8888))

while True:

    msg = input("输入要发送给服务端的消息：")
    if msg == "exit":
        break
    # 发送消息
    socket_client.send(msg.encode("UTF-8"))
    # 接收消息 recv方法是阻塞的，没有接受到消息不会执行下面
    recv_data = socket_client.recv(1024)
    print(f"服务器回复的消息是：{recv_data.decode('UTF-8')}")
socket_client.close()