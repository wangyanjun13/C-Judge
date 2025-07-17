from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from app.models import get_db
from app.schemas.tag import TagType, Tag, TagCreate, TagUpdate, TagTypeCreate, TagTypeUpdate
from app.services.tag_service import TagService
import logging

# 创建路由
router = APIRouter(prefix="/tags", tags=["tags"])

logger = logging.getLogger(__name__)

# 标签类型API
@router.get("/types", response_model=List[TagType])
async def get_tag_types(db: Session = Depends(get_db)):
    """获取所有标签类型"""
    return TagService.get_tag_types(db)

@router.post("/types", response_model=TagType)
async def create_tag_type(tag_type: TagTypeCreate, db: Session = Depends(get_db)):
    """创建标签类型"""
    return TagService.create_tag_type(db, tag_type)

@router.get("/types/{tag_type_id}", response_model=TagType)
async def get_tag_type(tag_type_id: int, db: Session = Depends(get_db)):
    """获取标签类型"""
    tag_type = TagService.get_tag_type(db, tag_type_id)
    if not tag_type:
        raise HTTPException(status_code=404, detail="标签类型不存在")
    return tag_type

@router.put("/types/{tag_type_id}", response_model=TagType)
async def update_tag_type(tag_type_id: int, tag_type: TagTypeUpdate, db: Session = Depends(get_db)):
    """更新标签类型"""
    updated_tag_type = TagService.update_tag_type(db, tag_type_id, tag_type)
    if not updated_tag_type:
        raise HTTPException(status_code=404, detail="标签类型不存在")
    return updated_tag_type

@router.delete("/types/{tag_type_id}")
async def delete_tag_type(tag_type_id: int, db: Session = Depends(get_db)):
    """删除标签类型"""
    success = TagService.delete_tag_type(db, tag_type_id)
    if not success:
        raise HTTPException(status_code=404, detail="标签类型不存在")
    return {"message": "标签类型已删除"}

# 标签API
@router.get("", response_model=List[Tag])
async def get_tags(tag_type_id: int = None, db: Session = Depends(get_db)):
    """获取所有标签，可以按标签类型过滤"""
    return TagService.get_tags(db, tag_type_id)

@router.post("", response_model=Tag)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    return TagService.create_tag(db, tag)

@router.get("/{tag_id}", response_model=Tag)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取标签"""
    tag = TagService.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return tag

@router.put("/{tag_id}", response_model=Tag)
async def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    """更新标签"""
    updated_tag = TagService.update_tag(db, tag_id, tag)
    if not updated_tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return updated_tag

@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """删除标签"""
    success = TagService.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="标签不存在")
    return {"message": "标签已删除"}

# 问题标签API
@router.get("/problem/{problem_id_or_path:path}", response_model=List[Tag])
async def get_problem_tags(problem_id_or_path: str, db: Session = Depends(get_db)):
    """获取问题的标签，支持通过ID或data_path查找"""
    # 移除不必要的日志
    tags = TagService.get_problem_tags(db, problem_id_or_path)
    return tags

@router.post("/problem/{problem_id_or_path:path}/tag/{tag_id}")
async def add_tag_to_problem(problem_id_or_path: str, tag_id: int, db: Session = Depends(get_db)):
    """为问题添加标签，支持通过ID或data_path查找"""
    success = TagService.add_tag_to_problem(db, problem_id_or_path, tag_id)
    if not success:
        logger.error(f"问题或标签不存在：{problem_id_or_path}, {tag_id}")
        raise HTTPException(status_code=404, detail="问题或标签不存在")
    return {"message": "标签已添加到问题"}

@router.delete("/problem/{problem_id_or_path:path}/tag/{tag_id}")
async def remove_tag_from_problem(problem_id_or_path: str, tag_id: int, db: Session = Depends(get_db)):
    """从问题中移除标签，支持通过ID或data_path查找"""
    success = TagService.remove_tag_from_problem(db, problem_id_or_path, tag_id)
    if not success:
        logger.error(f"问题或标签不存在，或标签未添加到问题：{problem_id_or_path}, {tag_id}")
        raise HTTPException(status_code=404, detail="问题或标签不存在，或标签未添加到问题")
    return {"message": "标签已从问题中移除"}

@router.put("/problem/{problem_id_or_path:path}/tags")
async def set_problem_tags(problem_id_or_path: str, tag_ids: List[int], db: Session = Depends(get_db)):
    """设置问题的标签，支持通过ID或data_path查找"""
    success = TagService.set_problem_tags(db, problem_id_or_path, tag_ids)
    if not success:
        logger.error(f"问题不存在：{problem_id_or_path}")
        raise HTTPException(status_code=404, detail="问题不存在")
    return {"message": "问题标签已更新"}

@router.post("/problems/batch-tags")
async def get_problems_batch_tags(problem_paths: List[str], db: Session = Depends(get_db)):
    """批量获取多个问题的标签"""
    if not problem_paths:
        return {}
    
    # 记录请求信息
    logger.info(f"批量获取标签: 收到 {len(problem_paths)} 个路径")
    
    # 使用优化的批量获取方法
    try:
        result = TagService.get_problems_batch_tags(db, problem_paths)
        
        # 确保所有标签都有tag_type_id字段
        for path, tags in result.items():
            for tag in tags:
                if not hasattr(tag, 'tag_type_id') or tag.tag_type_id is None:
                    tag.tag_type_id = None
        
        logger.info(f"批量获取标签完成: 处理了 {len(result)} 个路径")
        return result
    except Exception as e:
        logger.error(f"批量获取标签失败: {str(e)}")
        return {}