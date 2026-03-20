# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# 1. 数据库链接地址注意变了！ 使用了异步数据库
#    sqlite -> sqlite+aiosqlite
#    postgresql -> postgresql+asyncpg
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_async.db"

# 2. 创建异步引擎 (create_async_engine)
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. 创建异步会话工厂 (class_=AsyncSession)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()

# 4. 依赖注入函数变成异步生成器 (async def + yield)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session