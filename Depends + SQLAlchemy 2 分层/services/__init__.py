# 服务层
# 统一暴露 service 模块和常用类型别名，方便路由层直接导入。
from . import role_service, user_service
from .role_service import RoleListResult
from .user_service import LoginResult, UserListResult

__all__ = [
    "role_service",
    "user_service",
    "RoleListResult",
    "LoginResult",
    "UserListResult",
]
