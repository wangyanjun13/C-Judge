import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.database import Base, engine
from app.api import api_router

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="C-Judge API",
    description="C语言评测系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization", "Content-Length"]
)

# 包含API路由
app.include_router(api_router)

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 全局测试API
@app.get("/api/test")
async def test_api():
    return {"status": "ok", "message": "API连接正常"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
