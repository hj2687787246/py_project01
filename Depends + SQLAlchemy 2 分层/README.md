# FastAPI 分层项目源码归档

## 文档用途

这份文档用于把 `Depends + SQLAlchemy 2 分层` 项目的目录结构和全部代码文件集中到一个 Markdown 文件里，方便直接发给豆包或其他 AI。

说明:

- 代码文件来源于当前项目实际文件清单，自动收录，不再手工挑选。
- 当前已收录全部文本代码文件：`.env`, `core\__init__.py`, `core\exceptions.py`, `core\logger.py`, `dao\__init__.py`, `dao\role_dao.py`, `dao\user_dao.py`, `main.py`, `models\__init__.py`, `models\role.py`, `models\user.py`, `requirements.txt`, `routers\__init__.py`, `routers\role_routes.py`, `routers\user_routes.py`, `schemas\__init__.py`, `schemas\role_schema.py`, `schemas\user_schema.py`, `services\__init__.py`, `services\role_service.py`, `services\user_service.py`, `session\__init__.py`, `session\db_session.py`, `tests\test_user_system.py`, `utils\__init__.py`, `utils\file_utils.py`, `utils\password_utils.py`, `utils\security.py`。
- 二进制文件只列路径，不展开内容。
- `.env` 中的 `SECRET_KEY` 已脱敏。

## 实际目录结构

```text
Depends + SQLAlchemy 2 分层/
├── .env
├── core
├── __init__.py
├── exceptions.py
├── logger.py
├── dao
├── __init__.py
├── role_dao.py
├── user_dao.py
├── main.py
├── models
├── __init__.py
├── role.py
├── user.py
├── requirements.txt
├── routers
├── __init__.py
├── role_routes.py
├── user_routes.py
├── schemas
├── __init__.py
├── role_schema.py
├── user_schema.py
├── services
├── __init__.py
├── role_service.py
├── user_service.py
├── session
├── __init__.py
├── db_session.py
├── tests
├── test_user_system.py
├── utils
├── __init__.py
├── file_utils.py
├── password_utils.py
├── security.py
├── static
├── avatars
│   ├── 1774315893089.jpg
│   ├── 1774317347273.jpg
│   ├── default.jpg
```

## 二进制文件

- `static\avatars\1774315893089.jpg` (41710 bytes)
- `static\avatars\1774317347273.jpg` (41710 bytes)
- `static\avatars\default.jpg` (48903 bytes)

## 全部代码

### .env

```dotenv
# 密码规则
SECRET_KEY="<your-secret-key>"
# Token 30分钟过期
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库链接地址
SQLALCHEMY_DATABASE_URL="sqlite:///./fastapi_test.db"
```

### core\__init__.py

```python
# 核心能力
from .logger import get_logger
from .exceptions import BusinessException
```

### core\exceptions.py

```python
# 自定义业务异常
class BusinessException(Exception):
    def __init__(self, status_code: int, code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
```

### core\logger.py

```python
# 日志配置文件
import os
from loguru import logger
from datetime import datetime

# 1. 创建日志目录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 2. 配置日志格式和文件
log_file_path = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# 3. 移除默认的 handler，添加自定义配置
logger.remove()
logger.add(
    sink=log_file_path,          # 日志文件路径
    rotation="00:00",            # 每天 0 点分割日志
    retention="30 days",         # 保留 30 天
    level="INFO",                 # 日志级别
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{line} | {message}",
    encoding="utf-8"
)

# 4. 同时也在控制台输出（方便开发调试）
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# 导出 logger 实例
def get_logger():
    return logger
```

### dao\__init__.py

```python
# 数据访问层
# 集中导出 DAO 模块和常用返回结构，便于 service 层复用。
from . import role_dao, user_dao
from .user_dao import DeleteUserResult

__all__ = ["role_dao", "user_dao", "DeleteUserResult"]
```

### dao\role_dao.py

```python
from typing import Optional
from sqlalchemy.orm import Session

from core.exceptions import BusinessException
from models.role import Role

# 获取角色名称
def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """根据角色名查询角色。"""
    return db.query(Role).filter(Role.name == name).first()

# 新增角色
def create_role(db: Session, name: str, description: str | None = None) -> Role:
    """创建角色并写入数据库。"""
    db_role = Role(name=name, description=description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# 查重后新增角色
def create_role_with_check(db: Session, name: str, description: str | None = None) -> Role:
    """先校验是否重复，再创建角色。"""
    db_role = get_role_by_name(db, name)
    if db_role:
        raise BusinessException(400, 4006, "该角色已存在")
    return create_role(db, name, description)

# 获取所有角色信息
def get_all_roles(db: Session) -> list[type[Role]]:
    """查询全部角色。"""
    return db.query(Role).all()
```

### dao\user_dao.py

```python
from typing import Sequence, Optional, TypedDict, List

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from core.logger import get_logger
from dao import role_dao
import models
from schemas import UserCreate, UserUpdate
from utils.password_utils import get_password_hash

logger = get_logger()


class DeleteUserResult(TypedDict):
    success: bool
    reason: str


# C: Create 创建用户
# 通过角色名查询 role_id，避免路由层直接写死角色主键。
def create_user(db: Session, user: UserCreate, role_name: str = "user") -> models.User:
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
def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[models.User]:
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
def update_user_password(db: Session, db_user: models.User, hashed_password: str) -> models.User:
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
def update_user_avatar(db: Session, user_id: int, avatar_url: str) -> models.User | None:
    """更新用户头像地址。"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    # 更新用户头像
    db_user.avatar_url = avatar_url
    db.commit()
    db.refresh(db_user)
    return db_user
```

