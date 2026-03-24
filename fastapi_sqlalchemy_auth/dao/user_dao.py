from typing import List, Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from core.logger import get_logger
from dao import role_dao
import models
import schemas
from utils.auth import get_password_hash

logger = get_logger()

# C: Create 创建用户
# 通过角色名查询 role_id，避免路由层直接写死角色主键。
def create_user(db: Session, user: schemas.UserCreate, role_name: str = "user") -> models.User:
    """创建用户并写入关联角色。"""
    hashed_pwd = get_password_hash(user.password)
    role = role_dao.get_role_by_name(db, role_name)
    if role is None:
        logger.error(f"数据层创建用户失败: username={user.username}, reason=角色不存在, role={role_name}")
        raise ValueError(f"角色不存在: {role_name}")

    try:
        logger.info(f"数据层创建用户: username={user.username}, email={user.email}, role={role_name}")
        db_user = models.User(
            username=user.username,
            hashed_password=hashed_pwd,
            role_id=role.id,
            age=user.age,
            email=user.email,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.success(f"数据层创建用户成功: user_id={db_user.id}, username={db_user.username}, role={db_user.role}")
        return db_user
    except Exception as e:
        logger.exception(f"数据层创建用户异常: username={user.username}, email={user.email}, error={e}")
        db.rollback()
        raise

# R: Read 根据ID查询查询角色关系 Optional表示 models | None
def get_user_with_role(db: Session, user_id: int) -> Optional[models.User]:
    """根据用户 ID 查询用户及其角色关系。"""
    logger.info(f"数据层查询用户角色关系: user_id={user_id}")
    # 查询User表的时候同时连接查询Role表，避免后续响应序列化时再懒加载。一次性加载关联数据
    stmt = select(models.User).options(joinedload(models.User.role_info)).where(models.User.id == user_id)
    return db.scalar(stmt)


# R: Read 按 ID 查询，同时预加载角色，避免后续响应序列化时再懒加载。一次性加载关联数据
def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """根据用户 ID 查询单个用户。"""
    logger.info(f"数据层按ID查询用户: user_id={user_id}")
    stmt = select(models.User).options(joinedload(models.User.role_info)).where(models.User.id == user_id)
    return db.scalar(stmt)

# R: Read 按名字查询
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """根据用户名查询用户。"""
    logger.info(f"数据层按用户名查询用户: username={username}")
    stmt = select(models.User).options(joinedload(models.User.role_info)).where(models.User.username == username)
    return db.scalar(stmt)

# R: Read 按邮箱查询
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """根据邮箱查询用户。"""
    logger.info(f"数据层按邮箱查询用户: email={email}")
    stmt = select(models.User).options(joinedload(models.User.role_info)).where(models.User.email == email)
    return db.scalar(stmt)


# R: Read 分页查询列表，并返回总数。
def get_user_list(db: Session, page: int = 1, page_size: int = 10) -> tuple[List[models.User], int]:
    """分页查询用户列表，并返回总条数。"""
    if page_size <= 0:
        page_size = 10

    logger.info(f"数据层分页查询用户列表: page={page}, page_size={page_size}")
    offset = (page - 1) * page_size
    stmt = select(models.User).options(joinedload(models.User.role_info)).offset(offset).limit(page_size)
    # 1. 显式转换为 list
    items = list(db.scalars(stmt).all())
    count_stmt = select(func.count()).select_from(models.User)
    # 2. 显式转换为 int，消除 None | Any 的推断
    total = int(db.scalar(count_stmt) or 0)
    logger.success(f"数据层分页查询用户列表成功: returned_count={len(items)}, total={total}")
    return items, total


# R: Read 模糊查询
def search_users(db: Session, keyword: str) -> Sequence[models.User]:
    """按用户名或邮箱关键字模糊查询。"""
    logger.info(f"数据层模糊查询用户: keyword={keyword}")
    stmt = (select(models.User).options(joinedload(models.User.role_info))
            .where(or_(models.User.username.contains(keyword), models.User.email.contains(keyword))))
    users = db.scalars(stmt).all()
    logger.success(f"数据层模糊查询用户成功: keyword={keyword}, returned_count={len(users)}")
    return users


# U: Update 更新用户
def update_user(db: Session, db_user: models.User, user_update: schemas.UserUpdate) -> models.User:
    # 这里把 Pydantic 的增量更新数据转成字典，统一循环写回 ORM 对象。
    update_data = user_update.model_dump(exclude_unset=True)
    logger.info(f"数据层更新用户: user_id={db_user.id}, fields={list(update_data.keys())}")
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    logger.success(f"数据层更新用户成功: user_id={db_user.id}")
    return db_user


# U: Update 重置密码
def update_user_password(db: Session, db_user: models.User, new_hashed_password: str) -> models.User:
    """更新用户密码并持久化。"""
    logger.info(f"数据层重置密码: user_id={db_user.id}, username={db_user.username}")
    db_user.hashed_password = new_hashed_password
    db.commit()
    db.refresh(db_user)
    logger.success(f"数据层重置密码成功: user_id={db_user.id}")
    return db_user


# D: Delete 删除用户
def delete_user(db: Session, db_user: models.User) -> None:
    logger.info(f"数据层删除用户: user_id={db_user.id}, username={db_user.username}")
    db.delete(db_user)
    db.commit()
    logger.success(f"数据层删除用户成功: user_id={db_user.id}")

# 更新用户头像
def update_user_avatar(db: Session, db_user: models.User, avatar_url: str) -> models.User:
    # 更新用户头像
    logger.info(f"数据层更新头像: user_id={db_user.id}, username={db_user.username}")
    db_user.avatar_url = avatar_url
    db.commit()
    db.refresh(db_user)
    logger.success(f"数据层更新头像成功: user_id={db_user.id}")
    return db_user
