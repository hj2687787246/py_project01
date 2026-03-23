# 核心安全逻辑
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from dao import user_dao as crud
from session.db_session import get_db
from models import User # 导入User模型用于类型提示

load_dotenv()

# 配置项
# 生成一个安全的 SECRET_KEY: 终端运行 openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("未配置 SECRET_KEY，请在环境变量或 .env 文件中设置 SECRET_KEY")
ALGORITHM = "HS256"
#  # Token 过期时间
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# JWT Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # 生成JWT Token
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=15)
    # 显式写入 Unix 时间戳，避免时区和 naive datetime 的解释差异
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

# 获取当前管理员的依赖项
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user
