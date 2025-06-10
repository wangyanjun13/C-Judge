from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.models.database import Base


class SystemSetting(Base):
    """系统设置模型"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)

    @classmethod
    def get_setting(cls, db, key, default=None):
        """获取系统设置值"""
        setting = db.query(cls).filter(cls.key == key).first()
        if setting:
            return setting.value
        return default

    @classmethod
    def set_setting(cls, db, key, value, description=None):
        """设置系统设置值"""
        setting = db.query(cls).filter(cls.key == key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = cls(key=key, value=value, description=description)
            db.add(setting)
        db.commit()
        return setting 