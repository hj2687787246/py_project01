# 数据库模型文件
from sqlalchemy import Column,Integer,String,Float
from database import Base

class BookDB(Base):
    __tablename__ = 'books' #数据库中的表名
    # 表中的字段
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,index=True)
    author = Column(String,index=True)
    price = Column(Float)