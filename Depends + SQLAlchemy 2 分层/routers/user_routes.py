from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from core.logger import get_logger
from dao import user_dao
from session.db_session import get_db
from utils.password_utils import verify_password
from utils.security import (ACCESS_TOKEN_EXPIRE_MINUTES,
                            create_access_token,
                            get_current_admin,
                            get_current_user)

logger = get_logger()
router = APIRouter(prefix="/users", tags=["用户管理"])


# 登录
@router.post("/token", response_model=schemas.Token, summary="登录获取 Token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    logger.info(f"收到登录请求: username={form_data.username}")
    user = user_dao.get_user_by_username(db, username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.error(f"登录失败: username={form_data.username}, reason=用户名或密码错误")
        raise HTTPException(status_code=400,detail="用户名或密码错误",headers={"WWW-Authenticate": "Bearer"})

    # 创建 JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    logger.success(f"登录成功: user_id={user.id}, username={user.username}, role={user.role}")
    return {"access_token": access_token, "token_type": "bearer"}


# 创建用户
@router.post("",response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="创建新用户")
def create_user_api(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """创建普通用户账号。"""
    logger.info(f"收到创建用户请求: username={user.username}, email={user.email}")

    if user_dao.get_user_by_username(db, user.username):
        logger.error(f"创建用户失败: username={user.username}, reason=用户名已存在")
        raise BusinessException(status_code=400, code=4001, message="用户名已存在")

    if user_dao.get_user_by_email(db, user.email):
        logger.error(f"创建用户失败: username={user.username}, email={user.email}, reason=邮箱已存在")
        raise BusinessException(status_code=400, code=4002, message="邮箱已存在")

    # 普通注册入口固定创建 user 角色，避免通过该接口直接注册管理员。
    db_user = user_dao.create_user(db, user, role_name="user")
    logger.success(f"创建用户成功: user_id={db_user.id}, username={db_user.username}, role={db_user.role}")

    return schemas.UnifiedResponse(data=db_user)


# 按 ID 查询用户，增加 Depends(get_current_user) 保护
@router.get("/{user_id}", response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="根据ID查询用户")
def get_user_api(user_id: int,
                 db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    """查询单个用户详情。"""
    logger.info(f"收到查询用户请求: operator_id={current_user.id}, operator={current_user.username}, "
                f"role={current_user.role}, target_user_id={user_id}")

    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        logger.error(f"查询用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                     f"target_user_id={user_id}, reason=用户不存在")

        raise HTTPException(status_code=404, detail="用户不存在")

    # 权限判断：管理员可查看任意用户，普通用户只能查看自己。
    if db_user.id != current_user.id and current_user.role != "admin":
        logger.error(f"查询用户被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                     f"target_user_id={user_id}, reason=无权查看他人信息")

        raise HTTPException(status_code=403, detail="无权查看他人信息")

    logger.success(f"查询用户成功: operator_id={current_user.id}, operator={current_user.username}, "
                   f"target_user_id={user_id}")

    return schemas.UnifiedResponse(data=db_user)


# 分页查询
@router.get("",response_model=schemas.UnifiedResponse[schemas.PageResult[schemas.UserResponse]],summary="分页查询用户列表")
def get_user_list_api(page_params: schemas.PageParams = Depends(),
                      db: Session = Depends(get_db),
                      current_admin: models.User = Depends(get_current_admin)):
    """分页查询用户列表，仅管理员可访问。"""
    logger.info(f"收到分页查询用户列表请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f"role={current_admin.role}, page={page_params.page}, page_size={page_params.page_size}")

    users, total = user_dao.get_user_list(db, page_params.page, page_params.page_size)
    logger.success(f"分页查询用户列表成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"returned_count={len(users)}, total={total}")

    page_result = schemas.PageResult(items=users,total=total,page=page_params.page,page_size=page_params.page_size)
    return schemas.UnifiedResponse(data=page_result)


# 模糊查询
@router.get( "/search/", response_model=schemas.UnifiedResponse[List[schemas.UserResponse]], summary="模糊查询用户")
def search_users_api(keyword: str = Query(..., min_length=1, description="搜索关键字"),
                     db: Session = Depends(get_db),
                     current_admin: models.User = Depends(get_current_admin)):
    """按关键字模糊查询用户，仅管理员可访问。"""
    logger.info(f"收到模糊查询用户请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f"role={current_admin.role}, keyword={keyword}")

    users = user_dao.search_users(db, keyword)
    logger.success(f"模糊查询用户成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"keyword={keyword}, returned_count={len(users)}")
    return schemas.UnifiedResponse(data=users)


# 更新用户：自己能改基础信息，管理员能改全部信息，包括 role_id
@router.put("/{user_id}", response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="更新用户信息")
def update_user_api( user_id: int,
                     user_update: schemas.UserUpdate,
                     db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):
    """更新用户信息并执行权限与唯一性校验。"""
    logger.info(f"收到更新用户请求: operator_id={current_user.id}, operator={current_user.username}, "
                f"role={current_user.role}, target_user_id={user_id}")

    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                     f"target_user_id={user_id}, reason=用户不存在")

        raise HTTPException(status_code=404, detail="用户不存在")

    # 1. 基础权限：只能修改自己，除非是管理员。
    if db_user.id != current_user.id and current_user.role != "admin":
        logger.error(f"更新用户被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                     f"target_user_id={user_id}, reason=无权修改他人信息")

        raise HTTPException(status_code=403, detail="无权修改他人信息")

    # 2. 高级权限：只有管理员允许修改角色。
    if user_update.role_id is not None and current_user.role != "admin":
        logger.error(f"更新用户角色被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                     f"target_user_id={user_id}, reason=无管理员权限")

        raise BusinessException(status_code=403, code=4004, message="无权修改用户角色")

    # 角色主键存在性校验，避免写入无效外键。
    if user_update.role_id is not None and not db.get(models.Role, user_update.role_id):
        logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                     f"target_user_id={user_id}, role_id={user_update.role_id}, reason=角色不存在")

        raise BusinessException(status_code=400, code=4005, message="角色不存在")

    # 3. 唯一性校验
    if user_update.username and user_update.username != db_user.username:
        if user_dao.get_user_by_username(db, user_update.username):
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, username={user_update.username}, reason=用户名已被占用")

            raise BusinessException(status_code=400, code=4001, message="用户名已被占用")

    if user_update.email and user_update.email != db_user.email:
        if user_dao.get_user_by_email(db, user_update.email):
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, email={user_update.email}, reason=邮箱已被占用")

            raise BusinessException(status_code=400, code=4002, message="邮箱已被占用")

    updated_user = user_dao.update_user(db, user_id, user_update)
    logger.success(f"更新用户成功: operator_id={current_user.id}, operator={current_user.username}, "
                   f"target_user_id={user_id}")
    return schemas.UnifiedResponse(data=updated_user)


# 删除用户
@router.delete("/{user_id}",response_model=schemas.UnifiedResponse[dict],summary="删除用户",)
def delete_user_api(user_id: int,
                    db: Session = Depends(get_db),
                    current_admin: models.User = Depends(get_current_admin)):
    """删除普通用户，仅管理员可访问。"""
    logger.info(f"收到删除用户请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f"role={current_admin.role}, target_user_id={user_id}")

    delete_result = user_dao.delete_user(db, user_id)
    if not delete_result["success"]:
        if delete_result["reason"] == "admin_forbidden":
            logger.warning(f"删除用户失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                           f"target_user_id={user_id}, reason=不能删除 admin 角色用户")

            raise BusinessException(status_code=403, code=4003, message="不能删除 admin 角色账号")

        logger.error(f"删除用户失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                     f"target_user_id={user_id}, reason=用户不存在")

        raise HTTPException(status_code=404, detail="用户不存在")

    logger.success(f"删除用户成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"target_user_id={user_id}")

    return schemas.UnifiedResponse(data={"message": "删除成功", "user_id": user_id})