### main.py

```python
from contextlib import asynccontextmanager
import traceback
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from core.exceptions import BusinessException
from core.logger import get_logger
import schemas
from session.db_session import Base, engine, SessionLocal
from models.role import Role
from models.user import User
from routers import router as users_router

# 配置日志
logger = get_logger()


# FastAPI 启动前执行数据库初始化检查
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表初始化检查完成")
        # 初始化角色数据
        db = SessionLocal()
        try:
            if not db.query(Role).first():
                from dao.role_dao import create_role
                create_role(db, name="admin", description="系统管理员")
                create_role(db, name="user", description="普通用户")
                logger.info("初始化角色数据完成")
            if not db.query(User).first():
                from schemas.user_schema import UserCreate
                from dao.user_dao import create_user
                admin_user = UserCreate(username="admin", password="123456", age=26, email="2687787246@qq.com")
                create_user(db, admin_user, "admin")
                logger.info("初始化管理员账号完成")
        except Exception as e:
            logger.warning(f"初始化角色数据跳过或失败: {e}")
        finally:
            db.close()

    except Exception as e:
        logger.exception(f"数据库表初始化检查失败: {e}")
        raise
    yield


# FastAPI 实例
app = FastAPI(
    title="用户管理系统",
    description="分层版",
    lifespan=lifespan,
)
# 挂载静态文件目录（用于访问头像）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 挂载路由
app.include_router(users_router)

# 捕获自定义业务异常，统一返回业务错误格式
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    logger.error(f"业务异常: {exc}")
    logger.error(f"异常详情: {traceback.format_exc()}")
    return JSONResponse(
        status_code=exc.status_code,
        content=schemas.UnifiedResponse(
            code=exc.code,
            message=exc.message,
            data=None,
        ).model_dump()
    )

# 捕获 HTTPException，统一包装成标准响应格式
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP异常: status_code={exc.status_code}, detail={exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=schemas.UnifiedResponse(
            code=exc.status_code,
            message=str(exc.detail),
            data=None,
        ).model_dump()
    )


# 捕获请求参数校验错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=schemas.UnifiedResponse(
            code=422,
            message=f"参数校验失败: {error_msg}",
            data=None,
        ).model_dump(),
    )

# 兜底异常捕获，避免直接返回堆栈信息
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"发生未捕获异常: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=schemas.UnifiedResponse(
            code=500,
            message="服务器内部错误，请联系管理员",
            data=None,
        ).model_dump(),
    )

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务正常运行"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
```

### models\__init__.py

```python
# 模型层
from .user import User
from .role import Role
```

### models\role.py

```python
from session.db_session import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column,relationship

# 角色表
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="角色主键ID")
    # index 索引，给高频字段加索引
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色名称",index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True, comment="角色描述")
    # 一个角色可以对应多个用户
    # 注意：这里使用字符串 "User"，SQLAlchemy 会在所有类加载完成后自动解析
    users: Mapped[list["User"]] = relationship("User", back_populates="role_info")
```

### models\user.py

```python
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from session.db_session import Base


# 统一使用 UTC 时间入库，响应层再按需要转换时区。
def utc_now() -> datetime:
    """返回带 UTC 时区的当前时间。"""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="用户主键ID")
    # index 索引，给高频字段加索引
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名", index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="哈希密码")
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, comment="关联角色表ID")
    # 关系属性：通过 role_id 关联到角色表。
    role_info: Mapped["Role"] = relationship("Role", back_populates="users")
    age: Mapped[int] = mapped_column(comment="年龄")
    # index 索引，给高频字段加索引
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="邮箱", index=True)
    # nullable 允许为空
    avatar_url: Mapped[str | None] = mapped_column(String(255),nullable=True,default="static/avatars/default.jpg",comment="头像url")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=utc_now,onupdate=utc_now,comment="最后更新时间")

    @property
    def role(self) -> str | None:
        """兼容现有代码读取 user.role 的属性访问方式。"""
        # 兼容现有鉴权和响应层读取 user.role 的写法。
        return self.role_info.name if self.role_info else None
```

### requirements.txt

```text
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy>=2.0.35
pydantic>=2.10.0
pydantic-settings>=2.6.0
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.12
python-dotenv>=1.0.1
charset_normalizer>=3.4.6
loguru>=0.7.2
httpx>=0.28.1
tzdata>=2024.1
pytest>=8.3.0
```

### routers\__init__.py

```python
# 路由层
from fastapi import APIRouter

from .role_routes import router as role_router
from .user_routes import router as user_router

router = APIRouter()
router.include_router(user_router)
router.include_router(role_router)
```

### routers\role_routes.py

```python
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
```

### routers\user_routes.py

