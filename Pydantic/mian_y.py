# ------------------------------
# 1. 导入核心依赖（更新为最新写法）
# ------------------------------
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import (
    BaseModel, Field, EmailStr, ValidationError, ConfigDict
)
from pydantic.types import StringConstraints, Range
from datetime import datetime
from typing import Generic, TypeVar, Annotated

# ------------------------------
# 2. 预定义可复用的「类型约束别名」（核心优化）
# ------------------------------
T = TypeVar("T")

# 用户名：3-20个字符
Username = Annotated[
    str,
    StringConstraints(min_length=3, max_length=20),
    Field(description="用户名，3-20个字符", examples=["zhangsan"])
]

# 邮箱：合法邮箱地址
UserEmail = Annotated[
    EmailStr,
    Field(description="合法邮箱地址", examples=["zhangsan@example.com"])
]

# 密码：最少8位
UserPassword = Annotated[
    str,
    StringConstraints(min_length=8),
    Field(description="密码，最少8位", examples=["12345678"])
]

# 年龄：可选，18-100岁
UserAge = Annotated[
    int | None,  # Python 3.10+ 推荐用 | 替代 Optional
    Range(ge=18, le=100),
    Field(None, description="年龄，可选，18-100岁", examples=[25])
]

# 手机号：可选，11位中国大陆手机号（13-19开头）
UserPhone = Annotated[
    str | None,
    StringConstraints(pattern=r"^1[3-9]\d{9}$"),
    Field(None, description="手机号，可选，11位中国大陆手机号", examples=["13800138000"])
]

# ------------------------------
# 3. 统一响应格式模型（更新为 Pydantic v2 写法）
# ------------------------------
class ResponseModel(BaseModel, Generic[T]):
    code: int = Field(..., description="状态码：200成功，其他失败")
    msg: str = Field(..., description="提示信息")
    data: T | None = Field(None, description="业务数据，成功时返回，失败时为null")

    # Pydantic v2 用 model_config 替代 Config 类
    model_config = ConfigDict(from_attributes=True)

# ------------------------------
# 4. 自定义异常类（保持不变，逻辑通用）
# ------------------------------
class CustomException(HTTPException):
    def __init__(self, code: int, msg: str, status_code: int = 200):
        self.code = code
        self.msg = msg
        self.status_code = status_code

# ------------------------------
# 5. 创建FastAPI应用实例（保持不变）
# ------------------------------
app = FastAPI(title="规范的用户管理接口", version="1.0")

# ------------------------------
# 6. 全局异常处理（修正旧版 .dict() 为 .model_dump()）
# ------------------------------
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel(code=exc.code, msg=exc.msg, data=None).model_dump()
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    error_msg = f"参数校验失败：{exc.errors()[0]['msg']}（字段：{exc.errors()[0]['loc'][-1]}）"
    return JSONResponse(
        status_code=200,
        content=ResponseModel(code=400, msg=error_msg, data=None).model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content=ResponseModel(code=500, msg=f"服务器内部错误：{str(exc)}", data=None).model_dump()
    )

# ------------------------------
# 7. Pydantic数据模型（使用预定义的类型别名，代码大幅简化）
# ------------------------------
class UserCreate(BaseModel):
    username: Username
    email: UserEmail
    password: UserPassword
    age: UserAge
    phone: UserPhone

class UserUpdate(BaseModel):
    username: Username | None = None
    email: UserEmail | None = None
    password: UserPassword | None = None
    age: UserAge
    phone: UserPhone

class UserResponse(BaseModel):
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    age: int | None = Field(None, description="年龄")
    phone: str | None = Field(None, description="手机号")
    created_at: datetime = Field(..., description="用户创建时间")

    model_config = ConfigDict(from_attributes=True)

# ------------------------------
# 8. 模拟数据库（保持不变）
# ------------------------------
fake_user_db = {}
next_user_id = 1

# ------------------------------
# 9. 规范的路由接口（修正旧版 .dict() 为 .model_dump()）
# ------------------------------
@app.post("/users/", response_model=ResponseModel[UserResponse], summary="创建新用户")
def create_user(user_in: UserCreate):
    global next_user_id

    for user in fake_user_db.values():
        if user["username"] == user_in.username:
            raise CustomException(code=400, msg="用户名已存在")

    # 修正：.dict() → .model_dump()
    user_data = user_in.model_dump()
    user_data["user_id"] = next_user_id
    user_data["created_at"] = datetime.now()
    fake_user_db[next_user_id] = user_data
    next_user_id += 1

    return ResponseModel(code=200, msg="创建成功", data=user_data)

@app.put("/users/{user_id}", response_model=ResponseModel[UserResponse], summary="更新用户信息")
def update_user(user_id: int, user_in: UserUpdate):
    if user_id not in fake_user_db:
        raise CustomException(code=404, msg="用户不存在")

    existing_user = fake_user_db[user_id]
    # 修正：.dict(exclude_unset=True) → .model_dump(exclude_unset=True)
    update_data = user_in.model_dump(exclude_unset=True)
    existing_user.update(update_data)
    fake_user_db[user_id] = existing_user

    return ResponseModel(code=200, msg="更新成功", data=existing_user)

@app.get("/users/{user_id}", response_model=ResponseModel[UserResponse], summary="获取用户详情")
def get_user(user_id: int):
    if user_id not in fake_user_db:
        raise CustomException(code=404, msg="用户不存在")
    return ResponseModel(code=200, msg="查询成功", data=fake_user_db[user_id])