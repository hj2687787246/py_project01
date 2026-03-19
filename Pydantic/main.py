# 1. 导入核心依赖
from fastapi import FastAPI, HTTPException
# 从 pydantic 导入 BaseModel（所有数据模型的基类）和 Field（用来做更细的字段校验）
from pydantic import BaseModel, Field, EmailStr
# 导入 datetime 用来模拟创建时间
from datetime import datetime
# 导入 typing 的 Optional 用来定义可选字段
from typing import Optional

# 2. 创建 FastAPI 应用实例
app = FastAPI(title="Pydantic参数校验入门demo", version="1.0")


# ------------------- 3. 定义Pydantic数据模型（核心重点！） -------------------
# 模型1：创建用户时的请求体（所有必填字段都在这里，带严格校验）
class UserCreate(BaseModel):
    # Field的第一个参数是默认值，... 表示「必填，无默认值」
    # min_length/max_length：字符串长度限制
    # description：字段描述，会显示在/docs文档里
    # example：字段示例，会显示在/docs的「Try it out」里
    username: str = Field(..., min_length=3, max_length=20, description="用户名，3-20个字符", example="zhangsan")
    # EmailStr：Pydantic内置的邮箱格式校验，自动验证是否是合法邮箱
    email: EmailStr = Field(..., description="合法邮箱地址", example="zhangsan@example.com")
    # min_length：密码最少8位；我们可以后续加正则匹配，但先从简单的来
    password: str = Field(..., min_length=8, description="密码，最少8位", example="12345678")
    # Optional[int]：表示这是可选字段，可以不传；ge=18, le=100：数值范围（18<=年龄<=100）
    age: Optional[int] = Field(None, ge=18, le=100, description="年龄，可选，18-100岁", example=25)
    # regex改成pattern：正则匹配，这里用来匹配中国大陆手机号（1开头，后面10位数字）
    phone: Optional[str] = Field(None, pattern=r"^1\d{10}$", description="手机号，可选，11位中国大陆手机号",
                                 example="13800138000")


# 模型2：更新用户时的请求体（所有字段都是可选的，因为更新可能只改一部分）
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=20, description="用户名，3-20个字符")
    email: Optional[EmailStr] = Field(None, description="合法邮箱地址")
    password: Optional[str] = Field(None, min_length=8, description="密码，最少8位")
    age: Optional[int] = Field(None, ge=18, le=100, description="年龄，18-100岁")
    phone: Optional[str] = Field(None, pattern=r"^1\d{10}$", description="手机号，11位中国大陆手机号")


# 模型3：返回给前端的响应体（不要返回密码！只返回安全的用户信息）
class UserResponse(BaseModel):
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    age: Optional[int] = Field(None, description="年龄")
    phone: Optional[str] = Field(None, description="手机号")
    created_at: datetime = Field(..., description="用户创建时间")

    # Config类是Pydantic的配置类，这里用来告诉Pydantic：
    # 即使传入的是ORM对象（比如数据库查询结果），也能转换成这个响应模型
    class Config:
        from_attributes = True


# ------------------- 4. 模拟数据库（不用真的连数据库，用内存字典存数据） -------------------
fake_user_db = {}
# 模拟自增ID
next_user_id = 1


# ------------------- 5. 定义带参数校验的路由 -------------------
# 路由1：创建用户（POST请求，接收UserCreate请求体）
@app.post("/users/", response_model=UserResponse, summary="创建新用户",
          description="传入符合要求的用户信息，自动校验参数后创建用户")
def create_user(user_in: UserCreate):
    global next_user_id

    # 模拟保存到数据库
    user_data = user_in.dict()  # 把Pydantic模型转换成Python字典
    user_data["user_id"] = next_user_id
    user_data["created_at"] = datetime.now()

    # 存入模拟数据库
    fake_user_db[next_user_id] = user_data
    next_user_id += 1

    # 返回UserResponse模型（自动过滤掉password字段）
    return user_data


# 路由2：更新用户（PUT请求，接收路径参数user_id和UserUpdate请求体）
@app.put("/users/{user_id}", response_model=UserResponse, summary="更新用户信息",
         description="传入用户ID和要更新的字段，只更新传入的字段")
def update_user(user_id: int, user_in: UserUpdate):
    # 先检查用户是否存在
    if user_id not in fake_user_db:
        # 如果不存在，抛出404错误（HTTPException是FastAPI内置的错误处理）
        raise HTTPException(status_code=404, detail="用户不存在")
    # 获取现有用户数据
    existing_user = fake_user_db[user_id]
    # 把要更新的字段转换成字典，exclude_unset=True表示「只转换用户传入的字段，不传的字段保持原样」
    update_data = user_in.dict(exclude_unset=True)
    # 更新现有用户数据
    existing_user.update(update_data)
    # 保存回模拟数据库
    fake_user_db[user_id] = existing_user
    # 返回更新后的用户信息
    return existing_user


# 路由3：获取用户详情（GET请求，接收路径参数user_id）
@app.get("/users/{user_id}", response_model=UserResponse, summary="获取用户详情",
         description="传入用户ID，返回用户的完整信息（不含密码）")
def get_user(user_id: int):
    if user_id not in fake_user_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    return fake_user_db[user_id]