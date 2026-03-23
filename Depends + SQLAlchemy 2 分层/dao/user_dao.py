from typing import Sequence, Optional, TypedDict

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from core.logger import get_logger
from dao import role_dao
from models import User
from schemas import UserCreate, UserUpdate
from utils.password_utils import get_password_hash

logger = get_logger()


class DeleteUserResult(TypedDict):
    success: bool
    reason: str


# C: Create 创建用户
# 通过角色名查询 role_id，避免路由层直接写死角色主键。
def create_user(db: Session, user: UserCreate, role_name: str = "user") -> User:
    """创建用户并写入关联角色。"""
    hashed_pwd = get_password_hash(user.password)
    role = role_dao.get_role_by_name(db, role_name)
    if role is None:
        logger.error(f"数据层创建用户失败: username={user.username}, reason=角色不存在, role={role_name}")
        raise ValueError(f"角色不存在: {role_name}")

    try:
        logger.info(f"数据层创建用户: username={user.username}, email={user.email}, role={role_name}")
        db_user = User(
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

# R: Read 根据ID查询查询角色关系
def get_user_with_role(db: Session, user_id: int) -> Optional[User]:
    """根据用户 ID 查询用户及其角色关系。"""
    logger.info(f"数据层查询用户角色关系: user_id={user_id}")
    stmt = select(User).options(joinedload(User.role_info)).where(User.id == user_id)
    return db.scalar(stmt)


# R: Read 按 ID 查询，同时预加载角色，避免后续响应序列化时再懒加载。
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据用户 ID 查询单个用户。"""
    logger.info(f"数据层按ID查询用户: user_id={user_id}")
    stmt = select(User).options(joinedload(User.role_info)).where(User.id == user_id)
    return db.scalar(stmt)

# R: Read 按名字查询
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名查询用户。"""
    logger.info(f"数据层按用户名查询用户: username={username}")
    stmt = select(User).options(joinedload(User.role_info)).where(User.username == username)
    return db.scalar(stmt)

# R: Read 按邮箱查询
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱查询用户。"""
    logger.info(f"数据层按邮箱查询用户: email={email}")
    stmt = select(User).options(joinedload(User.role_info)).where(User.email == email)
    return db.scalar(stmt)


# R: Read 分页查询列表，并返回总数。
def get_user_list(db: Session, page: int = 1, page_size: int = 10) -> tuple[Sequence[User], int]:
    """分页查询用户列表，并返回总条数。"""
    if page_size <= 0:
        page_size = 10

    logger.info(f"数据层分页查询用户列表: page={page}, page_size={page_size}")
    offset = (page - 1) * page_size
    stmt = select(User).options(joinedload(User.role_info)).offset(offset).limit(page_size)
    items = db.scalars(stmt).all()

    count_stmt = select(func.count()).select_from(User)
    total = db.scalar(count_stmt) or 0
    logger.success(f"数据层分页查询用户列表成功: returned_count={len(items)}, total={total}")
    return items, total


# R: Read 模糊查询
def search_users(db: Session, keyword: str) -> Sequence[User]:
    """按用户名或邮箱关键字模糊查询。"""
    logger.info(f"数据层模糊查询用户: keyword={keyword}")
    stmt = (select(User).options(joinedload(User.role_info))
            .where(or_(User.username.contains(keyword), User.email.contains(keyword))))
    users = db.scalars(stmt).all()
    logger.success(f"数据层模糊查询用户成功: keyword={keyword}, returned_count={len(users)}")
    return users


# U: Update 更新用户
def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """更新用户可变字段。"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        logger.warning(f"数据层更新用户失败: user_id={user_id}, reason=用户不存在")
        return None

    # 这里把 Pydantic 的增量更新数据转成字典，统一循环写回 ORM 对象。
    update_data = user_update.model_dump(exclude_unset=True)
    logger.info(f"数据层更新用户: user_id={user_id}, fields={list(update_data.keys())}")
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    logger.success(f"数据层更新用户成功: user_id={user_id}")
    return db_user


# U: Update 重置密码
def update_user_password(db: Session, db_user: User, hashed_password: str) -> User:
    """更新用户密码并持久化。"""
    logger.info(f"数据层重置密码: user_id={db_user.id}, username={db_user.username}")
    db_user.hashed_password = hashed_password
    db.commit()
    db.refresh(db_user)
    logger.success(f"数据层重置密码成功: user_id={db_user.id}")
    return db_user


# D: Delete 删除用户
def delete_user(db: Session, user_id: int) -> DeleteUserResult:
    """删除普通用户，管理员账号禁止删除。"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        logger.warning(f"数据层删除用户失败: user_id={user_id}, reason=用户不存在")
        return {"success": False, "reason": "not_found"}

    if db_user.role == "admin":
        logger.warning(f"数据层删除用户失败: user_id={user_id}, reason=该角色为管理员")
        return {"success": False, "reason": "admin_forbidden"}

    logger.info(f"数据层删除用户: user_id={user_id}, username={db_user.username}")
    db.delete(db_user)
    db.commit()
    logger.success(f"数据层删除用户成功: user_id={user_id}")
    return {"success": True, "reason": "deleted"}

# 更新用户头像
def update_user_avatar(db: Session, user_id: int, avatar_url: str) -> User | None:
    """更新用户头像地址。"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    # 更新用户头像
    db_user.avatar_url = avatar_url
    db.commit()
    db.refresh(db_user)
    return db_user