from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from core.logger import get_logger
from dao import user_dao as user_crud
from session.db_session import get_db
from utils.security import get_current_admin

logger = get_logger()
router = APIRouter(prefix="/roles", tags=["角色管理"])


# 创建管理员账号
@router.post("/admin/users",response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="创建管理员账号")
def create_admin_user_api(user: schemas.UserCreate,
                          db: Session = Depends(get_db),
                          current_admin: models.User = Depends(get_current_admin)):
    """由管理员创建新的管理员账号。"""
    logger.info(f"收到创建管理员账号请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f""f"username={user.username}, email={user.email}")

    if user_crud.get_user_by_username(db, user.username):
        logger.error(f"创建管理员账号失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                     f"username={user.username}, reason=用户名已存在")

        raise BusinessException(status_code=400, code=4001, message="用户名已存在")
    if user_crud.get_user_by_email(db, user.email):
        logger.error(f"创建管理员账号失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                     f"email={user.email}, reason=邮箱已存在")

        raise BusinessException(status_code=400, code=4002, message="邮箱已存在")

    # 管理员创建管理员时，统一走角色名映射，避免写死 role_id。
    db_user = user_crud.create_user(db, user, role_name="admin")
    logger.success(f"创建管理员账号成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"user_id={db_user.id}, username={db_user.username}")

    return schemas.UnifiedResponse(data=db_user)
