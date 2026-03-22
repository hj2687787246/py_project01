from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from session.db_session import Base


# 统一使用 UTC 时间入库，响应层再按需要转换时区。
def utc_now() -> datetime:
    """返回带 UTC 时区的当前时间。"""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="用户主键ID")
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="用户名"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="哈希密码"
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"), nullable=False, comment="关联角色表ID"
    )
    # 关系属性：通过 role_id 关联到角色表。
    role_info: Mapped["Role"] = relationship("Role", back_populates="users")
    age: Mapped[int] = mapped_column(comment="年龄")
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="邮箱"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        comment="最后更新时间",
    )

    @property
    def role(self) -> str | None:
        """兼容现有代码读取 user.role 的属性访问方式。"""
        # 兼容现有鉴权和响应层读取 user.role 的写法。
        return self.role_info.name if self.role_info else None
