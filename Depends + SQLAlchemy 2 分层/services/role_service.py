from typing import List, TypeAlias
from sqlalchemy.orm import Session
import schemas

from core.exceptions import BusinessException
from dao import role_dao, user_dao
from models import Role, User

# 角色列表的统一返回类型。
RoleListResult: TypeAlias = List[Role]

# 管理员创建前校验
def _ensure_admin_user_unique(db: Session, user: schemas.UserCreate) -> None:
    """创建管理员前校验用户名和邮箱唯一性。"""
    if user_dao.get_user_by_username(db, user.username):
        raise BusinessException(status_code=400, code=4001, message="用户名已存在")

    if user_dao.get_user_by_email(db, user.email):
        raise BusinessException(status_code=400, code=4002, message="邮箱已存在")


# 创建管理员
def create_admin_user(db: Session, user: schemas.UserCreate) -> User:
    """创建管理员账号。"""
    _ensure_admin_user_unique(db, user)
    return user_dao.create_user(db, user, role_name="admin")


# 创建角色
def create_role(db: Session, role: schemas.RoleCreate) -> Role:
    """创建角色并校验重复。"""
    return role_dao.create_role_with_check(db, role.name, role.description)


# 查询全部角色
def get_all_roles(db: Session) -> list[type[Role]]:
    """查询全部角色列表。"""
    return role_dao.get_all_roles(db)



