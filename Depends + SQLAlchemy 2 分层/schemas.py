# Pydantic 请求 / 响应模型
from datetime import datetime
from typing import List,Optional,Generic,TypeVar
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

# 创建用户请求体
class UserCreat(BaseModel):
    username: Optional[str] = Field(min_length=3,max_length=50,description="用户名")
    age: Optional[int] = Field(ge=0,le=150,description="年龄")
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="邮箱地址")

# 更新用户请求体
class UserUpdate(BaseModel):
    username: Optional[str] = Field(min_length=3,max_length=50,default=None)
    age: Optional[int] = Field(ge=0,le=150,default=None)
    email: Optional[str] = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", default=None)

# 用户响应体
class UserResponse(UserCreat):
    id:int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True