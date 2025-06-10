from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)  # 操作类型，如"提交代码"、"删除题目"等
    target = Column(String, nullable=True)  # 操作对象，如题目名称或练习名称
    # details = Column(Text, nullable=True)  # 操作详情 - 数据库表中不存在此列
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="operation_logs") 