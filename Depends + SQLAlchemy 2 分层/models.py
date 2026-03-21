# 数据库 ORM 模型
from datetime import datetime
from sqlalchemy import String,DateTime
from sqlalchemy.orm import Mapped,mapped_column

from database import Base

class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True,comment="用户主键ID")
    username:Mapped[str] = mapped_column(String(50),unique=True,nullable=False,comment="用户名")
    age:Mapped[int] = mapped_column(comment="年龄")
    email:Mapped[str] = mapped_column(String(100),unique=True,nullable=False,comment="邮箱")

    # 创建时间 在创建的时候赋值
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )

    # 更新时间 创建、更新时赋值
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="最后更新时间"
    )