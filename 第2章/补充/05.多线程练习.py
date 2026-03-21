import threading
import time


def sing():
    while True:
        print("我在唱歌")
        time.sleep(1)

def dance():
    while True:
        print("我在跳舞")
        time.sleep(1)

def swing(msg):
    while True:
        print(msg)
        time.sleep(1)

def fly(msg):
    while True:
        print(msg)
        time.sleep(1)

# 创建线程
sing_thread = threading.Thread(target=sing)
dance_thread = threading.Thread(target=dance)
# args(元组，)
swing_thread = threading.Thread(target=swing,args=("我在游泳！哈哈哈",))
# kwargs(字典)
fly_thread = threading.Thread(target=fly,kwargs={"msg":"我在飞！哈哈哈哈"})
# 启动线程
sing_thread.start()
dance_thread.start()
swing_thread.start()
fly_thread.start()

swing_thread.join()
dance_thread.join()
swing_thread.join()
fly_thread.join()