```python
import os
from typing import List

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from core.logger import get_logger
from services import user_service
from session.db_session import get_db
from utils.security import get_current_admin, get_current_user

logger = get_logger()
router = APIRouter(prefix="/users", tags=["用户管理"])

# 限流
limiter = Limiter(key_func=get_remote_address)
if hasattr(router, "state"):
    router.state.limiter = limiter
if hasattr(router, "add_exception_handler"):
    router.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# 登录
@router.post("/token", response_model=schemas.Token, summary="登录获取 Token")
# 限流接口 防止暴力请求 比如1分钟最多5次
# 测试环境关闭限流
@(limiter.limit("5/minute") if os.getenv("TESTING") != "1" else (lambda func: func))
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    logger.info(f"收到登录请求: username={form_data.username}")
    try:
        user, access_token = user_service.login_user(db, form_data.username, form_data.password)
    except HTTPException:
        logger.error(f"登录失败: username={form_data.username}, reason=用户名或密码错误")
        raise

    logger.success(f"登录成功: user_id={user.id}, username={user.username}, role={user.role}")
    return {"access_token": access_token, "token_type": "bearer"}


# 创建用户
@router.post("",response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="创建新用户")
def create_user_api(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """创建普通用户账号。"""
    logger.info(f"收到创建用户请求: username={user.username}, email={user.email}")

    try:
        # 普通注册入口固定创建 user 角色，避免通过该接口直接注册管理员。
        db_user = user_service.create_user(db, user)
    except BusinessException as exc:
        if exc.code == 4001:
            logger.error(f"创建用户失败: username={user.username}, reason=用户名已存在")
        elif exc.code == 4002:
            logger.error(f"创建用户失败: username={user.username}, email={user.email}, reason=邮箱已存在")
        elif exc.code == 4003:
            logger.error(f"创建用户失败: username={user.username}, password={user.password}, reason=密码至少8位，包含大小写、数字、特殊字符")
        raise
    logger.success(f"创建用户成功: user_id={db_user.id}, username={db_user.username}, role={db_user.role}")

    return schemas.UnifiedResponse(data=db_user)


# 按 ID 查询用户，增加 Depends(get_current_user) 保护
@router.get("/{user_id}", response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="根据ID查询用户")
def get_user_api(user_id: int,
                 db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    """查询单个用户详情。"""
    logger.info(f"收到查询用户请求: operator_id={current_user.id}, operator={current_user.username}, "
                f"role={current_user.role}, target_user_id={user_id}")

    try:
        db_user = user_service.get_user_detail(db, user_id, current_user)
    except HTTPException as exc:
        if exc.status_code == 404:
            logger.error(f"查询用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=用户不存在")
        elif exc.status_code == 403:
            logger.error(f"查询用户被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=无权查看他人信息")
        raise

    logger.success(f"查询用户成功: operator_id={current_user.id}, operator={current_user.username}, "
                   f"target_user_id={user_id}")

    return schemas.UnifiedResponse(data=db_user)


# 分页查询
@router.get("",response_model=schemas.UnifiedResponse[schemas.PageResult[schemas.UserResponse]],summary="分页查询用户列表")
def get_user_list_api(page_params: schemas.PageParams = Depends(),
                      db: Session = Depends(get_db),
                      current_admin: models.User = Depends(get_current_admin)):
    """分页查询用户列表，仅管理员可访问。"""
    logger.info(f"收到分页查询用户列表请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f"role={current_admin.role}, page={page_params.page}, page_size={page_params.page_size}")

    users, total = user_service.get_user_list(db, page_params.page, page_params.page_size)
    logger.success(f"分页查询用户列表成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"returned_count={len(users)}, total={total}")

    page_result = schemas.PageResult(items=users,total=total,page=page_params.page,page_size=page_params.page_size)
    return schemas.UnifiedResponse(data=page_result)


# 模糊查询
@router.get( "/search/", response_model=schemas.UnifiedResponse[List[schemas.UserResponse]], summary="模糊查询用户")
def search_users_api(keyword: str = Query(..., min_length=1, description="搜索关键字"),
                     db: Session = Depends(get_db),
                     current_admin: models.User = Depends(get_current_admin)):
    """按关键字模糊查询用户，仅管理员可访问。"""
    logger.info(f"收到模糊查询用户请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f"role={current_admin.role}, keyword={keyword}")

    users = user_service.search_users(db, keyword)
    logger.success(f"模糊查询用户成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"keyword={keyword}, returned_count={len(users)}")
    return schemas.UnifiedResponse(data=users)


# 更新用户：自己能改基础信息，管理员能改全部信息，包括 role_id
@router.put("/{user_id}", response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="更新用户信息")
def update_user_api( user_id: int,
                     user_update: schemas.UserUpdate,
                     db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):
    """更新用户信息并执行权限与唯一性校验。"""
    logger.info(f"收到更新用户请求: operator_id={current_user.id}, operator={current_user.username}, "
                f"role={current_user.role}, target_user_id={user_id}")

    try:
        updated_user = user_service.update_user(db, user_id, user_update, current_user)
    except HTTPException as exc:
        if exc.status_code == 404:
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=用户不存在")
        elif exc.status_code == 403:
            logger.error(f"更新用户被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=无权修改他人信息")
        raise
    except BusinessException as exc:
        if exc.code == 4004:
            logger.error(f"更新用户角色被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, reason=无管理员权限")
        elif exc.code == 4005:
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, role_id={user_update.role_id}, reason=角色不存在")
        elif exc.code == 4001:
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, username={user_update.username}, reason=用户名已被占用")
        elif exc.code == 4002:
            logger.error(f"更新用户失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, email={user_update.email}, reason=邮箱已被占用")
        raise

    logger.success(f"更新用户成功: operator_id={current_user.id}, operator={current_user.username}, "
                   f"target_user_id={user_id}")
    return schemas.UnifiedResponse(data=updated_user)


# 删除用户
@router.delete("/{user_id}",response_model=schemas.UnifiedResponse[dict],summary="删除用户",)
def delete_user_api(user_id: int,
                    db: Session = Depends(get_db),
                    current_admin: models.User = Depends(get_current_admin)):
    """删除普通用户，仅管理员可访问。"""
    logger.info(f"收到删除用户请求: operator_id={current_admin.id}, operator={current_admin.username}, "
                f"role={current_admin.role}, target_user_id={user_id}")

    try:
        user_service.delete_user(db, user_id)
    except BusinessException:
        logger.warning(f"删除用户失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                       f"target_user_id={user_id}, reason=不能删除 admin 角色用户")
        raise
    except HTTPException:
        logger.error(f"删除用户失败: operator_id={current_admin.id}, operator={current_admin.username}, "
                     f"target_user_id={user_id}, reason=用户不存在")
        raise

    logger.success(f"删除用户成功: operator_id={current_admin.id}, operator={current_admin.username}, "
                   f"target_user_id={user_id}")

    return schemas.UnifiedResponse(data={"message": "删除成功", "user_id": user_id})


# 上传头像
@router.post("/{user_id}/avatar",response_model=schemas.UnifiedResponse[schemas.UserResponse],summary="上传头像")
def upload_avatar_api(user_id: int,
                      file: UploadFile = File(...,description="头像图片文件"),
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    """上传当前用户头像。"""
    logger.info(f"收到上传头像请求: operator_id={current_user.id}, operator={current_user.username}, "
                f"role={current_user.role}, target_user_id={user_id}, filename={file.filename}, content_type={file.content_type}")

    try:
        updated_user = user_service.upload_avatar(db, user_id, current_user, file)
    except HTTPException as exc:
        if exc.status_code == 404:
            logger.error(f"上传头像失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, filename={file.filename}, reason=用户不存在")
        elif exc.status_code == 403:
            logger.error(f"上传头像被拒绝: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, filename={file.filename}, reason=无权修改他人头像")
        elif exc.status_code == 400:
            logger.error(f"上传头像失败: operator_id={current_user.id}, operator={current_user.username}, "
                         f"target_user_id={user_id}, filename={file.filename}, content_type={file.content_type}, reason={exc.detail}")
        raise

    logger.success(f"上传头像成功: operator_id={current_user.id}, operator={current_user.username}, "
                   f"target_user_id={user_id}, avatar_url={updated_user.avatar_url}")
    return schemas.UnifiedResponse(data=updated_user)
```

