from typing import Sequence, TypeAlias

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from dao import role_dao, user_dao
from models import Role, User
from utils.password_utils import get_password_hash

# 角色列表的统一返回类型。
RoleListResult: TypeAlias = Sequence[Role]


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
def get_all_roles(db: Session) -> RoleListResult:
    """查询全部角色列表。"""
    return role_dao.get_all_roles(db)


# 重置密码
def reset_password(db: Session, user_id: int, current_user: models.User, new_password: str) -> User:
    """重置指定用户密码，并校验操作权限。"""
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权重置他人密码")

    hashed_password = get_password_hash(new_password)
    return user_dao.update_user_password(db, db_user, hashed_password)
