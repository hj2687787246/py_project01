import os
from typing import List

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Body
from sqlalchemy.orm import Session
import models
import schemas
from core.exceptions import BusinessException
from core.logger import get_logger
from schemas.user_schema import UserLogin
from services import user_service
from session.db_session import get_db
from utils.auth import get_current_admin, get_current_user
from config import Settings,get_settings

logger = get_logger()
router = APIRouter(prefix="/users", tags=["用户管理"])

# 限流
limiter = Limiter(key_func=get_remote_address)
if hasattr(router, "state"):
    router.state.limiter = limiter
if hasattr(router, "add_exception_handler"):
    router.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# 登录
@router.post("/login", response_model=schemas.UnifiedResponse, summary="登录获取 Token")
# 限流接口 防止暴力请求 比如1分钟最多5次
# 测试环境关闭限流
@(limiter.limit("5/minute") if os.getenv("TESTING") != "1" else (lambda func: func))
def login_for_access_token(request: Request, user_data: UserLogin,db: Session = Depends(get_db),settings: Settings = Depends(get_settings)):
    logger.info(f"收到登录请求: username={user_data.username}")
    try:
        user, access_token, refresh_token = user_service.login_user(db, user_data.username, user_data.password, settings)
    except HTTPException:
        logger.error(f"登录失败: username={user_data.username}, reason=账号或密码错误")
        raise
    logger.success(f"登录成功: user_id={user.id}, username={user.username}, role={user.role}")
    token_data = schemas.TokenResponse(access_token=access_token,refresh_token=refresh_token).model_dump()
    return schemas.UnifiedResponse(data=token_data)

# 重置密码
@router.post("/{user_id}/reset-password", response_model=schemas.UnifiedResponse[dict],summary="重置密码")
def reset_password_api(user_id: int,
                   new_password: str = Body(..., min_length=6),
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    logger.info(f"收到重置密码请求: operator_id={current_user.id}, operator={current_user.username}, "
                f"target_user_id={user_id}")
    try:
        # 更新密码
        user_service.reset_password(db, user_id, current_user, new_password)
    except HTTPException as exc:
        if exc.status_code == 404:
            logger.warning(f"重置密码失败: operator_id={current_user.id}, operator={current_user.username}, "
                           f"target_user_id={user_id}, reason=用户不存在")
        elif exc.status_code == 403:
            logger.warning(f"重置密码失败: operator_id={current_user.id}, operator={current_user.username}, "
                           f"target_user_id={user_id}, reason=无权重置他人密码")
        raise
    logger.success(f"重置密码成功: operator_id={current_user.id}, operator={current_user.username}, "
                   f"target_user_id={user_id}")
    return schemas.UnifiedResponse(data={"message":"密码重置成功"})

# 刷新Token
@router.post("/auth/refresh", response_model=schemas.UnifiedResponse, summary="刷新 Access Token")
def refresh_token_api(
    request: schemas.RefreshTokenRequest,
    settings: Settings = Depends(get_settings)
):
    logger.info("收到刷新Token请求")
    try:
        # 刷新令牌
        new_access_token = user_service.get_new_access_token(request,settings)
    except HTTPException as exc:
        logger.error(f"刷新Token失败: reason={exc.detail}")
        raise
    logger.success("刷新Token成功")
    return schemas.UnifiedResponse(data={"access_token": new_access_token, "token_type": "bearer"})


# 创建用户
@router.post("",response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="创建新用户")
def create_user_api(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """创建普通用户账号。"""
    logger.info(f"收到创建用户请求: username={user.username}, email={user.email}")

    try:
        # 普通注册入口固定创建 user 角色，避免通过该接口直接注册管理员。
        db_user = user_service.create_user(db, user)
    except BusinessException as exc:
        if exc.code == 4001:
            logger.error(f"创建用户失败: username={user.username}, reason=用户名已存在")
        elif exc.code == 4002:
            logger.error(f"创建用户失败: username={user.username}, email={user.email}, reason=邮箱已存在")
        elif exc.code == 4003:
            logger.error(f"创建用户失败: username={user.username}, password={user.password}, reason=密码至少8位，包含大小写、数字、特殊字符")
        raise
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

    try:
        db_user = user_service.get_user_detail(db, user_id, current_user)
    except HTTPException as exc:
        if exc.status_code == 404:
            logger.error(f"查询用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=用户不存在")
        elif exc.status_code == 403:
            logger.error(f"查询用户被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=无权查看他人信息")
        raise

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

    users, total = user_service.get_user_list(db, page_params.page, page_params.page_size)
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

    users = user_service.search_users(db, keyword)
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

    try:
        updated_user = user_service.update_user(db, user_id, user_update, current_user)
    except HTTPException as exc:
        if exc.status_code == 404:
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=用户不存在")
        elif exc.status_code == 403:
            logger.error(f"更新用户被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=无权修改他人信息")
        raise
    except BusinessException as exc:
        if exc.code == 4004:
            logger.error(f"更新用户角色被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=无管理员权限")
        elif exc.code == 4005:
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, role_id={user_update.role_id}, reason=角色不存在")
        elif exc.code == 4001:
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, username={user_update.username}, reason=用户名已被占用")
        elif exc.code == 4002:
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, email={user_update.email}, reason=邮箱已被占用")
        raise

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

    try:
        user_service.delete_user(db, user_id)
    except BusinessException:
        logger.warning(f"删除用户失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                       f"target_user_id={user_id}, reason=不能删除 admin 角色用户")
        raise
    except HTTPException:
        logger.error(f"删除用户失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                     f"target_user_id={user_id}, reason=用户不存在")
        raise

    logger.success(f"删除用户成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"target_user_id={user_id}")

    return schemas.UnifiedResponse(data={"message": "删除成功", "user_id": user_id})


# 上传头像
@router.post("/{user_id}/avatar",response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="上传头像")
def upload_avatar_api(user_id: int,
                      file: UploadFile = File(...,description="头像图片文件"),
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    """上传当前用户头像。"""
    logger.info(f"收到上传头像请求: operator_id={current_user.id}, operator={current_user.username}, "
                f"role={current_user.role}, target_user_id={user_id}, filename={file.filename}, content_type={file.content_type}")

    try:
        updated_user = user_service.upload_avatar(db, user_id, current_user, file)
    except HTTPException as exc:
        if exc.status_code == 404:
            logger.error(f"上传头像失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, filename={file.filename}, reason=用户不存在")
        elif exc.status_code == 403:
            logger.error(f"上传头像被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, filename={file.filename}, reason=无权修改他人头像")
        elif exc.status_code == 400:
            logger.error(f"上传头像失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, filename={file.filename}, content_type={file.content_type}, reason={exc.detail}")
        raise

    logger.success(f"上传头像成功: operator_id={current_user.id}, operator={current_user.username}, "
                   f"target_user_id={user_id}, avatar_url={updated_user.avatar_url}")
    return schemas.UnifiedResponse(data=updated_user)