import os

class Settings:
    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cjudge.db")
    
    # 评测服务配置
    JUDGE_SERVER_URL = os.getenv("JUDGE_SERVER_URL", "http://oj-judge:8080")
    JUDGE_SERVER_TOKEN = os.getenv("JUDGE_SERVER_TOKEN", "12345678")
    
    # 应用配置
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1天

# 创建一个settings实例
settings = Settings() 