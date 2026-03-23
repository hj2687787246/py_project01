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
