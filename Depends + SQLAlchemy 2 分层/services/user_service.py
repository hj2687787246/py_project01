from typing import List, Tuple, TypeAlias, Sequence

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from dao import user_dao
from dao.user_dao import DeleteUserResult
from models import User
from utils.auth import create_refresh_token
from utils.file_utils import save_avatar
from utils.auth import validate_password, verify_password, verify_token, create_access_token, get_password_hash
from config import Settings

# 登录后返回“用户对象 + token”的统一结构。
LoginResult: TypeAlias = Tuple[models.User, str, str]

# 分页查询返回“数据列表 + 总数”的统一结构。
UserListResult: TypeAlias = tuple[List[models.User], int]


# 注册校验

def _ensure_user_unique(db: Session, user: schemas.UserCreate) -> None:
    """注册前检查用户名和邮箱是否已被使用。"""
    if user_dao.get_user_by_username(db, user.username):
        raise BusinessException(status_code=400, code=4001, message="用户名已存在")

    if user_dao.get_user_by_email(db, user.email):
        raise BusinessException(status_code=400, code=4002, message="邮箱已存在")


# 密码校验
def _ensure_password_valid(password: str) -> None:
    """密码复杂度校验统一放在 service 层。"""
    if not validate_password(password):
        raise BusinessException(status_code=400, code=4003, message="密码至少8位，包含大小写、数字、特殊字符")

# 重置密码
def reset_password(db: Session, user_id: int, current_user: models.User, password: str, new_password: str) -> User:
    """重置指定用户密码，并校验操作权限。"""
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权重置他人密码")

    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")

    # 密码复杂度验证
    _ensure_password_valid(new_password)
    hashed_password = get_password_hash(new_password)
    return user_dao.update_user_password(db, db_user, hashed_password)

# 登录校验
def login_user(db: Session, username: str, password: str, settings: Settings) -> LoginResult:
    """完成用户查找、密码校验和 token 生成。"""
    db_user = user_dao.get_user_by_username(db, username=username)
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误", headers={"WWW-Authenticate": "Bearer"})
    #生成两个Token：payload里都放{"sub": username}
    access_token = create_access_token(data={"sub": db_user.username}, settings=settings)
    refresh_token = create_refresh_token(data={"sub": db_user.username}, settings=settings)

    return db_user, access_token, refresh_token

# 刷新 Token 接口
def get_new_access_token(request, settings) -> str:

    exception = HTTPException(401, detail="Refresh Token 无效")
    username = verify_token(request.refresh_token, exception, settings)
    new_access_token = create_access_token(data={"sub": username}, settings=settings)

    return new_access_token

# 创建用户
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """完成注册前置校验并创建普通用户。"""
    _ensure_user_unique(db, user)
    _ensure_password_valid(user.password)
    return user_dao.create_user(db, user, role_name="user")


# 根据id查询
def get_user_detail(db: Session, user_id: int, current_user: models.User) -> models.User:
    """完成用户存在性与查看权限校验，并返回用户详情。"""
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if db_user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权查看他人信息")

    return db_user


# 分页查询
def get_user_list(db: Session, page: int, page_size: int) -> tuple[List[models.User], int]:
    """分页查询用户列表并返回总数。"""
    return user_dao.get_user_list(db, page, page_size)


# 根据ID、用户名模糊查询
def search_users(db: Session, keyword: str) -> Sequence[User]:
    """按关键字搜索用户。"""
    return user_dao.search_users(db, keyword)


# 更新用户
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate, current_user: models.User) -> models.User:
    """完成权限、角色、唯一性校验并更新用户。"""
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

# 删除用户
def delete_user(db: Session, user_id: int) -> DeleteUserResult:
    """删除用户，并将 DAO 返回结果翻译成业务异常或 HTTP 异常。"""
    delete_result = user_dao.delete_user(db, user_id)
    if not delete_result["success"]:
        if delete_result["reason"] == "admin_forbidden":
            raise BusinessException(status_code=403, code=4003, message="不能删除 admin 角色账号")
        raise HTTPException(status_code=404, detail="用户不存在")
    return delete_result

# 头像保存
def upload_avatar(db: Session,
                  user_id: int,
                  current_user: models.User,
                  file: UploadFile) -> models.User:
    """上传并保存当前用户头像。"""
    # 1.查找用户是否存在
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 2.校验ID是否一致，只能改自己的
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改他人头像")
    # 3.使用工具保存文件到 static/avatars，并获取 avatar_url
    new_avatar_url = save_avatar(file,db_user.avatar_url)
    # 4.更新数据库
    updated_user = user_dao.update_user_avatar(db, user_id, new_avatar_url)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return updated_user