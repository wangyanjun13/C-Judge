from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import User, Class, get_db, OperationLog
from app.utils.auth import get_current_active_user, get_teacher_user, get_admin_user
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse
from app.services import ClassService

router = APIRouter(prefix="/classes", tags=["班级"])

@router.get("/", response_model=List[ClassResponse])
async def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取班级列表"""
    # 获取班级列表
    classes = ClassService.get_classes(db, current_user.id)
    
    # 确保每个班级对象都包含student_count字段
    for class_item in classes:
        if "student_count" not in class_item:
            class_item["student_count"] = 0
    
    return classes

@router.post("/", response_model=ClassResponse)
async def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建班级（管理员可创建任意班级，教师只能创建自己作为教师的班级）"""
    # 检查权限
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="没有权限创建班级")
    
    # 检查班级名称是否已存在
    if ClassService.check_class_name_exists(db, class_data.name):
        raise HTTPException(status_code=400, detail="班级名称已存在")
    
    # 如果是教师，只能将自己设为教师
    if current_user.role == "teacher":
        if len(class_data.teacher_ids) != 1 or class_data.teacher_ids[0] != current_user.id:
            raise HTTPException(status_code=400, detail="教师只能创建自己作为教师的班级")
    
    # 创建班级
    new_class = ClassService.create_class(db, class_data.name, class_data.teacher_ids)
    
    # 记录操作日志
    ClassService.log_operation(db, current_user.id, "创建班级", new_class.name)
    
    # 手动构造符合ClassResponse模型的响应数据
    response_data = {
        "id": new_class.id,
        "name": new_class.name,
        "created_at": new_class.created_at,
        "student_count": len(new_class.students),
        "teachers": [
            {
                "id": teacher.id,
                "username": teacher.username,
                "real_name": teacher.real_name
            } for teacher in new_class.teachers
        ]
    }
    
    return response_data

@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新班级（管理员可更新任意班级，教师只能更新自己的班级）"""
    # 检查权限
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="没有权限更新班级")
    
    # 获取班级
    class_item = db.query(Class).filter(Class.id == class_id).first()
    if not class_item:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 如果是教师，检查是否是该班级的教师
    if current_user.role == "teacher":
        if current_user not in class_item.teachers:
            raise HTTPException(status_code=403, detail="只能更新自己的班级")
        if len(class_data.teacher_ids) != 1 or class_data.teacher_ids[0] != current_user.id:
            raise HTTPException(status_code=400, detail="教师不能更改班级的教师")
    
    # 检查班级名称是否已存在
    if ClassService.check_class_name_exists(db, class_data.name, exclude_id=class_id):
        raise HTTPException(status_code=400, detail="班级名称已存在")
    
    # 更新班级
    class_item = ClassService.update_class(db, class_id, class_data.name, class_data.teacher_ids)
    if not class_item:
        raise HTTPException(status_code=404, detail="班级更新失败")
    
    # 记录操作日志
    ClassService.log_operation(db, current_user.id, "更新班级", class_item.name)
    
    # 手动构造符合ClassResponse模型的响应数据
    response_data = {
        "id": class_item.id,
        "name": class_item.name,
        "created_at": class_item.created_at,
        "student_count": len(class_item.students),
        "teachers": [
            {
                "id": teacher.id,
                "username": teacher.username,
                "real_name": teacher.real_name
            } for teacher in class_item.teachers
        ]
    }
    
    return response_data

@router.delete("/{class_id}")
async def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除班级（管理员可删除任意班级，教师只能删除自己的班级）"""
    # 检查权限
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="没有权限删除班级")
    
    # 获取班级
    class_item = db.query(Class).filter(Class.id == class_id).first()
    if not class_item:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 如果是教师，检查是否是该班级的教师
    if current_user.role == "teacher":
        if current_user not in class_item.teachers:
            raise HTTPException(status_code=403, detail="只能删除自己的班级")
    
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

@router.get("/teacher", response_model=List[ClassResponse])
async def get_teacher_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """获取当前教师关联的班级列表"""
    # 使用现有服务方法获取教师关联的班级
    classes = ClassService.get_classes(db, current_user.id)
    
    # 确保每个班级对象都包含student_count字段
    for class_item in classes:
        if "student_count" not in class_item:
            class_item["student_count"] = 0
    
    return classes 