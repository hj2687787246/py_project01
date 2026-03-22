from passlib.context import CryptContext

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
