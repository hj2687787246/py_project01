from typing import List

from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from core.logger import get_logger
from services import role_service
from session.db_session import get_db
from utils.security import get_current_admin, get_current_user

logger = get_logger()
router = APIRouter(prefix="/roles", tags=["角色管理"])


# 创建管理员账号
@router.post("/admin/users",response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="创建管理员账号")
def create_admin_user_api(user: schemas.UserCreate,
                          db: Session = Depends(get_db),
                          current_admin: models.User = Depends(get_current_admin)):
    """由管理员创建新的管理员账号。"""
    logger.info(f"收到创建管理员账号请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f"username={user.username}, email={user.email}")

    try:
        # 管理员创建管理员时，统一走角色名映射，避免写死 role_id。
        db_user = role_service.create_admin_user(db, user)
    except BusinessException as exc:
        if exc.code == 4001:
            logger.error(f"创建管理员账号失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                         f"username={user.username}, reason=用户名已存在")
        elif exc.code == 4002:
            logger.error(f"创建管理员账号失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                         f"email={user.email}, reason=邮箱已存在")
        raise

    logger.success(f"创建管理员账号成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"user_id={db_user.id}, username={db_user.username}")

    return schemas.UnifiedResponse(data=db_user)
# 新增角色
@router.post("", response_model=schemas.UnifiedResponse[schemas.RoleResponse])
def create_role_api(role: schemas.RoleCreate,
                    db: Session = Depends(get_db),
                    current_admin: models.User = Depends(get_current_admin)):
    logger.info(f"收到创建角色请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f"role_name={role.name}")
    try:
        new_role = role_service.create_role(db, role)
    except BusinessException:
        logger.warning(f"创建角色失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                       f"role_name={role.name}, reason=角色已存在")
        raise
    logger.success(f"创建角色成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"role_id={new_role.id}, role_name={new_role.name}")
    return schemas.UnifiedResponse(data=new_role)

# 查询所有角色
@router.get("", response_model=schemas.UnifiedResponse[List[schemas.RoleResponse]])
def get_all_roles_api(db: Session = Depends(get_db), current_admin: models.User = Depends(get_current_admin)):
    logger.info(f"收到查询全部角色请求: operator_id={current_admin.id}, operator={current_admin.username}")
    roles = role_service.get_all_roles(db)
    logger.success(f"查询全部角色成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"count={len(roles)}")
    return schemas.UnifiedResponse(data=roles)

# 重置密码
@router.post("/{user_id}/reset-password", response_model=schemas.UnifiedResponse[dict])
def reset_password_api(user_id: int,
                   new_password: str = Body(..., min_length=6),
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    logger.info(f"收到重置密码请求: operator_id={current_user.id}, operator={current_user.username}, "
                f"target_user_id={user_id}")
    try:
        # 更新密码
        role_service.reset_password(db, user_id, current_user, new_password)
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
