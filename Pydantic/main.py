# 1. 导入核心依赖
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, ValidationError
from datetime import datetime
from typing import Optional, Generic, TypeVar, Union

# 2. 定义通用类型（用于统一响应模型）
T = TypeVar("T")


# 3. 统一响应格式模型（所有接口返回相同结构）
class ResponseModel(BaseModel, Generic[T]):
    code: int = Field(..., description="状态码：200成功，其他失败")
    msg: str = Field(..., description="提示信息")
    data: Optional[T] = Field(None, description="业务数据，成功时返回，失败时为null")

    class Config:
        from_attributes = True


# 4. 自定义异常类（用于全局捕获）
class CustomException(HTTPException):
    def __init__(self, code: int, msg: str, status_code: int = 200):
        self.code = code
        self.msg = msg
        self.status_code = status_code  # HTTP状态码，默认200（前后端分离常用）


# 5. 创建FastAPI应用实例
app = FastAPI(title="规范的用户管理接口", version="1.0")


# 6. 全局异常处理（核心！统一捕获所有异常）
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """捕获自定义异常，返回统一格式"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel(code=exc.code, msg=exc.msg, data=None).dict()
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """捕获Pydantic参数校验异常，返回统一格式"""
    error_msg = f"参数校验失败：{exc.errors()[0]['msg']}（字段：{exc.errors()[0]['loc'][-1]}）"
    return JSONResponse(
        status_code=200,
        content=ResponseModel(code=400, msg=error_msg, data=None).dict()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """捕获所有未处理的异常，返回统一格式"""
    return JSONResponse(
        status_code=200,
        content=ResponseModel(code=500, msg=f"服务器内部错误：{str(exc)}", data=None).dict()
    )


# 7. Pydantic数据模型（用户相关）
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="用户名，3-20个字符", example="zhangsan")
    email: EmailStr = Field(..., description="合法邮箱地址", example="zhangsan@example.com")
    password: str = Field(..., min_length=8, description="密码，最少8位", example="12345678")
    age: Optional[int] = Field(None, ge=18, le=100, description="年龄，可选，18-100岁", example=25)
    phone: Optional[str] = Field(None, pattern=r"^1\d{10}$", description="手机号，可选，11位中国大陆手机号",
                                 example="13800138000")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=20, description="用户名，3-20个字符")
    email: Optional[EmailStr] = Field(None, description="合法邮箱地址")
    password: Optional[str] = Field(None, min_length=8, description="密码，最少8位")
    age: Optional[int] = Field(None, ge=18, le=100, description="年龄，18-100岁")
    phone: Optional[str] = Field(None, pattern=r"^1\d{10}$", description="手机号，11位中国大陆手机号")


class UserResponse(BaseModel):
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    age: Optional[int] = Field(None, description="年龄")
    phone: Optional[str] = Field(None, description="手机号")
    created_at: datetime = Field(..., description="用户创建时间")

    class Config:
        from_attributes = True


# 8. 模拟数据库
fake_user_db = {}
next_user_id = 1


# 9. 规范的路由接口（返回统一响应格式）
@app.post("/users/", response_model=ResponseModel[UserResponse], summary="创建新用户")
def create_user(user_in: UserCreate):
    global next_user_id

    # 模拟：检查用户名是否已存在
    for user in fake_user_db.values():
        if user["username"] == user_in.username:
            raise CustomException(code=400, msg="用户名已存在")

    # 保存用户数据
    user_data = user_in.dict()
    user_data["user_id"] = next_user_id
    user_data["created_at"] = datetime.now()
    fake_user_db[next_user_id] = user_data
    next_user_id += 1

    # 返回统一格式的响应
    return ResponseModel(code=200, msg="创建成功", data=user_data)


@app.put("/users/{user_id}", response_model=ResponseModel[UserResponse], summary="更新用户信息")
def update_user(user_id: int, user_in: UserUpdate):
    # 检查用户是否存在
    if user_id not in fake_user_db:
        raise CustomException(code=404, msg="用户不存在")

    # 更新数据
    existing_user = fake_user_db[user_id]
    update_data = user_in.dict(exclude_unset=True)
    existing_user.update(update_data)
    fake_user_db[user_id] = existing_user

    return ResponseModel(code=200, msg="更新成功", data=existing_user)


@app.get("/users/{user_id}", response_model=ResponseModel[UserResponse], summary="获取用户详情")
def get_user(user_id: int):
    if user_id not in fake_user_db:
        raise CustomException(code=404, msg="用户不存在")
    return ResponseModel(code=200, msg="查询成功", data=fake_user_db[user_id])