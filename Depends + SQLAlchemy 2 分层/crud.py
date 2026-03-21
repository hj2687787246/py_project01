from sqlalchemy import select,or_
from sqlalchemy.orm import Session

from models import User
from schemas import UserCreate,UserUpdate
from security import get_password_hash # 新增

# C:Create 创建用户
def create_user(db: Session, user: UserCreate):
    # 将 user.password 哈希后再存入模型
    hashed_pwd = get_password_hash(user.password)
    try:
        print(f"创建用户: {user}")
        db_user = User(
            username=user.username,
            hashed_password=hashed_pwd,
            age=user.age,
            email=user.email
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print(f"用户创建成功: {db_user.id}")
        return db_user
    except Exception as e:
        print(f"创建用户时出错: {e}")
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
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    for key,value in update_data.items():
        setattr(db_user,key,value)
    db.commit()
    db.refresh(db_user)
    return db_user

# D:Delete 删除用户
def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True