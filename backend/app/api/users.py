from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
import os
from datetime import datetime

from app.models import User, Class, get_db, OperationLog, student_class
from app.utils.auth import get_current_active_user, get_teacher_user, get_admin_user, get_password_hash
from app.schemas.user import UserCreate, UserUpdate, UserResponse, TeacherResponse, StudentResponse

router = APIRouter(prefix="/users", tags=["用户"])

@router.get("/teachers", response_model=List[TeacherResponse])
async def get_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """获取教师列表（仅限管理员）"""
    # 查询所有教师
    teachers = db.query(User).filter(User.role == "teacher").all()
    
    return teachers

@router.get("/students", response_model=List[StudentResponse])
async def get_students(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取学生列表"""
    
    # 构建查询条件
    query = db.query(User).filter(User.role == "student")
    
    # 根据用户角色和班级筛选学生
    if current_user.role == "admin":
        # 管理员可以查看所有学生，如果指定了班级则筛选
        if class_id:
            query = query.join(student_class).filter(student_class.c.class_id == class_id)
    elif current_user.role == "teacher":
        # 教师只能查看其课程关联班级的学生
        teacher_courses = current_user.courses
        class_ids = set()
        for course in teacher_courses:
            for class_item in course.classes:
                class_ids.add(class_item.id)
        
        # 如果指定了班级，检查教师是否有权限查看该班级
        if class_id:
            if class_id not in class_ids:
                raise HTTPException(status_code=403, detail="无权查看此班级的学生")
            query = query.join(student_class).filter(student_class.c.class_id == class_id)
        else:
            # 查看所有自己有权限的班级的学生
            query = query.join(student_class).filter(student_class.c.class_id.in_(class_ids))
    else:
        # 学生只能查看自己所在班级的其他学生
        student_class_ids = [cls.id for cls in current_user.classes]
        if class_id:
            if class_id not in student_class_ids:
                raise HTTPException(status_code=403, detail="无权查看此班级的学生")
            query = query.join(student_class).filter(student_class.c.class_id == class_id)
        else:
            query = query.join(student_class).filter(student_class.c.class_id.in_(student_class_ids))
    
    # 查询学生
    students = query.all()
    
    return students

@router.post("/teacher", response_model=TeacherResponse)
async def create_teacher(
    teacher_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """创建教师账号（仅限管理员）"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == teacher_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建教师账号
    hashed_password = get_password_hash(teacher_data.password)
    new_teacher = User(
        username=teacher_data.username,
        password=hashed_password,
        real_name=teacher_data.real_name,
        role="teacher"
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    
    # 记录操作日志
    now = datetime.now()
    log = OperationLog(
        user_id=current_user.id,
        operation="创建教师账号",
        target=new_teacher.username,
        created_at=now
    )
    db.add(log)
    db.commit()
    
    return new_teacher

@router.post("/student", response_model=StudentResponse)
async def create_student(
    student_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建学生账号"""
    # 检查权限（只有管理员和教师可以创建学生账号）
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail="无权创建学生账号")
    
    # 从请求体中提取必要字段
    try:
        username = student_data.get("username")
        password = student_data.get("password")
        real_name = student_data.get("real_name")
        class_ids = student_data.get("class_ids", [])
        
        if not username or not password or not real_name:
            raise HTTPException(status_code=400, detail="缺少必要字段")
    except Exception as e:
        print(f"参数解析错误: {e}, 接收到的数据: {student_data}")
        raise HTTPException(status_code=400, detail=f"参数解析错误: {str(e)}")
    
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查班级是否存在
    for class_id in class_ids:
        class_item = db.query(Class).filter(Class.id == class_id).first()
        if not class_item:
            raise HTTPException(status_code=404, detail=f"班级ID {class_id} 不存在")
        
        # 如果是教师创建，检查教师是否有权限操作该班级
        if current_user.role == "teacher":
            teacher_class_ids = set()
            for course in current_user.courses:
                for cls in course.classes:
                    teacher_class_ids.add(cls.id)
            
            if class_id not in teacher_class_ids:
                raise HTTPException(status_code=403, detail=f"无权向班级ID {class_id} 添加学生")
    
    # 创建学生账号
    hashed_password = get_password_hash(password)
    new_student = User(
        username=username,
        password=hashed_password,
        real_name=real_name,
        role="student"
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    # 添加班级关联
    for class_id in class_ids:
        class_item = db.query(Class).filter(Class.id == class_id).first()
        new_student.classes.append(class_item)
    
    db.commit()
    db.refresh(new_student)
    
    # 记录操作日志
    now = datetime.now()
    log = OperationLog(
        user_id=current_user.id,
        operation="创建学生账号",
        target=new_student.username,
        created_at=now
    )
    db.add(log)
    db.commit()
    
    return new_student

@router.put("/teacher/{user_id}", response_model=TeacherResponse)
async def update_teacher(
    user_id: int,
    teacher_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """更新教师信息（仅限管理员）"""
    # 查询教师
    teacher = db.query(User).filter(User.id == user_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    
    # 更新教师信息
    if teacher_data.real_name:
        teacher.real_name = teacher_data.real_name
    
    if teacher_data.password:
        teacher.password = get_password_hash(teacher_data.password)
    
    db.commit()
    db.refresh(teacher)
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        operation="更新教师信息",
        target=teacher.username
    )
    db.add(log)
    db.commit()
    
    return teacher

@router.put("/student/{user_id}", response_model=StudentResponse)
async def update_student(
    user_id: int,
    student_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新学生信息"""
    # 查询学生
    student = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 检查权限
    if current_user.role == "student" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="无权更新其他学生信息")
    
    # 从请求体中提取字段
    try:
        real_name = student_data.get("real_name")
        password = student_data.get("password")
        class_ids = student_data.get("class_ids")
        
        print(f"接收到的学生数据: {student_data}")
    except Exception as e:
        print(f"参数解析错误: {e}, 接收到的数据: {student_data}")
        raise HTTPException(status_code=400, detail=f"参数解析错误: {str(e)}")
    
    # 更新学生信息
    if real_name:
        student.real_name = real_name
    
    if password:
        student.password = get_password_hash(password)
    
    # 如果是管理员或教师且提供了班级ID，更新学生班级
    if (current_user.role == "admin" or current_user.role == "teacher") and class_ids is not None:
        # 检查班级是否存在
        for class_id in class_ids:
            class_item = db.query(Class).filter(Class.id == class_id).first()
            if not class_item:
                raise HTTPException(status_code=404, detail=f"班级ID {class_id} 不存在")
            
            # 如果是教师创建，检查教师是否有权限操作该班级
            if current_user.role == "teacher":
                teacher_class_ids = set()
                for course in current_user.courses:
                    for cls in course.classes:
                        teacher_class_ids.add(cls.id)
                
                if class_id not in teacher_class_ids:
                    raise HTTPException(status_code=403, detail=f"无权操作班级ID {class_id}")
        
        # 清除现有班级关联
        student.classes = []
        
        # 添加新班级关联
        for class_id in class_ids:
            class_item = db.query(Class).filter(Class.id == class_id).first()
            student.classes.append(class_item)
    
    db.commit()
    db.refresh(student)
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        operation="更新学生信息",
        target=student.username
    )
    db.add(log)
    db.commit()
    
    return student

@router.delete("/teacher/{user_id}")
async def delete_teacher(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """删除教师账号（仅限管理员）"""
    # 查询教师
    teacher = db.query(User).filter(User.id == user_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    
    # 检查是否有课程关联该教师
    if teacher.courses:
        raise HTTPException(status_code=400, detail="教师有关联的课程，请先删除或转移这些课程")
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        operation="删除教师账号",
        target=teacher.username
    )
    db.add(log)
    
    # 删除教师
    db.delete(teacher)
    db.commit()
    
    return {"message": "教师删除成功"}

@router.delete("/student/{user_id}")
async def delete_student(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除学生账号"""
    # 查询学生
    student = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 检查权限
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail="学生无权删除账号")
    
    if current_user.role == "teacher":
        # 检查教师是否有权限操作该学生所在班级
        teacher_class_ids = set()
        for course in current_user.courses:
            for cls in course.classes:
                teacher_class_ids.add(cls.id)
        
        student_class_ids = [cls.id for cls in student.classes]
        
        if not any(class_id in teacher_class_ids for class_id in student_class_ids):
            raise HTTPException(status_code=403, detail="无权删除此学生")
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        operation="删除学生账号",
        target=student.username
    )
    db.add(log)
    
    # 删除学生
    db.delete(student)
    db.commit()
    
    return {"message": "学生删除成功"}

@router.post("/import")
async def import_students(
    file: UploadFile = File(...),
    class_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量导入学生"""
    # 检查权限
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail="学生无权导入账号")
    
    try:
        class_id_int = int(class_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="班级ID必须是整数")
    
    # 检查班级是否存在
    class_item = db.query(Class).filter(Class.id == class_id_int).first()
    if not class_item:
        raise HTTPException(status_code=404, detail=f"班级不存在 (ID: {class_id_int})")
    
    # 如果是教师，检查是否有权限操作该班级
    if current_user.role == "teacher":
        teacher_class_ids = set()
        for course in current_user.courses:
            for cls in course.classes:
                teacher_class_ids.add(cls.id)
        
        if class_id_int not in teacher_class_ids:
            raise HTTPException(status_code=403, detail="无权向此班级导入学生")
    
    # 读取文件内容
    try:
        content = await file.read()
        # 尝试不同编码读取文件
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:  # 如果所有编码都尝试失败
            raise HTTPException(status_code=400, detail="文件编码错误")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"读取文件失败: {str(e)}")
    
    # 解析CSV数据
    reader = csv.reader(io.StringIO(text))
    
    # 处理每一行数据
    success_count = 0
    error_messages = []
    
    for i, row in enumerate(reader):
        if len(row) != 3:
            error_messages.append(f"第{i+1}行: 格式错误，应为'学号,密码,真实姓名'")
            continue
        
        username, password, real_name = row
        
        # 去除空白
        username = username.strip()
        password = password.strip()
        real_name = real_name.strip()
        
        if not username or not password or not real_name:
            error_messages.append(f"第{i+1}行: 学号、密码或姓名不能为空")
            continue
        
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            error_messages.append(f"第{i+1}行: 用户名'{username}'已存在")
            continue
        
        # 创建学生账号
        try:
            hashed_password = get_password_hash(password)
            new_student = User(
                username=username,
                password=hashed_password,
                real_name=real_name,
                role="student"
            )
            db.add(new_student)
            db.flush()
            
            # 添加班级关联
            new_student.classes.append(class_item)
            
            success_count += 1
        except Exception as e:
            error_messages.append(f"第{i+1}行: 创建失败")
    
    # 提交事务
    if success_count > 0:
        try:
            db.commit()
            
            # 记录操作日志
            now = datetime.now()
            log = OperationLog(
                user_id=current_user.id,
                operation="批量导入学生",
                target=class_item.name,
                created_at=now
            )
            db.add(log)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=500, detail="保存数据失败")
    else:
        db.rollback()
    
    return {
        "message": f"导入完成，成功导入{success_count}名学生",
        "success_count": success_count,
        "errors": error_messages
    }

