from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 直接从环境变量获取数据库URL，如果不存在则使用默认值
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cjudge:password@db:5432/cjudge")

# 创建数据库引擎 - 高性能连接池配置
engine = create_engine(
    DATABASE_URL,
    pool_size=100,         # 增加连接池大小
    max_overflow=200,      # 增加最大溢出连接数
    pool_timeout=5,        # 减少获取连接超时时间
    pool_recycle=1800,     # 减少连接回收时间（30分钟）
    pool_pre_ping=True,    # 连接前ping检查
    echo=False,            # 生产环境关闭SQL日志
    connect_args={
        "options": "-c default_transaction_isolation=read\\ committed",
        "connect_timeout": 10,
        "application_name": "cjudge_backend"
    },
    # 性能优化参数
    pool_reset_on_return='commit',  # 连接返回时重置
    isolation_level='READ_COMMITTED'  # 隔离级别
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