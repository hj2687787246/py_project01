from sqlalchemy import select,or_
from sqlalchemy.orm import Session

from models import User
from schemas import UserCreate,UserUpdate
from core.logger import get_logger
from utils.password_utils import get_password_hash

logger = get_logger()

# C:Create 创建用户 新增 role 参数，允许外部指定角色（默认普通用户）
def create_user(db: Session, user: UserCreate, role: str = "user"):
    # 将 user.password 哈希后再存入模型
    hashed_pwd = get_password_hash(user.password)
    try:
        logger.info(f"数据层创建用户: username={user.username}, email={user.email}, role={role}")
        db_user = User(
            username=user.username,
            hashed_password=hashed_pwd,
            role= role,
            age=user.age,
            email=user.email
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

# R:Read 按ID查询
def get_user_by_id(db:Session,user_id:int):
    return db.get(User,user_id)

# R:Read 按用户名查询
def get_user_by_username(db:Session,username:str):
    stmt = select(User).where(User.username == username)
    return db.scalar(stmt)

# R:Read 按邮箱查询
def get_user_by_email(db:Session,email:str):
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)

# R:Read 分页查询列表
def get_user_list(db:Session,page: int = 1,page_size: int=10):
    if page_size <= 0:
        page_size = 10
    stmt = select(User).offset((page - 1) * page_size).limit(page_size)
    return db.scalars(stmt).all()

# R:Read 模糊查询
def search_users(db: Session,keyword: str):
    stmt = select(User).where(
        or_(
            User.username.contains(keyword),
            User.email.contains(keyword)
        )
    )
    return db.scalars(stmt).all()

# U:Update 更新用户
def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        logger.warning(f"数据层更新用户失败: user_id={user_id}, reason=用户不存在")
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    logger.info(f"数据层更新用户: user_id={user_id}, fields={list(update_data.keys())}")
    for key,value in update_data.items():
        setattr(db_user,key,value)
    db.commit()
    db.refresh(db_user)
    logger.success(f"数据层更新用户成功: user_id={user_id}")
    return db_user

# D:Delete 删除用户
def delete_user(db: Session, user_id: int):
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
