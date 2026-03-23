# 数据库连接配置
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker

# SQLite数据库链接地址
SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi_test.db"

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread":False})

# 会话工厂
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# ORM模型基类
class Base(DeclarativeBase):
    pass

# 依赖项：获取数据库会话
def get_db():
    with SessionLocal() as db:
        yield db
