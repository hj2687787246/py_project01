# 路由层
from fastapi import APIRouter

from .role_routes import router as role_router
from .user_routes import router as user_router

router = APIRouter()
router.include_router(user_router)
router.include_router(role_router)
