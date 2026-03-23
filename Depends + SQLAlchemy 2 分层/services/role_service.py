from typing import List, TypeAlias

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from dao import role_dao, user_dao
from models import Role, User
from utils.password_utils import get_password_hash

# 角色列表的统一返回类型。
RoleListResult: TypeAlias = List[Role]


def _ensure_admin_user_unique(db: Session, user: schemas.UserCreate) -> None:
    # 创建管理员前先做用户名和邮箱的唯一性校验。
    if user_dao.get_user_by_username(db, user.username):
        raise BusinessException(status_code=400, code=4001, message="用户名已存在")

    if user_dao.get_user_by_email(db, user.email):
        raise BusinessException(status_code=400, code=4002, message="邮箱已存在")


def create_admin_user(db: Session, user: schemas.UserCreate) -> User:
    # 将创建管理员账号的流程收口到 service 层。
    _ensure_admin_user_unique(db, user)
    return user_dao.create_user(db, user, role_name="admin")


def create_role(db: Session, role: schemas.RoleCreate) -> Role:
    # 角色的“查重 + 创建”统一由 DAO 封装。
    return role_dao.create_role_with_check(db, role.name, role.description)


def get_all_roles(db: Session) -> RoleListResult:
    # 统一角色列表查询入口。
    return role_dao.get_all_roles(db)


def reset_password(db: Session, user_id: int, current_user: models.User, new_password: str) -> User:
    # 将“查用户 + 权限判断 + 密码更新”统一放在 service 层。
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权重置他人密码")

    hashed_password = get_password_hash(new_password)
    return user_dao.update_user_password(db, db_user, hashed_password)
