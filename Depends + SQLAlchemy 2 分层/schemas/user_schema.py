# Pydantic 请求 / 响应模型
from datetime import datetime
from typing import Optional,Generic,TypeVar,List
from zoneinfo import ZoneInfo

from fastapi import Query
from pydantic import BaseModel,Field, field_serializer

# 泛型定义
T = TypeVar("T")
SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")

# 统一返回格式
class UnifiedResponse(BaseModel,Generic[T]):
    code: int = Field(default=200,description="状态码")
    message: str = Field(default="success",description="提示信息")
    data: Optional[T] = Field(default=None,description="响应数据")

    class Config:
        from_attributes = True

# 新增Token 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str

# 创建用户请求体
class UserCreate(BaseModel):
    username: str = Field(min_length=3,max_length=50,description="用户名")
    password: str = Field(min_length=6,description="密码") #新增
    age: int = Field(ge=0,le=150,description="年龄")
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="邮箱地址")

# 更新用户请求体
class UserUpdate(BaseModel):
    username: Optional[str] = Field(min_length=3,max_length=50,default=None)
    age: Optional[int] = Field(ge=0,le=150,default=None)
    email: Optional[str] = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", default=None)
    role: Optional[str] = None #只有管理员能修改这个字段

# 用户响应体 不返回密码
class UserResponse(BaseModel):
    id:int
    username: str
    role: str
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

    class Config:
        from_attributes = True

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
    # 通用分页响应结果
    items: List[T]          # 数据列表
    total: int              # 总条数
    page: int               # 当前页码
    page_size: int          # 每页条数

    class Config:
        from_attributes = True