from session.db_session import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column,relationship

# 角色表
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="角色主键ID")
    # index 索引，给高频字段加索引
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色名称",index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True, comment="角色描述")
    # 一个角色可以对应多个用户
    # 注意：这里使用字符串 "User"，SQLAlchemy 会在所有类加载完成后自动解析
    users: Mapped[list["User"]] = relationship("User", back_populates="role_info")