@router.get("/export")
async def export_students(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """导出学生信息"""
    # 检查权限
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail="学生无权导出账号")
    
    # 构建查询条件
    query = db.query(User).filter(User.role == "student")
    
    # 根据班级筛选
    if class_id:
        # 检查班级是否存在
        class_item = db.query(Class).filter(Class.id == class_id).first()
        if not class_item:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        # 如果是教师，检查是否有权限操作该班级
        if current_user.role == "teacher":
            teacher_class_ids = set()
            for course in current_user.courses:
                for cls in course.classes:
                    teacher_class_ids.add(cls.id)
            
            if class_id not in teacher_class_ids:
                raise HTTPException(status_code=403, detail="无权导出此班级学生")
        
        query = query.join(student_class).filter(student_class.c.class_id == class_id)
    elif current_user.role == "teacher":
        # 教师只能导出自己班级的学生
        teacher_class_ids = set()
        for course in current_user.courses:
            for cls in course.classes:
                teacher_class_ids.add(cls.id)
        
        if teacher_class_ids:
            query = query.join(student_class).filter(student_class.c.class_id.in_(teacher_class_ids))
        else:
            return {"message": "无关联班级，无法导出学生"}
    
    # 查询学生
    students = query.all()
    
    # 创建CSV文件
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入标题行
    writer.writerow(["学号", "姓名", "班级"])
    
    # 写入学生数据
    for student in students:
        class_names = ", ".join([cls.name for cls in student.classes])
        writer.writerow([student.username, student.real_name, class_names])
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        operation="导出学生信息",
        target="学生列表"
    )
    db.add(log)
    db.commit()
    
    # 返回CSV文件
    output.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"students_{timestamp}.csv"
    
    return {
        "content": output.getvalue(),
        "filename": filename
    }

@router.delete("/clear")
async def clear_students(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """清空学生数据（仅限管理员）"""
    # 构建查询条件
    query = db.query(User).filter(User.role == "student")
    
    # 根据班级筛选
    if class_id:
        # 检查班级是否存在
        class_item = db.query(Class).filter(Class.id == class_id).first()
        if not class_item:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        query = query.join(student_class).filter(student_class.c.class_id == class_id)
    
    # 查询要删除的学生
    students = query.all()
    count = len(students)
    
    # 删除学生
    for student in students:
        db.delete(student)
    
    db.commit()
    
    # 记录操作日志
    target = f"所有学生" if not class_id else f"班级ID {class_id} 的学生"
    log = OperationLog(
        user_id=current_user.id,
        operation="清空学生数据",
        target=target
    )
    db.add(log)
    db.commit()
    
    return {"message": f"成功清空{count}名学生数据"} 