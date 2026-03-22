from contextlib import asynccontextmanager
import traceback

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.logger import get_logger
import schemas
from session.db_session import Base, engine

# 配置日志
logger = get_logger()
# 自定义业务异常
class BusinessException(Exception):
    def __init__(self, status_code: int, code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


from routers import router as users_router

# FastAPI 启动前执行数据库初始化检查
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表初始化检查完成")
    except Exception as e:
        logger.exception(f"数据库表初始化检查失败: {e}")
        raise
    yield


# FastAPI 实例
app = FastAPI(
    title="用户管理系统",
    description="分层版",
    lifespan=lifespan,
)

# 挂载路由
app.include_router(users_router)

# 捕获自定义业务异常，统一返回业务错误格式
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    logger.error(f"业务异常: {exc}")
    logger.error(f"异常详情: {traceback.format_exc()}")
    return JSONResponse(
        status_code=exc.status_code,
        content=schemas.UnifiedResponse(
            code=exc.code,
            message=exc.message,
            data=None,
        ).model_dump()
    )

# 捕获 HTTPException，统一包装成标准响应格式
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP异常: status_code={exc.status_code}, detail={exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=schemas.UnifiedResponse(
            code=exc.status_code,
            message=str(exc.detail),
            data=None,
        ).model_dump()
    )


# 捕获请求参数校验错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=schemas.UnifiedResponse(
            code=422,
            message=f"参数校验失败: {error_msg}",
            data=None,
        ).model_dump(),
    )

# 兜底异常捕获，避免直接返回堆栈信息
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"发生未捕获异常: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=schemas.UnifiedResponse(
            code=500,
            message="服务器内部错误，请联系管理员",
            data=None,
        ).model_dump(),
    )

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务正常运行"}
