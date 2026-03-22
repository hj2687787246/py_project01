from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import traceback

from pydantic import BaseModel
from logger_config import get_logger
# 配置日志
logger = get_logger()

import models
from database import engine
from api import router as users_router

# 1.定义统一返回格式
class ResponseModel(BaseModel):
    code: int
    message: str
    data: dict | list | None = None

# 2.自定义业务异常类
class BusinessException(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message
# @asynccontextmanager
# -FastAPI 启动应用前，先执行 yield 前面的代码
# - 应用运行期间，控制权交给 FastAPI
# - 应用关闭时，再继续执行 yield 后面的代码
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("数据库表初始化检查完成")
    except Exception as e:
        logger.exception(f"数据库表初始化检查失败: {e}")
        raise
    yield

# FastAPI 实例
app = FastAPI(title="用户管理系统", description="分层版", lifespan=lifespan)
# 挂载路由
app.include_router(users_router)

# 3.捕获自定义业务异常 用来处理 “用户名已存在”、“权限不足” 等业务逻辑错误。
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    logger.error(f"全局异常: {exc}")
    logger.error(f"异常详情: {traceback.format_exc()}")
    
    # 返回标准化的错误响应
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseModel(
            code=exc.code,
            message=exc.message,
            data=None
        ).model_dump()
    )

# 4.捕获请求参数校验错误 比如前端传错了字段 FastAPI 自动抛出的，比如你要求传 int，前端传了个 str。
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 提取具体的错误信息
    error_msg= "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ResponseModel(
            code=422,
            message=f"参数校验失败：{error_msg}",
            data=None
        ).model_dump()
    )

# 5.兜底异常捕获，服务器内部错误 最后的防线，防止代码崩了直接给用户看堆栈信息。
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 记录详细的错误堆栈
    logger.exception(f"发生未捕获的异常：{str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ResponseModel(
            code=500,
            message="服务器内部错误，请联系管理员",
            data=None
        ).model_dump()
    )



# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务正常运行"}
