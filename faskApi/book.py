from fastapi import APIRouter

# 创建一个路由分发实例
books = APIRouter()
# 创建一个路由，并指定路径为/
@books.get("/xixi")
async def index():
    return {"message": "Hello 大笨猪"}