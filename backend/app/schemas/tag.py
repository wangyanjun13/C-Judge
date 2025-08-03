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
    tag_type_id: Optional[int] = None

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

# 标签审核请求相关模型
class TagApprovalRequestBase(BaseModel):
    """标签审核请求基础模型"""
    problem_data_path: str
    tag_ids: List[int]
    request_message: Optional[str] = None

class TagApprovalRequestCreate(TagApprovalRequestBase):
    """创建标签审核请求"""
    pass

class TagApprovalRequestUpdate(BaseModel):
    """审核标签申请（管理员使用）"""
    status: str  # 'approved' or 'rejected'
    review_message: Optional[str] = None

class TagApprovalRequest(TagApprovalRequestBase):
    """标签审核请求响应模型"""
    id: int
    requestor_id: int
    status: str
    reviewer_id: Optional[int] = None
    review_message: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    requestor: Optional[dict] = None  # 简化的用户信息
    reviewer: Optional[dict] = None   # 简化的用户信息
    
    class Config:
        orm_mode = True

# 解决循环引用问题
TagType.update_forward_refs() 