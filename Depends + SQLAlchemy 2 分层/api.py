from datetime import timedelta
from fastapi import APIRouter,Depends,HTTPException,Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import crud
import models
import schemas
from database import get_db
from password_utils import verify_password
from security import (
create_access_token,
ACCESS_TOKEN_EXPIRE_MINUTES,
get_current_user,
get_current_admin
)
from logger_config import get_logger
# 配置日志
logger = get_logger()

# 创建路由对象
router = APIRouter(prefix="/users",tags=["用户管理"])
# 登录
@router.post("/token", response_model=schemas.Token, summary="登录获取Token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    logger.info(f"收到登录请求: username={form_data.username}")
    # 1.查找用户
    user = crud.get_user_by_username(db, username=form_data.username)
    # 2.验证用户和密码
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.error(f"登录失败: username={form_data.username}, reason=用户名或密码错误")
        raise HTTPException(
            status_code=400,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # 3.创建Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.success(f"登录成功: user_id={user.id}, username={user.username}, role={user.role}")
    return {"access_token": access_token,"token_type":"bearer"}

# 创建用户
@router.post("", response_model=schemas.UnifiedResponse[schemas.UserResponse], summary="创建新用户")
def create_user_api(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"收到创建用户请求: username={user.username}, email={user.email}")
    if crud.get_user_by_username(db, user.username):
        logger.error(f"创建用户失败: username={user.username}, reason=用户名已存在")
        raise HTTPException(status_code=400,detail="用户名已存在")
    if crud.get_user_by_email(db, user.email):
        logger.error(f"创建用户失败: username={user.username}, email={user.email}, reason=邮箱已存在")
        raise HTTPException(status_code=400,detail="邮箱已存在")
    # 这里强制role = "user",防止有人通过接口直接注册管理员
    db_user = crud.create_user(db,user,role="user")
    logger.success(f"创建用户成功: user_id={db_user.id}, username={db_user.username}, role={db_user.role}")
    return schemas.UnifiedResponse(data=db_user)

# 按ID查询用户 增加Depends(get_current_user)保护
@router.get("/{user_id}", response_model=schemas.UnifiedResponse[schemas.UserResponse], summary="根据ID查询用户")
def get_user_api(
        user_id: int,
        db:Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user) # 新增依赖注入
):
    logger.info(
        f"收到查询用户请求: operator_id={current_user.id}, operator={current_user.username}, "
        f"role={current_user.role}, target_user_id={user_id}"
    )
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        logger.error(
            f"查询用户失败: operator_id={current_user.id}, operator={current_user.username}, "
            f"target_user_id={user_id}, reason=用户不存在"
        )
        raise HTTPException(status_code=404, detail="用户不存在")

    # 权限判断：如果不是管理人员，不能看别人信息
    if db_user.id != current_user.id and current_user.role != "admin":
        logger.error(
            f"查询用户被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
            f"target_user_id={user_id}, reason=无权查看他人信息"
        )
        raise HTTPException(status_code=403,detail="无权查看他人信息")
    logger.success(
        f"查询用户成功: operator_id={current_user.id}, operator={current_user.username}, "
        f"target_user_id={user_id}"
    )
    return schemas.UnifiedResponse(data=db_user)

# 分页查询
@router.get("", response_model=schemas.UnifiedResponse[List[schemas.UserResponse]], summary="分页查询用户列表")
def get_user_list_api(
        page: int = 1,
        page_size: int = 10,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_admin)
):
    logger.info(
        f"收到分页查询用户列表请求: operator_id={current_user.id}, operator={current_user.username}, "
        f"role={current_user.role}, page={page}, page_size={page_size}"
    )
    users = crud.get_user_list(db, page, page_size)
    logger.success(
        f"分页查询用户列表成功: operator_id={current_user.id}, operator={current_user.username}, "
        f"returned_count={len(users)}"
    )
    return schemas.UnifiedResponse(data=users)

# 模糊查询
@router.get("/search/", response_model=schemas.UnifiedResponse[List[schemas.UserResponse]], summary="模糊查询用户")
def search_users_api(
        keyword: str = Query(..., min_length=1, description="搜索关键词"),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_admin)
):
    logger.info(
        f"收到模糊查询用户请求: operator_id={current_user.id}, operator={current_user.username}, "
        f"role={current_user.role}, keyword={keyword}"
    )
    users = crud.search_users(db, keyword)
    logger.success(
        f"模糊查询用户成功: operator_id={current_user.id}, operator={current_user.username}, "
        f"keyword={keyword}, returned_count={len(users)}"
    )
    return schemas.UnifiedResponse(data=users)

# 更新用户 自己能改基本信息，管理员能改全部，包括role
@router.put("/{user_id}", response_model=schemas.UnifiedResponse[schemas.UserResponse], summary="更新用户信息")
def update_user_api(
        user_id: int,
        user_update: schemas.UserUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    logger.info(
        f"收到更新用户请求: operator_id={current_user.id}, operator={current_user.username}, "
        f"role={current_user.role}, target_user_id={user_id}"
    )
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        logger.error(
            f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
            f"target_user_id={user_id}, reason=用户不存在"
        )
        raise HTTPException(status_code=404, detail="用户不存在")

    # 1.基础权限：只能改自己，除非是管理员
    if db_user.id != current_user.id and current_user.role != "admin":
        logger.error(
            f"更新用户被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
            f"target_user_id={user_id}, reason=无权修改他人信息"
        )
        raise HTTPException(status_code=403, detail="无权修改他人信息")

    # 2.高级权限
    if user_update.role is not None and current_user.role !="admin":
        logger.error(
            f"更新用户角色被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
            f"target_user_id={user_id}, reason=无管理员权限"
        )
        raise HTTPException(status_code=403, detail="无权修改用户角色")

    # 3.唯一校验
    if user_update.username and user_update.username != db_user.username:
        if crud.get_user_by_username(db, user_update.username):
            logger.error(
                f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                f"target_user_id={user_id}, username={user_update.username}, reason=用户名已被占用"
            )
            raise HTTPException(status_code=400, detail="用户名已被占用")
    if user_update.email and user_update.email != db_user.email:
        if crud.get_user_by_email(db, user_update.email):
            logger.error(
                f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                f"target_user_id={user_id}, email={user_update.email}, reason=邮箱已被占用"
            )
            raise HTTPException(status_code=400, detail="邮箱已被占用")

    updated_user = crud.update_user(db, user_id, user_update)
    logger.success(
        f"更新用户成功: operator_id={current_user.id}, operator={current_user.username}, "
        f"target_user_id={user_id}"
    )
    return schemas.UnifiedResponse(data=updated_user)


@router.delete("/{user_id}", response_model=schemas.UnifiedResponse[dict], summary="删除用户")
def delete_user_api(
        user_id: int,
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)
):
    logger.info(
        f"收到删除用户请求: operator_id={current_admin.id}, operator={current_admin.username}, "
        f"role={current_admin.role}, target_user_id={user_id}"
    )
    if not crud.delete_user(db, user_id):
        logger.error(
            f"删除用户失败: operator_id={current_admin.id}, operator={current_admin.username}, "
            f"target_user_id={user_id}, reason=用户不存在"
        )
        raise HTTPException(status_code=404, detail="用户不存在")
    logger.success(
        f"删除用户成功: operator_id={current_admin.id}, operator={current_admin.username}, "
        f"target_user_id={user_id}"
    )
    return schemas.UnifiedResponse(data={"message": "删除成功", "user_id": user_id})
