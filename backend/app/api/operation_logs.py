from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.models import get_db, OperationLog
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/operation-logs", tags=["操作日志"])

@router.get("/", response_model=List[dict])
async def get_user_operation_logs(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的操作日志
    """
    query = db.query(OperationLog).filter(OperationLog.user_id == current_user.id)
    
    # 日期过滤
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(OperationLog.created_at >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="开始日期格式无效")
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(OperationLog.created_at < end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="结束日期格式无效")
    
    # 按时间倒序排序
    query = query.order_by(OperationLog.created_at.desc())
    
    # 分页
    logs = query.offset(skip).limit(limit).all()
    
    # 转换为字典列表
    result = []
    for log in logs:
        # 使用当前时间替代错误的未来时间
        created_at = log.created_at
        if created_at and created_at.year > datetime.now().year:
            created_at = datetime.now()
            
        result.append({
            "id": log.id,
            "operation": log.operation,
            "target": log.target,
            "created_at": created_at.isoformat(),
            "user_id": log.user_id
        })
    
    return result

@router.post("/")
async def create_operation_log(
    operation: str,
    target: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建操作日志
    """
    # 使用当前时间
    now = datetime.now()
    
    log = OperationLog(
        user_id=current_user.id,
        operation=operation,
        target=target,
        created_at=now  # 明确设置当前时间
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"success": True, "id": log.id}

@router.delete("/")
async def clear_user_operation_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    清空当前用户的所有操作日志
    """
    # 查询当前用户的所有日志
    logs = db.query(OperationLog).filter(OperationLog.user_id == current_user.id).all()
    
    # 记录删除的日志数量
    deleted_count = len(logs)
    
    # 删除所有日志
    for log in logs:
        db.delete(log)
    
    db.commit()
    
    # 创建一条新的日志，记录清空操作
    now = datetime.now()
    
    new_log = OperationLog(
        user_id=current_user.id,
        operation="清空操作记录",
        target=f"已删除 {deleted_count} 条记录",
        created_at=now  # 明确设置当前时间
    )
    db.add(new_log)
    db.commit()
    
    return {"success": True, "deleted_count": deleted_count} 