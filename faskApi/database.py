from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 数据库 URL，数据库文件就在当前目录下
SQLALCHEMY_DATABASE_URL = "sqlite:///./bookstore.db"

# 创建引擎
engine = create_engine(
    # 禁用 SQLite 的多线程模式，因为 SQLite 不支持多线程
    SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread":False}
)

# 创建会话本地类
SessionLocal = sessionmaker(autocommit = False,autoflush=False,bind=engine)
# 创造基类
Base = declarative_base()

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()