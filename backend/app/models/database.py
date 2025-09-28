from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 直接从环境变量获取数据库URL，如果不存在则使用默认值
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cjudge:password@db:5432/cjudge")

# 创建数据库引擎
# engine = create_engine(DATABASE_URL)

# 创建数据库引擎 - 4核8G服务器高并发优化配置
engine = create_engine(
    DATABASE_URL,
    pool_size=50,          # 增加连接池大小以支持100+并发
    max_overflow=100,      # 增加溢出连接数，支持突发流量
    pool_timeout=60,       # 增加获取连接超时时间
    pool_recycle=1800,     # 连接回收时间（30分钟）
    pool_pre_ping=True,    # 连接前ping检查
    echo=False,            # 关闭SQL日志
    connect_args={
        "connect_timeout": 60,  # 增加连接超时时间
        "application_name": "cjudge_backend",
        "options": "-c default_transaction_isolation=read\\ committed"  # 优化事务隔离级别
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 