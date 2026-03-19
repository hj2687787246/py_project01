from fastapi import APIRouter,Depends,HTTPException,Path
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

# 导入我们自己写的模块
from database import get_db
import models

#创建分发路由
books = APIRouter()

# Pydantic Schema(用于API文档和数据验证)
class BookBase(BaseModel):
    title: str
    author: str
    price:float

class BookCreate(BookBase):
    pass # 创建时不需要id

class Book(BookBase):
    id: int
    class Config:
        orm_mode = True # 告诉Pydantic 这是ORM模型，可以直接读取

# 增（create）：POST /book/
@books.post("/",response_model=Book)
def create_book(book: BookCreate,db:Session=Depends(get_db)):
    # 1.将Pydantic 数据库转换为SQLAlchemy模型
    db_book = models.BookDB(**book.dict())
    # 2.存入数据库
    db.add(db_book)
    db.commit()
    # 3.刷新以获得自增ID
    db.refresh(db_book)

    return db_book

# 2.查（Read）：get / book/{book_id}---
@books.get("/{book_id}",response_model=Book)
def get_book(book_id:int,db:Session = Depends(get_db)):
    # 1.从数据库中查询
    book = db.query(models.BookDB).filter(models.BookDB.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404,detail="Book not found")
    return book
# 3.查（read）：get/book/列表
@books.get("/",response_model=List[Book])
# 分页参数
def get_books(skip: int = 0,limit:int=10,db:Session = Depends(get_db)):
    # 从数据库中查询
    return db.query(models.BookDB).offset(skip).limit(limit).all()

# 4. 改（Update）：PUT/book/{book_id}
@books.put("/{book_id}",response_model=Book)
def update_book(book_id:int,updated_book:BookCreate,db:Session=Depends(get_db)):
    db_book = db.query(models.BookDB).filter(models.BookDB.id==book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404,detail="Book not found")

    # 更新字段
    for key,value in updated_book.dict().items():
        setattr(db_book,key,value)

    db.commit()
    # 刷新
    db.refresh(db_book)
    return db_book

# 删（DELETE） delete/book/{book_id}
@books.delete("/{book_id}")
def delete_book(book_id:int,db:Session = Depends(get_db)):
    db_book = db.query(models.BookDB).filter(models.BookDB.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404,detail="Book not found")

    db.delete(db_book)
    db.commit()
    return {"message":"book deleted successfully"}