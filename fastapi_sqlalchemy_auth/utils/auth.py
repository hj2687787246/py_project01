from passlib.context import CryptContext
import re
# 核心安全逻辑
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from config import Settings, get_settings

from dao import user_dao
from models import User
from session.db_session import get_db


# 1. 初始化密码加密上下文：改用 pbkdf2_sha256，避免当前环境下 bcrypt 兼容问题
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=100000,
    deprecated="auto",
)
# 2. 初始化OAuth2方案：指定登录接口是"/users/login"，FastAPI会自动从Header取Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# 密码相关函数
# 验证密码：输入明文密码和数据库里的哈希密码，返回是否匹配
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 验证密码：明文 vs 哈希值
    return pwd_context.verify(plain_password, hashed_password)

# 生成密码哈希：注册或修改密码时用，不存明文密码到数据库
def get_password_hash(password: str) -> str:
    # 获取密码的哈希值
    return pwd_context.hash(password)

# 校验密码复杂度
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

# Token生成函数 接收数据、过期时间、配置，返回Token
def create_token(data: dict, expires_delta: timedelta, settings: Settings) -> str:
    """
    生成JWT认证令牌
    参数:data: 要存入Token的核心数据（通常存放用户唯一标识，如sub: 用户ID/用户名）
        expires_delta: Token的有效时长（timedelta对象）
        settings: 项目配置实例，获取密钥和加密算法
    返回:生成的JWT字符串（令牌）
    """
    # 浅拷贝原始数据字典，避免直接修改传入的原数据（保证函数无副作用）
    to_encode = data.copy()
    # 获取【带时区的UTC当前时间】：JWT标准时间格式，杜绝时区bug
    now = datetime.now(timezone.utc)
    # 计算Token过期时间
    if expires_delta:
        # 传入了有效时长 → 使用指定时长计算过期时间
        expire = now + expires_delta
    else:
        # 未传入有效时长 → 默认设置15分钟过期（安全兜底）
        expire = now + timedelta(minutes=15)
    # 向JWT载荷(payload)中添加标准声明字段
    to_encode.update({
        "iat": int(now.timestamp()),  # iat = Issued at → 令牌签发时间（标准时间戳）
        "exp": int(expire.timestamp())  # exp = Expiration time → 令牌过期时间（标准时间戳）
    })
    # 生成最终的JWT令牌
    # 使用密钥签名 + 指定算法加密，保证令牌不可篡改
    encoded_jwt = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    # 返回生成好的JWT令牌
    return encoded_jwt

# 生成access_token：调用通用函数，传短的过期时间
def create_access_token(data: dict, settings: Settings) -> str:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(data, access_token_expires, settings)

# 生成refresh_token：调用通用函数，传长的过期时间
def create_refresh_token(data: dict, settings: Settings) -> str:
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(data, refresh_token_expires, settings)

# 通用Token验证函数：接收Token、异常对象、配置，返回Token里的数据
def verify_token(token: str,credentials_exception: HTTPException,settings: Settings) -> str:
    """
    通用JWT Token验证
    :param token: 请求头中的Token
    :param credentials_exception: 认证失败异常
    :param settings: 配置类
    :return: 从Token中解析出的用户名
    """
    try:
        # 解码Token：验证签名、过期时间
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        # 获取用户标识（sub是JWT标准字段，存用户名/ID）
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    # 捕获所有Token错误（过期、签名错误、格式非法）
    except JWTError:
        raise credentials_exception

# ====================== 接口依赖：获取当前登录用户 ======================
async def get_current_user(
    token: str = Depends(oauth2_scheme),  # 自动从请求头取Token
    db: Session = Depends(get_db),  # 注入数据库会话
    settings: Settings = Depends(get_settings)  # 注入配置
):
    """
    接口鉴权依赖：验证Token并返回当前登录的用户
    用法：在接口参数中写 current_user = Depends(get_current_user)
    """
    # 定义认证失败的统一异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. 调用通用函数校验Token，获取用户名
    username = verify_token(token, credentials_exception, settings)
    # 2. 查询数据库，获取完整用户信息
    user = user_dao.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    # 3. 返回用户对象，供接口使用
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)):
    # 依赖项： 通过Token获取当前用户，用于保护接口
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user