### schemas\__init__.py

```python
# Pydantic 请求 / 响应模型
from .user_schema import Token, UnifiedResponse, UserCreate, UserResponse, UserUpdate, PageParams, PageResult
from .role_schema import RoleResponse,RoleCreate
```

### schemas\role_schema.py

```python
from typing import Optional
from pydantic import BaseModel, ConfigDict

class RoleBase(BaseModel):
    """角色基础模型。"""

    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    """创建角色请求模型。"""

    pass

class RoleResponse(RoleBase):
    """角色响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
```

### schemas\user_schema.py

```python
# Pydantic 请求 / 响应模型
from datetime import datetime
from typing import Optional,Generic,TypeVar,List
from zoneinfo import ZoneInfo

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_serializer

# 泛型定义
T = TypeVar("T")
SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")

# 统一返回格式
class UnifiedResponse(BaseModel,Generic[T]):
    """统一响应结构。"""
    # 模型配置
    model_config = ConfigDict(from_attributes=True)

    code: int = Field(default=200,description="状态码")
    message: str = Field(default="success",description="提示信息")
    data: Optional[T] = Field(default=None,description="响应数据")

# 新增Token 响应模型
class Token(BaseModel):
    """登录接口返回的 Token 结构。"""

    access_token: str
    token_type: str

# 创建用户请求体
class UserCreate(BaseModel):
    """创建用户请求模型。"""
    username: str = Field(min_length=3,max_length=50,description="用户名")
    password: str = Field(min_length=6,description="密码") #新增
    age: int = Field(ge=0,le=150,description="年龄")
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="邮箱地址")

# 更新用户请求体
class UserUpdate(BaseModel):
    """更新用户请求模型。"""

    username: Optional[str] = Field(min_length=3,max_length=50,default=None)
    age: Optional[int] = Field(ge=0,le=150,default=None)
    email: Optional[str] = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", default=None)
    role_id: Optional[int] = None #只有管理员能修改这个字段

# 用户响应体 不返回密码
class UserResponse(BaseModel):
    """用户响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id:int
    username: str
    role: Optional[str]
    age: Optional[int]
    email: str
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        # SQLite 读回来的 datetime 可能不带时区；当前项目统一按 UTC 存储，响应时转为北京时间
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        return value.astimezone(SHANGHAI_TZ).isoformat()

# 分页相关通用模型
class PageParams:
    # 通用分页参数依赖项
    def __init__(
            self,page: int = Query(1, ge=1, description="页码，从1开始"),
            page_size: int = Query(10, ge=1, le=100, description="每页数量,最大100")
    ):
        self.page = page
        self.page_size = page_size

class PageResult(BaseModel, Generic[T]):
    """通用分页响应结果。"""

    model_config = ConfigDict(from_attributes=True)

    # 通用分页响应结果
    items: List[T]          # 数据列表
    total: int              # 总条数
    page: int               # 当前页码
    page_size: int          # 每页条数

# 解决User和Role之间的循环依赖
# 在文件末尾，等 RoleResponse 导入后，手动让 Pydantic 重新构建 UserResponse 的模型结构。
# 1.在这里导入RoleResponse
from .role_schema import RoleResponse
# 2.调用model_rebuild（）来修复 UserResponse 里的字符串引用
UserResponse.model_rebuild()
```

