from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import User, Class, get_db, OperationLog
from app.utils.auth import get_current_active_user, get_teacher_user, get_admin_user
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse
from app.services import ClassService

router = APIRouter(prefix="/classes", tags=["班级"])

@router.get("/test")
async def test_classes_api():
    """测试班级API，无需身份验证"""
    return {"status": "ok", "message": "班级API工作正常"}

@router.get("/", response_model=List[ClassResponse])
async def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取班级列表"""
    # 记录操作日志
    ClassService.log_operation(db, current_user.id, "查看班级列表", "班级列表")
    
    # 获取班级列表
    return ClassService.get_classes(db, current_user.id)

@router.post("/", response_model=ClassResponse)
async def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """创建班级（仅限管理员）"""
    # 检查班级名称是否已存在
    if ClassService.check_class_name_exists(db, class_data.name):
        raise HTTPException(status_code=400, detail="班级名称已存在")
    
    # 创建班级
    new_class = ClassService.create_class(db, class_data.name)
    
    # 记录操作日志
    ClassService.log_operation(db, current_user.id, "创建班级", new_class.name)
    
    # 返回创建的班级信息
    return {
        "id": new_class.id,
        "name": new_class.name,
        "created_at": new_class.created_at,
        "student_count": 0
    }

@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """更新班级（仅限管理员）"""
    # 检查班级名称是否已存在（如果更改了名称）
    if ClassService.check_class_name_exists(db, class_data.name, exclude_id=class_id):
        raise HTTPException(status_code=400, detail="班级名称已存在")
    
    # 更新班级
    class_item = ClassService.update_class(db, class_id, class_data.name)
    if not class_item:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 记录操作日志
    ClassService.log_operation(db, current_user.id, "更新班级", class_item.name)
    
    # 返回更新后的班级信息
    return {
        "id": class_item.id,
        "name": class_item.name,
        "created_at": class_item.created_at,
        "student_count": len(class_item.students)
    }

@router.delete("/{class_id}")
async def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """删除班级（仅限管理员）"""
    # 查询班级
    class_item = db.query(Class).filter(Class.id == class_id).first()
    if not class_item:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 记录操作日志
    ClassService.log_operation(db, current_user.id, "删除班级", class_item.name)
    
    # 删除班级
    success = ClassService.delete_class(db, class_id)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="无法删除班级，请确保班级内没有学生且未关联任何课程"
        )
    
    return {"message": "班级删除成功"} 