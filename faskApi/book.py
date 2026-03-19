from fastapi import APIRouter,Path,Query
from pydantic import BaseModel
# 引入类型注解 它的作用就是告诉代码的读者（包括你自己、IDE 工具、FastAPI 框架）：“这个变量 / 参数 / 返回值应该是什么类型
from typing import List, Optional

# 创建一个路由分发实例
books = APIRouter()

# 1.定义数据模型
class Book(BaseModel):
    id: int
    title: str
    author: str
    price: float

# 2.模拟数据库（内存中的列表）
fake_books_db = [
    Book(id=1,title="三体",author="刘慈欣",price=99.8),
    Book(id=2,title="活着",author="余华",price=45.0),
    Book(id=3,title="百年孤独",author="马尔克斯",price=59.9),
]
# 3. 路径参数进阶，根据ID获取单本书
# 使用Path（...，title = '书籍ID'，ge=1）进行验证：ge=1 表示必须大于等于1
@books.get("/{book_id}",response_model=Book)
async def get_book(book_id:int = Path(...,title = '书籍ID',ge=1,description="要查询的书籍的唯一标识符")):
    for book in fake_books_db:
        if book.id == book_id:
            return book
    return {"error":"Book not found"} # 实际项目中建议使用 HTTPException

# 4.查询进阶:获取书籍列表（支持筛选和分页）
# 使用Query(...)对查询参数进行验证
"""
查询参数示例：获取书籍列表，支持多条件筛选
-**author**:作者名可选
-**min_price**:最低价格可选
-**limit**:最多返回多少本（默认10本）
"""
@books.get("/",response_model=List[Book])
async def get_books(author:Optional[str] = Query(None,min_length = 2,max_length=20,description="按作者名筛选"),min_price: Optional[float] = Query(None,ge=0,description="最低价格筛选"),limit: int = Query(10,ge=1,le=100,description="返回数量限制限制")):
    results = fake_books_db
    # 简单的筛选逻辑
    if author:
        results = [book for book in results if author in book.author]
    if min_price is not None:
        results = [book for book in results if book.price >= min_price]
    return results[:limit]