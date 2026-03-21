# books.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession  # 注意这里导入变了
from sqlalchemy import select  # 导入 select 函数
from typing import List
from pydantic import BaseModel

from database import get_db
import models

books = APIRouter()


# --- Pydantic Schema (保持不变) ---
class BookBase(BaseModel):
    title: str
    author: str
    price: float


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    model_config = {"from_attributes": True}

    # ================= 异步 CRUD 实现 =================


# --- 1. 增 (Create) ---
@books.post("/", response_model=Book)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    # 1. 转换数据
    db_book = models.BookDB(**book.model_dump())  # 注意：pydantic v2 推荐用 model_dump() 代替 dict()

    # 2. 存入数据库 (加 await)
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)  # 刷新也要 await

    return db_book


# --- 2. 查 (单个) ---
@books.get("/{book_id}", response_model=Book)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    # 新语法：select + execute + scalar_one_or_none
    result = await db.execute(select(models.BookDB).where(models.BookDB.id == book_id))
    book = result.scalar_one_or_none()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# --- 3. 查 (列表) ---
@books.get("/", response_model=List[Book])
async def get_books(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    # scalars().all() 用于获取列表
    result = await db.execute(select(models.BookDB).offset(skip).limit(limit))
    return result.scalars().all()


# --- 4. 改 (Update) ---
@books.put("/{book_id}", response_model=Book)
async def update_book(book_id: int, updated_book: BookCreate, db: AsyncSession = Depends(get_db)):
    # 1. 先查找到这本书
    result = await db.execute(select(models.BookDB).where(models.BookDB.id == book_id))
    db_book = result.scalar_one_or_none()

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # 2. 更新字段 (这一步是操作内存对象，不需要 await)
    book_data = updated_book.model_dump()
    for key, value in book_data.items():
        setattr(db_book, key, value)

    # 3. 提交保存 (需要 await)
    await db.commit()
    await db.refresh(db_book)

    return db_book


# --- 5. 删 (Delete) ---
@books.delete("/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.BookDB).where(models.BookDB.id == book_id))
    db_book = result.scalar_one_or_none()

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # 删除和提交都需要 await
    await db.delete(db_book)
    await db.commit()

    return {"message": "Book deleted successfully"}
