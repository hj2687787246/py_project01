# Pydantic 请求 / 响应模型
from datetime import datetime
from typing import Optional,Generic,TypeVar,List
from zoneinfo import ZoneInfo

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_serializer

# 泛型定义
T = TypeVar("T")
SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")

# 统一返回格式
class UnifiedResponse(BaseModel,Generic[T]):
    """统一响应结构。"""

    model_config = ConfigDict(from_attributes=True)

    code: int = Field(default=200,description="状态码")
    message: str = Field(default="success",description="提示信息")
    data: Optional[T] = Field(default=None,description="响应数据")

# 新增Token 响应模型
class Token(BaseModel):
    """登录接口返回的 Token 结构。"""

    access_token: str
    token_type: str

# 创建用户请求体
class UserCreate(BaseModel):
    """创建用户请求模型。"""

    username: str = Field(min_length=3,max_length=50,description="用户名")
    password: str = Field(min_length=6,description="密码") #新增
    age: int = Field(ge=0,le=150,description="年龄")
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="邮箱地址")

# 更新用户请求体
class UserUpdate(BaseModel):
    """更新用户请求模型。"""

    username: Optional[str] = Field(min_length=3,max_length=50,default=None)
    age: Optional[int] = Field(ge=0,le=150,default=None)
    email: Optional[str] = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", default=None)
    role_id: Optional[int] = None #只有管理员能修改这个字段

# 用户响应体 不返回密码
class UserResponse(BaseModel):
    """用户响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id:int
    username: str
    role: Optional[str]
    age: Optional[int]
    email: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        # SQLite 读回来的 datetime 可能不带时区；当前项目统一按 UTC 存储，响应时转为北京时间
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        return value.astimezone(SHANGHAI_TZ).isoformat()

# 分页相关通用模型
class PageParams:
    # 通用分页参数依赖项
    def __init__(
            self,page: int = Query(1, ge=1, description="页码，从1开始"),
            page_size: int = Query(10, ge=1, le=100, description="每页数量,最大100")
    ):
        self.page = page
        self.page_size = page_size

class PageResult(BaseModel, Generic[T]):
    """通用分页响应结果。"""

    model_config = ConfigDict(from_attributes=True)

    # 通用分页响应结果
    items: List[T]          # 数据列表
    total: int              # 总条数
    page: int               # 当前页码
    page_size: int          # 每页条数

# 解决User和Role之间的循环依赖
# 在文件末尾，等 RoleResponse 导入后，手动让 Pydantic 重新构建 UserResponse 的模型结构。
# 1.在这里导入RoleResponse
from .role_schema import RoleResponse
# 2.调用model_rebuild（）来修复 UserResponse 里的字符串引用
UserResponse.model_rebuild()
