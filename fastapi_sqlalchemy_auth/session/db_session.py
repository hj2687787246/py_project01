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
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 模型基类
class Base(DeclarativeBase):
    pass

# 依赖项：获取数据库会话
def get_db():
    with SessionLocal() as db:
        yield db
