from dataclasses import field

from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy import create_engine,String,select
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,sessionmaker,Session
from pydantic import BaseModel,Field
from typing import List,Optional
# 1.数据库基本配置
# SQLite数据库链接地址
SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi_test.db"

# 创建数据库引擎，connect_args为SQLite专属配置，解决多线程问题
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread": False}
)
# 会话工厂：用于生成数据库操作会话
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# ORM模型基类：所有数据库表模型必须继承该类
class Base(DeclarativeBase):
    pass

# 2.定义ORM模型，也就是数据库表结构
class User(Base):
    __tablename__ = "users"#数据库表名

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True,comment="用户主键ID")
    username:Mapped[str] = mapped_column(String(50),unique=True,nullable=False,comment="用户名")
    age:Mapped[int] = mapped_column(comment="年龄")
    email:Mapped[str] = mapped_column(String(100),unique=True,nullable=False,comment="邮箱")
# 自动创建数据库，首次运行生成fastapi_test.db文件和users表
Base.metadata.create_all(bind=engine)

# 3.Pydantic Schema（请求/响应验证）
# 创建用户请求体
class UserCreate(BaseModel):
    username: str = Field(min_length=3,max_length=50,description="用户名")
    age: Optional[int] = Field(ge=0,le=150,description="年龄")
    email:str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",description="邮箱地址")

# 更新用户请求体
class UserUpdate(BaseModel):
    username:Optional[str] =Field(min_length=3,max_length=50,default=None)
    age:Optional[int] = Field(ge=0,le=150,default=None)
    email:Optional[str] = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",default=None)

# 用户响应体
class UserResponse(UserCreate):
    id:int
    # 告诉Pydantic从ORM模型中获取属性
    class Config:
        from_attributes = True # Pydantic 2.x 标准写法，支持ORM模型直接转响应对象

# 4.核心：数据库会话依赖（Depends实现）
def get_db():
    # 请求进入时创建数据库会话
    with SessionLocal() as db:
        yield db# 将会话注入到接口中

# 5.CRUD操作封装

# C.Create创建用户
def create_user(db:Session,user:UserCreate):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit() # 提交事务到数据库
    db.refresh(db_user) # 刷新数据库，获取自增主键ID
    return db_user

# R.Read 按ID查询单个用户
def get_user_by_id(db:Session,user_id:int):
    return db.get(User,user_id) # 主键查询推荐写法，性能最优

# R.Read 按用户名查询单个用户
def get_user_by_username(db:Session,username:str):
    stmt = select(User).where(User.username == username)
    # db.scalar()：返回单个值
    return db.scalar(stmt)
# R.Read 按邮箱查询单个用户
def get_user_by_email(db:Session,email:str):
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)

# R.Read 分页查询用户列表
def get_user_list(db: Session,page:int = 1,page_size:int=10):
    stmt = select(User).offset((page - 1) * page_size).limit(page_size)
    # db.scalars 返回单个列的结果集
    return db.scalars(stmt).all()

# U.Update 更新用户
def update_user(db:Session,user_id:int,user_update: UserUpdate):
    # 传入id查询用户
    db_user = get_user_by_id(db,user_id)
    if not db_user:
        return None
    # 仅更新用户传入的字段，实现局部更新
    update_date = user_update.model_dump(exclude_unset=True)
    for key,value in update_date.items():
        # 使用setattr方法设置属性值
        setattr(db_user,key,value)
    db.commit()
    db.refresh(db_user)
    return db_user

# D:Delete 删除用户
def delete_user(db:Session,user_id:int):
    db_user = get_user_by_id(db,user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

#6.FastAPI接口实现
app = FastAPI(title="用户CRUD管理系统",description="Depends + SQLAlchemy 2.0 完整示例")

# 创建用户
@app.post("/users/",response_model=UserResponse,summary="创建新用户")
def create_user_api(user:UserCreate,db:Session = Depends(get_db)):
    # 校验用户名唯一性
    if get_user_by_username(db,user.username):
        raise HTTPException(status_code=400,detail="用户名已存在")
    elif get_user_by_email(db,user.email):
        raise HTTPException(status_code=400, detail="邮箱已存在")
    return create_user(db,user)

# 按ID查询用户
@app.get("/users/{user_id}",response_model=UserResponse,summary="根据ID查询用户")
def get_user_api(user_id:int,db:Session = Depends(get_db)):
    db_user= get_user_by_id(db,user_id)
    if not db_user:
        raise HTTPException(status_code=404,detail="用户不存在")
    return db_user

# 分页查询用户列表
@app.get("/users/",response_model=List[UserResponse],summary="分页查询用户列表")
def get_user_list_api(page:int = 1,page_size:int = 10,db:Session=Depends(get_db)):
    return get_user_list(db,page,page_size)

# 更新用户
@app.put("/users/{user_id}",response_model=UserResponse,summary="更新用户信息")
def update_user_api(user_id:int,user_update:UserUpdate,db:Session = Depends(get_db)):
    db_user = update_user(db,user_id,user_update)
    if not db_user:
        raise HTTPException(status_code=404,detail="用户不存在")
    return db_user

# 删除用户
@app.delete("/users/{user_id}",summary="删除用户")
def delete_user_api(user_id:int,db:Session = Depends(get_db)):
    if not delete_user(db,user_id):
        raise HTTPException(status_code=404,detail="用户不存在")
    return {"message":"删除成功","user_id":user_id}