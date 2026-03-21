# Pydantic 请求 / 响应模型
from datetime import datetime
from typing import Optional,Generic,TypeVar
from pydantic import BaseModel,Field

# 泛型定义
T = TypeVar("T")

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
    username: Optional[str] = Field(min_length=3,max_length=50,description="用户名")
    password: str = Field(min_length=6,description="密码") #新增
    age: Optional[int] = Field(ge=0,le=150,description="年龄")
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

    class Config:
        from_attributes = True