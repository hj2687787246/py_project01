from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # JWT签名密钥（生产环境必须配置复杂的随机字符串，禁止使用代码内置默认值）
    SECRET_KEY: str
    # JWT加密算法，固定用HS256即可
    ALGORITHM: str = "HS256"
    # access_token过期时间：30分钟（经常用，泄露风险大，所以短）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # refresh_token过期时间：7天（只在刷新时用，存得安全，所以长）
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 允许 .env 中存在当前 Settings 未声明的其他配置，避免和仓库里别的项目变量冲突
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


@lru_cache(maxsize=None)  # 缓存配置对象，只在第一次调用时创建Settings对象，后续都返回缓存，提升性能
def get_settings():
    return Settings()
