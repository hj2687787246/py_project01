from datetime import timedelta

from fastapi import APIRouter,Depends,HTTPException,Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import crud
import models
import schemas
from database import get_db
from security import (
verify_password,
create_access_token,
ACCESS_TOKEN_EXPIRE_MINUTES,
get_current_user
)

# 创建路由对象
router = APIRouter(prefix="/users",tags=["用户管理"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    # 1.查找用户
    user = crud.get_user_by_username(db, username=form_data.username)
    # 2.验证用户和密码
    if not user or not verify_password(form_data.password, user.hashed_password):
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

    return {"access_token": access_token,"token_type":"bearer"}

# 创建用户
@router.post("", response_model=schemas.UnifiedResponse[schemas.UserResponse], summary="创建新用户")
def create_user_api(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400,detail="用户名已存在")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400,detail="邮箱已存在")
    db_user = crud.create_user(db, user)

    return schemas.UnifiedResponse(data=db_user)
# 按ID查询用户 增加Depends(get_current_user)保护
@router.get("/{user_id}", response_model=schemas.UnifiedResponse[schemas.UserResponse], summary="根据ID查询用户")
def get_user_api(
        user_id: int,
        db:Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user) # 新增依赖注入
):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="用户不存在")
    return schemas.UnifiedResponse(data=db_user)

# 分页查询
@router.get("", response_model=schemas.UnifiedResponse[List[schemas.UserResponse]], summary="分页查询用户列表")
def get_user_list_api(
        page: int = 1,
        page_size: int = 10,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    users = crud.get_user_list(db, page, page_size)
    return schemas.UnifiedResponse(data=users)


@router.get("/search/", response_model=schemas.UnifiedResponse[List[schemas.UserResponse]], summary="模糊查询用户")
def search_users_api(
        keyword: str = Query(..., min_length=1, description="搜索关键词"),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    users = crud.search_users(db, keyword)
    return schemas.UnifiedResponse(data=users)


@router.put("/{user_id}", response_model=schemas.UnifiedResponse[schemas.UserResponse], summary="更新用户信息")
def update_user_api(
        user_id: int,
        user_update: schemas.UserUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user_update.username and user_update.username != db_user.username:
        if crud.get_user_by_username(db, user_update.username):
            raise HTTPException(status_code=400, detail="用户名已被占用")

    if user_update.email and user_update.email != db_user.email:
        if crud.get_user_by_email(db, user_update.email):
            raise HTTPException(status_code=400, detail="邮箱已被占用")

    updated_user = crud.update_user(db, user_id, user_update)
    return schemas.UnifiedResponse(data=updated_user)


@router.delete("/{user_id}", response_model=schemas.UnifiedResponse[dict], summary="删除用户")
def delete_user_api(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="用户不存在")
    return schemas.UnifiedResponse(data={"message": "删除成功", "user_id": user_id})