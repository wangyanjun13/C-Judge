from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 基础模型
class TagTypeBase(BaseModel):
    """标签类型基础模型"""
    name: str

class TagBase(BaseModel):
    """标签基础模型"""
    name: str
    tag_type_id: int

# 创建模型
class TagTypeCreate(TagTypeBase):
    pass

class TagCreate(TagBase):
    pass

# 更新模型
class TagTypeUpdate(TagTypeBase):
    pass

class TagUpdate(TagBase):
    name: Optional[str] = None
    tag_type_id: Optional[int] = None

# 数据库模型
class TagTypeInDB(TagTypeBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TagInDB(TagBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# 响应模型
class TagType(TagTypeInDB):
    tags: List["Tag"] = []

class Tag(TagInDB):
    tag_type: Optional[TagTypeBase] = None

# 解决循环引用问题
TagType.update_forward_refs() 