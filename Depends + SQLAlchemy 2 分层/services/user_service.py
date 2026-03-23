from datetime import timedelta
from typing import List, Tuple, TypeAlias

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from dao import user_dao
from dao.user_dao import DeleteUserResult
from utils.password_utils import validate_password, verify_password
from utils.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

# 登录后返回“用户对象 + token”的统一结构。
LoginResult: TypeAlias = Tuple[models.User, str]
# 分页查询返回“数据列表 + 总数”的统一结构。
UserListResult: TypeAlias = tuple[List[models.User], int]


def _ensure_user_unique(db: Session, user: schemas.UserCreate) -> None:
    # 注册前检查用户名和邮箱是否已被使用。
    if user_dao.get_user_by_username(db, user.username):
        raise BusinessException(status_code=400, code=4001, message="用户名已存在")

    if user_dao.get_user_by_email(db, user.email):
        raise BusinessException(status_code=400, code=4002, message="邮箱已存在")


def _ensure_password_valid(password: str) -> None:
    # 密码复杂度校验统一放在 service 层。
    if not validate_password(password):
        raise BusinessException(status_code=400, code=4003, message="密码至少8位，包含大小写、数字、特殊字符")


def login_user(db: Session, username: str, password: str) -> LoginResult:
    # 登录时统一完成用户查找、密码校验和 token 生成。
    user = user_dao.get_user_by_username(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误", headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return user, access_token


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    # 注册流程统一在 service 层完成各类前置校验。
    _ensure_user_unique(db, user)
    _ensure_password_valid(user.password)
    return user_dao.create_user(db, user, role_name="user")


def get_user_detail(db: Session, user_id: int, current_user: models.User) -> models.User:
    # 详情查询在 service 层完成“存在性 + 查看权限”判断。
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if db_user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权查看他人信息")

    return db_user


def get_user_list(db: Session, page: int, page_size: int) -> UserListResult:
    # 分页查询先保持轻量包装，便于后续扩展。
    return user_dao.get_user_list(db, page, page_size)


def search_users(db: Session, keyword: str) -> List[models.User]:
    # 搜索保留为 service 层入口，避免 route 直接调数据层。
    return user_dao.search_users(db, keyword)


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate, current_user: models.User) -> models.User:
    # 更新流程统一完成权限、角色、唯一性校验。
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if db_user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权修改他人信息")

    if user_update.role_id is not None and current_user.role != "admin":
        raise BusinessException(status_code=403, code=4004, message="无权修改用户角色")

    if user_update.role_id is not None and not db.get(models.Role, user_update.role_id):
        raise BusinessException(status_code=400, code=4005, message="角色不存在")

    if user_update.username and user_update.username != db_user.username:
        if user_dao.get_user_by_username(db, user_update.username):
            raise BusinessException(status_code=400, code=4001, message="用户名已被占用")

    if user_update.email and user_update.email != db_user.email:
        if user_dao.get_user_by_email(db, user_update.email):
            raise BusinessException(status_code=400, code=4002, message="邮箱已被占用")

    return user_dao.update_user(db, user_id, user_update)


def delete_user(db: Session, user_id: int) -> DeleteUserResult:
    # 删除流程统一把 DAO 返回结果翻译成业务异常或 HTTP 异常。
    delete_result = user_dao.delete_user(db, user_id)
    if not delete_result["success"]:
        if delete_result["reason"] == "admin_forbidden":
            raise BusinessException(status_code=403, code=4003, message="不能删除 admin 角色账号")
        raise HTTPException(status_code=404, detail="用户不存在")
    return delete_result