### services\__init__.py

```python
# 服务层
# 统一暴露 service 模块和常用类型别名，方便路由层直接导入。
from . import role_service, user_service
from .role_service import RoleListResult
from .user_service import LoginResult, UserListResult

__all__ = [
    "role_service",
    "user_service",
    "RoleListResult",
    "LoginResult",
    "UserListResult",
]
```

### services\role_service.py

```python
from typing import List, TypeAlias

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from dao import role_dao, user_dao
from models import Role, User
from utils.password_utils import get_password_hash

# 角色列表的统一返回类型。
RoleListResult: TypeAlias = List[Role]

# 管理员创建前校验
def _ensure_admin_user_unique(db: Session, user: schemas.UserCreate) -> None:
    """创建管理员前校验用户名和邮箱唯一性。"""
    if user_dao.get_user_by_username(db, user.username):
        raise BusinessException(status_code=400, code=4001, message="用户名已存在")

    if user_dao.get_user_by_email(db, user.email):
        raise BusinessException(status_code=400, code=4002, message="邮箱已存在")


# 创建管理员
def create_admin_user(db: Session, user: schemas.UserCreate) -> User:
    """创建管理员账号。"""
    _ensure_admin_user_unique(db, user)
    return user_dao.create_user(db, user, role_name="admin")


# 创建角色
def create_role(db: Session, role: schemas.RoleCreate) -> Role:
    """创建角色并校验重复。"""
    return role_dao.create_role_with_check(db, role.name, role.description)


# 查询全部角色
def get_all_roles(db: Session) -> list[type[Role]]:
    """查询全部角色列表。"""
    return role_dao.get_all_roles(db)


# 重置密码
def reset_password(db: Session, user_id: int, current_user: models.User, new_password: str) -> User:
    """重置指定用户密码，并校验操作权限。"""
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权重置他人密码")

    hashed_password = get_password_hash(new_password)
    return user_dao.update_user_password(db, db_user, hashed_password)
```

### services\user_service.py

```python
from datetime import timedelta
from typing import List, Tuple, TypeAlias, Sequence, Any

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

import models
import schemas
from core.exceptions import BusinessException
from dao import user_dao
from dao.user_dao import DeleteUserResult
from models import User
from utils.file_utils import save_avatar
from utils.password_utils import validate_password, verify_password
from utils.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

# 登录后返回“用户对象 + token”的统一结构。
LoginResult: TypeAlias = Tuple[models.User, str]
# 分页查询返回“数据列表 + 总数”的统一结构。
UserListResult: TypeAlias = tuple[List[models.User], int]


# 注册校验

def _ensure_user_unique(db: Session, user: schemas.UserCreate) -> None:
    """注册前检查用户名和邮箱是否已被使用。"""
    if user_dao.get_user_by_username(db, user.username):
        raise BusinessException(status_code=400, code=4001, message="用户名已存在")

    if user_dao.get_user_by_email(db, user.email):
        raise BusinessException(status_code=400, code=4002, message="邮箱已存在")


# 密码校验
def _ensure_password_valid(password: str) -> None:
    """密码复杂度校验统一放在 service 层。"""
    if not validate_password(password):
        raise BusinessException(status_code=400, code=4003, message="密码至少8位，包含大小写、数字、特殊字符")


# 登录校验
def login_user(db: Session, username: str, password: str) -> LoginResult:
    """完成用户查找、密码校验和 token 生成。"""
    user = user_dao.get_user_by_username(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误", headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return user, access_token

# 创建用户
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """完成注册前置校验并创建普通用户。"""
    _ensure_user_unique(db, user)
    _ensure_password_valid(user.password)
    return user_dao.create_user(db, user, role_name="user")


# 根据id查询
def get_user_detail(db: Session, user_id: int, current_user: models.User) -> models.User:
    """完成用户存在性与查看权限校验，并返回用户详情。"""
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if db_user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权查看他人信息")

    return db_user


# 分页查询
def get_user_list(db: Session, page: int, page_size: int) -> tuple[List[models.User], int]:
    """分页查询用户列表并返回总数。"""
    return user_dao.get_user_list(db, page, page_size)


# 根据ID、用户名模糊查询
def search_users(db: Session, keyword: str) -> Sequence[User]:
    """按关键字搜索用户。"""
    return user_dao.search_users(db, keyword)


# 更新用户
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate, current_user: models.User) -> models.User:
    """完成权限、角色、唯一性校验并更新用户。"""
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if db_user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权修改他人信息")

    if user_update.role_id is not None and current_user.role != "admin":
        raise BusinessException(status_code=403, code=4004, message="无权修改用户角色")

    if user_update.role_id is not None and not db.get(models.Role, user_update.role_id):
        raise BusinessException(status_code=400, code=4005, message="角色不存在")

    if user_update.username and user_update.username != db_user.username:
        if user_dao.get_user_by_username(db, user_update.username):
            raise BusinessException(status_code=400, code=4001, message="用户名已被占用")

    if user_update.email and user_update.email != db_user.email:
        if user_dao.get_user_by_email(db, user_update.email):
            raise BusinessException(status_code=400, code=4002, message="邮箱已被占用")

    return user_dao.update_user(db, user_id, user_update)

# 删除用户
def delete_user(db: Session, user_id: int) -> DeleteUserResult:
    """删除用户，并将 DAO 返回结果翻译成业务异常或 HTTP 异常。"""
    delete_result = user_dao.delete_user(db, user_id)
    if not delete_result["success"]:
        if delete_result["reason"] == "admin_forbidden":
            raise BusinessException(status_code=403, code=4003, message="不能删除 admin 角色账号")
        raise HTTPException(status_code=404, detail="用户不存在")
    return delete_result

# 头像保存
def upload_avatar(db: Session,
                  user_id: int,
                  current_user: models.User,
                  file: UploadFile) -> models.User:
    """上传并保存当前用户头像。"""
    # 1.查找用户是否存在
    db_user = user_dao.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 2.校验ID是否一致，只能改自己的
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改他人头像")
    # 3.使用工具保存文件到 static/avatars，并获取 avatar_url
    new_avatar_url = save_avatar(file,db_user.avatar_url)
    # 4.更新数据库
    updated_user = user_dao.update_user_avatar(db, user_id, new_avatar_url)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return updated_user
```

