from fastapi import FastAPI,Depends

# 1.定义依赖项：普通函数，封装分页参数逻辑
def common_page_params(page: int = 1,page_size: int = 10 ):
    return {"page":page,"page_size":page_size}
# 创建app
app = FastAPI()
# 2.接口中通过Depends注入依赖
@app.get("/items",summary="商品列表")
def get_items(commons: dict = Depends(common_page_params)):
    return f"第{commons['page']}页每页{commons['page_size']}"