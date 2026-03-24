from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from core.logger import get_logger
from services import role_service
from session.db_session import get_db
from utils.auth import get_current_admin

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

    # 管理员创建管理员时，统一走角色名映射，避免写死 role_id。
    db_user = role_service.create_admin_user(db, user)
    logger.success(f"创建管理员账号成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"user_id={db_user.id}, username={db_user.username}")

    return schemas.UnifiedResponse(data=db_user)
# 新增角色
@router.post("", response_model=schemas.UnifiedResponse[schemas.RoleResponse],summary="新增角色")
def create_role_api(role: schemas.RoleCreate,
                    db: Session = Depends(get_db),
                    current_admin: models.User = Depends(get_current_admin)):
    logger.info(f"收到创建角色请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f"role_name={role.name}")
    new_role = role_service.create_role(db, role)
    logger.success(f"创建角色成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"role_id={new_role.id}, role_name={new_role.name}")
    return schemas.UnifiedResponse(data=new_role)

# 查询所有角色
@router.get("", response_model=schemas.UnifiedResponse[List[schemas.RoleResponse]],summary="查询所有角色")
def get_all_roles_api(db: Session = Depends(get_db), current_admin: models.User = Depends(get_current_admin)):
    logger.info(f"收到查询全部角色请求: operator_id={current_admin.id}, operator={current_admin.username}")
    roles = role_service.get_all_roles(db)
    logger.success(f"查询全部角色成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"count={len(roles)}")
    return schemas.UnifiedResponse(data=roles)
