from fastapi import FastAPI,Depends

# 定义一个类依赖
class CommonPageParams:
    def __init__(self,page:int = 1,page_size:int=10):
        self.page = page
        self.page_size = page_size

# 实例化FastAPI
app = FastAPI()
@app.get("/goods",summary="商品列表")
def get_goods(commons:CommonPageParams = Depends()):
    return f"第{commons.page}页，每页{commons.page_size}条商品"