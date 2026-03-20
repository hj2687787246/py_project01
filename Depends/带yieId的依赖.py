from fastapi import FastAPI,Depends,Request
import time

def log_request(request:Request):
    start_time = time.time()
    print(f"请求路由路径：{request.url.path},方法：{request.method}")
    # 带 yield 的依赖（资源管理核心，数据库必用）
    # 带yield的依赖支持请求前执行逻辑 + 响应后释放资源，是管理数据库会话、文件句柄等资源的标准方案：
    yield # 释放控制权，注入到接口中
    # 接口返回响应后执行
    print(f"请求处理完成，耗时：{time.time() - start_time:.4f}s")
# 创建fastAPI 全局依赖：所有接口自动生效
app = FastAPI(dependencies=[Depends(log_request)])

@app.get("/test1")
def test1():
    print("test1已执行")
    return "test1"
@app.get("/")
def index():
    print("index已执行")
    return "hello yieId"