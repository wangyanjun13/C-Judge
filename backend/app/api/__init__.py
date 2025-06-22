from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.exercises import router as exercises_router
from app.api.classes import router as classes_router
from app.api.users import router as users_router
from app.api.courses import router as courses_router
from app.api.problems import router as problems_router
from app.api.submissions import router as submissions_router
from app.api.operation_logs import router as operation_logs_router

# 创建主路由
api_router = APIRouter(prefix="/api")

# 包含子路由
api_router.include_router(auth_router)
api_router.include_router(exercises_router)
api_router.include_router(classes_router)
api_router.include_router(users_router)
api_router.include_router(courses_router)
api_router.include_router(problems_router)
api_router.include_router(submissions_router)
api_router.include_router(operation_logs_router)

# 导出API路由
__all__ = ["api_router"] 