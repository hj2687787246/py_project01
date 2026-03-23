# 数据访问层
# 集中导出 DAO 模块和常用返回结构，便于 service 层复用。
from . import role_dao, user_dao
from .user_dao import DeleteUserResult

__all__ = ["role_dao", "user_dao", "DeleteUserResult"]