### session\__init__.py

```python
# 会话层
```

### session\db_session.py

```python
# 数据库连接配置
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# SQLite 数据库连接地址
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("未配置 SQLALCHEMY_DATABASE_URL，请检查 .env 文件")

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 模型基类
class Base(DeclarativeBase):
    pass

# 依赖项：获取数据库会话
def get_db():
    with SessionLocal() as db:
        yield db
```

### tests\test_user_system.py

```python
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import get_logger

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
# 测试环境关闭登录限流，避免批量用例触发 429。
os.environ.setdefault("TESTING", "1")

import main
import routers.user_routes as user_routes
import utils.file_utils as file_utils
import utils.security as security

security.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
user_routes.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
from dao import role_dao, user_dao
from schemas import UserCreate
from session import db_session
from session.db_session import Base

logger = get_logger()


def cleanup_test_avatars():
    """清理测试生成的头像文件，保留默认头像。"""
    if not file_utils.STATIC_DIR.exists():
        return
    for avatar_file in file_utils.STATIC_DIR.iterdir():
        if avatar_file.is_file() and avatar_file.name != "default.jpg":
            avatar_file.unlink()


def setup_module():
    """测试模块启动前清理遗留测试库。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    if db_path.exists():
        logger.info(f"删除遗留测试数据库: path={db_path}")
        db_path.unlink()
    cleanup_test_avatars()


def teardown_module():
    """测试模块结束后清理测试库。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    if db_path.exists():
        logger.info(f"清理测试数据库: path={db_path}")
        db_path.unlink()
    cleanup_test_avatars()


def build_test_client():
    """构建独立测试库和 TestClient。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    logger.info(f"构建测试客户端: db_path={db_path}")
    test_engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    db_session.engine = test_engine
    db_session.SessionLocal = testing_session_local
    main.engine = test_engine
    main.SessionLocal = testing_session_local

    # 每次构建测试客户端都重置库，确保测试之间互不污染。
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # 初始化角色和管理员账号，避免依赖外部环境已有数据。
    with testing_session_local() as db:
        role_dao.create_role(db, name="admin", description="系统管理员")
        role_dao.create_role(db, name="user", description="普通用户")
        admin_user = UserCreate(
            username="admin",
            password="123456",
            age=30,
            email="admin@example.com",
        )
        user_dao.create_user(db, admin_user, role_name="admin")

    cleanup_test_avatars()
    client = TestClient(main.app)
    logger.success("测试客户端构建完成")
    return client, test_engine


def auth_headers(token: str) -> dict:
    """构建 Bearer Token 请求头。"""
    return {"Authorization": f"Bearer {token}"}


def login(client: TestClient, username: str, password: str) -> str:
    """执行登录并返回访问令牌。"""
    logger.info(f"测试登录: username={username}")
    response = client.post(
        "/users/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    logger.success(f"测试登录成功: username={username}")
    return response.json()["access_token"]


def create_user(
    client: TestClient,
    username: str = "alice",
    password: str = "Aa123456!",
    age: int = 18,
    email: str = "alice@example.com",
) -> dict:
    """通过注册接口创建测试用户。"""
    logger.info(f"测试创建用户: username={username}, email={email}")
    response = client.post(
        "/users",
        json={
            "username": username,
            "password": password,
            "age": age,
            "email": email,
        },
    )
    assert response.status_code == 200, response.text
    logger.success(f"测试创建用户成功: username={username}")
    return response.json()["data"]


def test_health_check():
    """验证健康检查接口。"""
    client, engine = build_test_client()
    try:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "message": "服务正常运行"}
    finally:
        client.close()
        engine.dispose()


def test_user_basic_flow():
    """验证普通用户注册、登录、查询、更新主流程。"""
    client, engine = build_test_client()
    try:
        created_user = create_user(client)
        token = login(client, "alice", "Aa123456!")

        get_response = client.get(
            f"/users/{created_user['id']}",
            headers=auth_headers(token),
        )
        assert get_response.status_code == 200, get_response.text
        assert get_response.json()["data"]["username"] == "alice"
        assert get_response.json()["data"]["role"] == "user"

        update_response = client.put(
            f"/users/{created_user['id']}",
            json={"age": 20, "email": "alice.updated@example.com"},
            headers=auth_headers(token),
        )
        assert update_response.status_code == 200, update_response.text
        assert update_response.json()["data"]["age"] == 20
        assert update_response.json()["data"]["email"] == "alice.updated@example.com"
    finally:
        client.close()
        engine.dispose()


def test_exception_responses():
    """验证常见异常响应格式和业务码。"""
    client, engine = build_test_client()
    try:
        create_user(client)

        duplicate_username = client.post(
            "/users",
            json={
                "username": "alice",
                "password": "Aa123456!",
                "age": 18,
                "email": "alice2@example.com",
            },
        )
        assert duplicate_username.status_code == 400, duplicate_username.text
        assert duplicate_username.json()["code"] == 4001

        duplicate_email = client.post(
            "/users",
            json={
                "username": "alice2",
                "password": "Aa123456!",
                "age": 18,
                "email": "alice@example.com",
            },
        )
        assert duplicate_email.status_code == 400, duplicate_email.text
        assert duplicate_email.json()["code"] == 4002

        bad_login = client.post(
            "/users/token",
            data={"username": "alice", "password": "wrong-password"},
        )
        assert bad_login.status_code == 400, bad_login.text
        assert bad_login.json()["code"] == 400

        no_token = client.get("/users/1")
        assert no_token.status_code == 401, no_token.text
        assert no_token.json()["code"] == 401
    finally:
        client.close()
        engine.dispose()


def test_permission_and_admin_flows():
    """验证管理员权限相关接口和删除限制。"""
    client, engine = build_test_client()
    try:
        user = create_user(client)
        user_token = login(client, "alice", "Aa123456!")
        admin_token = login(client, "admin", "123456")

        forbidden_role_update = client.put(
            f"/users/{user['id']}",
            json={"role_id": 1},
            headers=auth_headers(user_token),
        )
        assert forbidden_role_update.status_code == 403, forbidden_role_update.text
        assert forbidden_role_update.json()["code"] == 4004

        list_response = client.get(
            "/users?page=1&page_size=10",
            headers=auth_headers(admin_token),
        )
        assert list_response.status_code == 200, list_response.text
        list_data = list_response.json()["data"]
        assert list_data["total"] == 2
        assert len(list_data["items"]) == 2

        search_response = client.get(
            "/users/search/?keyword=alice",
            headers=auth_headers(admin_token),
        )
        assert search_response.status_code == 200, search_response.text
        assert len(search_response.json()["data"]) == 1

        delete_admin = client.delete(
            "/users/1",
            headers=auth_headers(admin_token),
        )
        assert delete_admin.status_code == 403, delete_admin.text
        assert delete_admin.json()["code"] == 4003

        delete_user_response = client.delete(
            f"/users/{user['id']}",
            headers=auth_headers(admin_token),
        )
        assert delete_user_response.status_code == 200, delete_user_response.text
        assert delete_user_response.json()["data"]["user_id"] == user["id"]
    finally:
        client.close()
        engine.dispose()


def test_create_admin_user_api():
    """验证管理员创建管理员账号接口。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.post(
            "/roles/admin/users",
            json={
                "username": "boss2",
                "password": "Aa123456!",
                "age": 35,
                "email": "boss2@example.com",
            },
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["username"] == "boss2"
        assert data["role"] == "admin"
    finally:
        client.close()
        engine.dispose()


def test_create_admin_user_api_duplicate_cases():
    """验证创建管理员账号时的重复校验。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")
        create_user(client, username="alice", email="alice@example.com")

        duplicate_username = client.post(
            "/roles/admin/users",
            json={
                "username": "alice",
                "password": "Aa123456!",
                "age": 28,
                "email": "alice_admin@example.com",
            },
            headers=auth_headers(admin_token),
        )
        assert duplicate_username.status_code == 400, duplicate_username.text
        assert duplicate_username.json()["code"] == 4001

        duplicate_email = client.post(
            "/roles/admin/users",
            json={
                "username": "alice_admin",
                "password": "Aa123456!",
                "age": 28,
                "email": "alice@example.com",
            },
            headers=auth_headers(admin_token),
        )
        assert duplicate_email.status_code == 400, duplicate_email.text
        assert duplicate_email.json()["code"] == 4002
    finally:
        client.close()
        engine.dispose()


def test_create_role_api():
    """验证管理员创建角色接口。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.post(
            "/roles",
            json={"name": "editor", "description": "编辑角色"},
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["name"] == "editor"
        assert data["description"] == "编辑角色"
    finally:
        client.close()
        engine.dispose()


def test_create_role_api_duplicate_role():
    """验证创建重复角色时返回业务错误。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.post(
            "/roles",
            json={"name": "admin", "description": "系统管理员"},
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 400, response.text
        assert response.json()["code"] == 4006
    finally:
        client.close()
        engine.dispose()


def test_get_all_roles():
    """验证管理员查询全部角色接口。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.get(
            "/roles",
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        role_names = [item["name"] for item in data]
        assert "admin" in role_names
        assert "user" in role_names
    finally:
        client.close()
        engine.dispose()


def test_reset_password_by_self():
    """验证用户可以重置自己的密码。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="alice", email="alice@example.com")
        user_token = login(client, "alice", "Aa123456!")

        response = client.post(
            f"/roles/{user['id']}/reset-password",
            json="654321",
            headers=auth_headers(user_token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["message"] == "密码重置成功"

        bad_login = client.post(
            "/users/token",
            data={"username": "alice", "password": "Aa123456!"},
        )
        assert bad_login.status_code == 400, bad_login.text

        new_token = login(client, "alice", "654321")
        assert new_token
    finally:
        client.close()
        engine.dispose()


def test_reset_password_by_admin():
    """验证管理员可以重置其他用户密码。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="alice", email="alice@example.com")
        admin_token = login(client, "admin", "123456")

        response = client.post(
            f"/roles/{user['id']}/reset-password",
            json="654321",
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["message"] == "密码重置成功"

        new_token = login(client, "alice", "654321")
        assert new_token
    finally:
        client.close()
        engine.dispose()


def test_reset_password_permission_denied():
    """验证普通用户不能重置他人密码。"""
    client, engine = build_test_client()
    try:
        alice = create_user(client, username="alice", email="alice@example.com")
        bob = create_user(client, username="bob", email="bob@example.com")
        alice_token = login(client, "alice", "Aa123456!")

        response = client.post(
            f"/roles/{bob['id']}/reset-password",
            json="654321",
            headers=auth_headers(alice_token),
        )
        assert response.status_code == 403, response.text
        assert response.json()["code"] == 403
    finally:
        client.close()
        engine.dispose()


def test_reset_password_user_not_found():
    """验证重置不存在用户密码时返回 404。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.post(
            "/roles/999/reset-password",
            json="654321",
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 404, response.text
        assert response.json()["code"] == 404
    finally:
        client.close()
        engine.dispose()


def test_upload_avatar_success_with_png():
    """验证用户可上传 PNG 头像，并写入数据库。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="avatar_user", email="avatar_user@example.com")
        token = login(client, "avatar_user", "Aa123456!")

        response = client.post(
            f"/users/{user['id']}/avatar",
            files={"file": ("avatar.png", b"fake-png-bytes", "image/png")},
            headers=auth_headers(token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["code"] == 200

        with db_session.SessionLocal() as db:
            db_user = user_dao.get_user_by_id(db, user["id"])
            assert db_user.avatar_url is not None
            assert db_user.avatar_url.startswith("static/avatars/")
            assert db_user.avatar_url.endswith(".png")
            assert db_user.avatar_url != "static/avatars/default.jpg"
            assert (PROJECT_ROOT / db_user.avatar_url).exists()
    finally:
        client.close()
        engine.dispose()


def test_upload_avatar_reject_invalid_content_type():
    """验证上传非图片文件时返回 400。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="bad_file_user", email="bad_file_user@example.com")
        token = login(client, "bad_file_user", "Aa123456!")

        response = client.post(
            f"/users/{user['id']}/avatar",
            files={"file": ("avatar.txt", b"not-an-image", "text/plain")},
            headers=auth_headers(token),
        )
        assert response.status_code == 400, response.text
        assert response.json()["code"] == 400
    finally:
        client.close()
        engine.dispose()


def test_upload_avatar_reject_oversized_file():
    """验证上传超过 2MB 的文件时返回 400。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="large_file_user", email="large_file_user@example.com")
        token = login(client, "large_file_user", "Aa123456!")
        large_content = b"a" * (2 * 1024 * 1024 + 1)

        response = client.post(
            f"/users/{user['id']}/avatar",
            files={"file": ("avatar.jpg", large_content, "image/jpeg")},
            headers=auth_headers(token),
        )
        assert response.status_code == 400, response.text
        assert response.json()["code"] == 400
    finally:
        client.close()
        engine.dispose()
```

