import os
from dataclasses import dataclass
from sqlalchemy.orm import Session

from core.logger import get_logger
from dao import role_dao, user_dao
from session import db_session

logger = get_logger()


@dataclass
class _SeedAdminUser:
    username: str
    password: str
    age: int
    email: str


def initialize_database() -> None:
    """应用启动时初始化数据库表并补齐基础种子数据。"""
    db_session.Base.metadata.create_all(bind=db_session.engine)
    logger.info("数据库表初始化检查完成")
    _seed_base_data()


def _seed_base_data() -> None:
    """确保默认角色和管理员账号存在。"""
    # 初始化角色数据
    with db_session.SessionLocal() as db:
        _ensure_default_roles(db)
        _ensure_default_admin(db)


def _ensure_default_roles(db: Session) -> None:
    created = False
    if role_dao.get_role_by_name(db, "admin") is None:
        role_dao.create_role(db, name="admin", description="系统管理员")
        created = True
    if role_dao.get_role_by_name(db, "user") is None:
        role_dao.create_role(db, name="user", description="普通用户")
        created = True
    if created:
        logger.info("初始化角色数据完成")


def _ensure_default_admin(db: Session) -> None:
    if user_dao.get_user_by_username(db, "admin") is not None:
        return

    # 避免在代码里写死默认管理员密码；未配置时只跳过初始化管理员账号。
    default_admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
    if not default_admin_password:
        logger.warning("未配置 DEFAULT_ADMIN_PASSWORD，跳过初始化管理员账号")
        return

    admin_user = _SeedAdminUser(
        username="admin",
        password=default_admin_password,
        age=26,
        email="2687787246@qq.com",
    )
    user_dao.create_user(db, admin_user, role_name="admin")
    logger.info("初始化管理员账号完成")
