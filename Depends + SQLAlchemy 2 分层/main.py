from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import models
from database import engine
from api import router as users_router

# 创建数据库表
try:
    models.Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建成功")
except Exception as e:
    logger.error(f"创建数据库表时出错: {e}")
    traceback.print_exc()

# FastAPI 实例
app = FastAPI(title="用户管理系统", description="分层版")

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {exc}")
    logger.error(f"异常详情: {traceback.format_exc()}")
    
    # 返回标准化的错误响应
    return JSONResponse(
        status_code=500,
        content={
            "code": 500, 
            "message": "服务器内部错误",
            "data": None
        }
    )

# 挂载路由
app.include_router(users_router)

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务正常运行"}