### utils\__init__.py

```python
# 工具包
```

### utils\file_utils.py

```python
import os
import time
from pathlib import Path

from fastapi import UploadFile, HTTPException

# 限制文件类型和大小
ALLOWED_TYPES = {"image/jpeg","image/png"}
MAX_SIZE = 2 * 1024 * 1024 #限制2MB文件大小

# 保存相对路径
STATIC_DIR = Path(__file__).resolve().parents[1] / "static" / "avatars"


def save_avatar(file: UploadFile,avatar_url) -> str:
    # 校验类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "只允许上传jpg/png图片")

    # 校验大小 2MB
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0) # 重置指针
    if size > MAX_SIZE:
        raise HTTPException(400,"图片大小不能超过2MB")

    # 时间戳命名
    suffix = Path(file.filename or "avatar.jpg").suffix or ".jpg"
    filename = f"{int(time.time() * 1000)}{suffix}"

    # 删除旧图片
    if not avatar_url == "static/avatars/default.jpg":
        static = Path(__file__).resolve().parents[1]
        # 删除该图片
        file_path = static / avatar_url
        if file_path.exists():
            file_path.unlink()
    # 保存文件
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    file_path = STATIC_DIR / filename
    with open(file_path,"wb") as f:
        f.write(file.file.read())

    return f"static/avatars/{filename}"
```

### utils\password_utils.py

```python
from passlib.context import CryptContext
import re
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=100000, # 迭代次数（越高越安全，默认10万次）
    deprecated="auto",
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 验证密码：明文 vs 哈希值
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # 获取密码的哈希值
    return pwd_context.hash(password)

def validate_password(password: str) -> bool:
    # 校验密码复杂度：至少8位，包含大小写、数字、特殊字符
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*()_+=-]", password):
        return False
    return True
```

### utils\security.py

```python
# 核心安全逻辑
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from dao import user_dao as crud
from models import User
from session.db_session import get_db

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("未配置 SECRET_KEY，请在环境变量或 .env 文件中设置 SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=15)
    to_encode.update({
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 依赖项： 通过Token获取当前用户，用于保护接口
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)):
    # 依赖项： 通过Token获取当前用户，用于保护接口
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user
```

