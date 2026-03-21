# 核心安全逻辑
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import crud
from database import get_db
from models import User # 导入User模型用于类型提示

# 配置项
# 生成一个安全的 SECRET_KEY: 终端运行 openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token 30分钟过期

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=100000,  # 迭代次数（越高越安全，默认10万次）
    deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 验证密码：明文 vs 哈希值
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str)->str:
    # 获取密码的哈希值
    return pwd_context.hash(password)

# JWT Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # 生成JWT Token
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
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
