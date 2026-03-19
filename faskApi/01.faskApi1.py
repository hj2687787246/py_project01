from fastapi import FastAPI
import uvicorn
import fastapi_cdn_host
# 引入Request对象
from fastapi import Request
from book import books
from pydantic import BaseModel

# Pydantic 模型验证
# 定义数据模型 User 模型，包含 name 和 age 两个字段
class User(BaseModel):
    name: str
    age: int

# 实例化FastAPI
app = FastAPI()
# 使用CDN加速静态文件 访问docs会加快访问速度
fastapi_cdn_host.patch_docs(app)

# 引入路由模块books
app.include_router(books,prefix="/book")
# 定义路由
@app.get("/")
async def root():
    return {"message": "Hello ..."}

@app.get("/say")
async def say_hello(request: Request):
    name,age = request.query_params.get("name"),request.query_params.get("age")
    return {"message": f"Hello {name},{age}"}

# 使用POST方式接收数据  Pydantic 模型验证 POST 请求体
@app.post("/root1")
async def root1(user: User):
    print(user.name,user.age)
    return {"message": f"Hello {user.name},{user.age}"}

# 使用POST方式接收数据 没有使用Pydantic 模型验证
@app.post("/")
async def root(request: Request):
    # 将请求体中的数据转换为JSON await 在post类型异步函数中使用
    result = await request.json()
    print(result)
    name,age = result.get("name"),result.get("age")

    return {"message": f"Hello {name},{age}"}

if __name__ == '__main__':
    # 启动服务
    uvicorn.run(app, host="127.0.0.1", port=8000)