from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import csv
import io
from datetime import datetime

from app.models import User, Class, get_db, OperationLog, student_class
from app.utils.auth import get_password_hash

class UserService:
    """用户服务类"""
    
    @staticmethod
    def get_teachers(db: Session) -> List[User]:
        """获取教师列表"""
        return db.query(User).filter(User.role == "teacher").all()
    
    @staticmethod
    def get_students(db: Session, user_id: int, class_id: Optional[int] = None) -> List[User]:
        """获取学生列表"""
        # 获取用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # 构建查询条件
        query = db.query(User).filter(User.role == "student")
        
        # 根据用户角色和班级筛选学生
        if user.role == "admin":
            # 管理员可以查看所有学生，如果指定了班级则筛选
            if class_id:
                query = query.join(student_class).filter(student_class.c.class_id == class_id)
        elif user.role == "teacher":
            # 教师只能查看其课程关联班级的学生
            teacher_courses = user.courses
            class_ids = set()
            for course in teacher_courses:
                for class_item in course.classes:
                    class_ids.add(class_item.id)
            
            # 如果指定了班级，检查教师是否有权限查看该班级
            if class_id:
                if class_id not in class_ids:
                    return []
                query = query.join(student_class).filter(student_class.c.class_id == class_id)
            elif class_ids:
                # 查看所有自己有权限的班级的学生
                query = query.join(student_class).filter(student_class.c.class_id.in_(class_ids))
            else:
                return []
        else:
            # 学生只能查看自己所在班级的其他学生
            student_class_ids = [cls.id for cls in user.classes]
            if class_id:
                if class_id not in student_class_ids:
                    return []
                query = query.join(student_class).filter(student_class.c.class_id == class_id)
            elif student_class_ids:
                query = query.join(student_class).filter(student_class.c.class_id.in_(student_class_ids))
            else:
                return []
        
        # 查询学生
        return query.all()
    
    @staticmethod
    def create_teacher(db: Session, username: str, password: str, real_name: str) -> Optional[User]:
        """创建教师账号"""
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return None
        
        # 创建教师账号
        hashed_password = get_password_hash(password)
        new_teacher = User(
            username=username,
            password=hashed_password,
            real_name=real_name,
            role="teacher"
        )
        db.add(new_teacher)
        db.commit()
        db.refresh(new_teacher)
        
        return new_teacher
    
    @staticmethod
    def create_student(db: Session, username: str, password: str, real_name: str, class_ids: List[int]) -> Optional[User]:
        """创建学生账号"""
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return None
        
        # 检查班级是否存在
        class_items = []
        for class_id in class_ids:
            class_item = db.query(Class).filter(Class.id == class_id).first()
            if not class_item:
                return None
            class_items.append(class_item)
        
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
        for class_item in class_items:
            new_student.classes.append(class_item)
        
        db.commit()
        db.refresh(new_student)
        
        return new_student
    
    @staticmethod
    def update_teacher(db: Session, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """更新教师信息"""
        # 查询教师
        teacher = db.query(User).filter(User.id == user_id, User.role == "teacher").first()
        if not teacher:
            return None
        
        # 更新教师信息
        if 'real_name' in update_data and update_data['real_name']:
            teacher.real_name = update_data['real_name']
        
        if 'password' in update_data and update_data['password']:
            teacher.password = get_password_hash(update_data['password'])
        
        db.commit()
        db.refresh(teacher)
        
        return teacher
    
    @staticmethod
    def update_student(db: Session, user_id: int, update_data: Dict[str, Any], class_ids: Optional[List[int]] = None) -> Optional[User]:
        """更新学生信息"""
        # 查询学生
        student = db.query(User).filter(User.id == user_id, User.role == "student").first()
        if not student:
            return None
        
        # 更新学生信息
        if 'real_name' in update_data and update_data['real_name']:
            student.real_name = update_data['real_name']
        
        if 'password' in update_data and update_data['password']:
            student.password = get_password_hash(update_data['password'])
        
        # 如果提供了班级ID，更新学生班级
        if class_ids is not None:
            # 检查班级是否存在
            class_items = []
            for class_id in class_ids:
                class_item = db.query(Class).filter(Class.id == class_id).first()
                if not class_item:
                    return None
                class_items.append(class_item)
            
            # 清除现有班级关联
            student.classes = []
            
            # 添加新班级关联
            for class_item in class_items:
                student.classes.append(class_item)
        
        db.commit()
        db.refresh(student)
        
        return student
    
    @staticmethod
    def delete_teacher(db: Session, user_id: int) -> bool:
        """删除教师账号"""
        # 查询教师
        teacher = db.query(User).filter(User.id == user_id, User.role == "teacher").first()
        if not teacher:
            return False
        
        # 检查是否有课程关联该教师
        if teacher.courses:
            return False
        
        # 删除教师
        db.delete(teacher)
        db.commit()
        
        return True
    
    @staticmethod
    def delete_student(db: Session, user_id: int) -> bool:
        """删除学生账号"""
        # 查询学生
        student = db.query(User).filter(User.id == user_id, User.role == "student").first()
        if not student:
            return False
        
        # 删除学生
        db.delete(student)
        db.commit()
        
        return True
    
    @staticmethod
    def import_students(db: Session, file_content: str, class_id: int) -> Dict[str, Any]:
        """批量导入学生"""
        # 检查班级是否存在
        class_item = db.query(Class).filter(Class.id == class_id).first()
        if not class_item:
            return {"success": False, "message": "班级不存在"}
        
        # 解析CSV数据
        reader = csv.reader(io.StringIO(file_content))
        
        # 处理每一行数据
        success_count = 0
        error_messages = []
        
        for i, row in enumerate(reader):
            if len(row) != 3:
                error_messages.append(f"第{i+1}行: 格式错误，应为'学号,密码,真实姓名'")
                continue
            
            username, password, real_name = row
            
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
                db.flush()  # 分配ID但不提交事务
                
                # 添加班级关联
                new_student.classes.append(class_item)
                
                success_count += 1
            except Exception as e:
                error_messages.append(f"第{i+1}行: 创建失败，错误: {str(e)}")
        
        # 提交事务
        db.commit()
        
        return {
            "success": True,
            "message": f"导入完成，成功导入{success_count}名学生",
            "success_count": success_count,
            "errors": error_messages
        }
    
    @staticmethod
    def export_students(db: Session, user_id: int, class_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """导出学生信息"""
        # 获取用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # 构建查询条件
        query = db.query(User).filter(User.role == "student")
        
        # 根据班级筛选
        if class_id:
            # 检查班级是否存在
            class_item = db.query(Class).filter(Class.id == class_id).first()
            if not class_item:
                return None
            
            # 如果是教师，检查是否有权限操作该班级
            if user.role == "teacher":
                teacher_class_ids = set()
                for course in user.courses:
                    for cls in course.classes:
                        teacher_class_ids.add(cls.id)
                
                if class_id not in teacher_class_ids:
                    return None
            
            query = query.join(student_class).filter(student_class.c.class_id == class_id)
        elif user.role == "teacher":
            # 教师只能导出自己班级的学生
            teacher_class_ids = set()
            for course in user.courses:
                for cls in course.classes:
                    teacher_class_ids.add(cls.id)
            
            if teacher_class_ids:
                query = query.join(student_class).filter(student_class.c.class_id.in_(teacher_class_ids))
            else:
                return None
        
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
        
        # 返回CSV文件内容
        output.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"students_{timestamp}.csv"
        
        return {
            "content": output.getvalue(),
            "filename": filename
        }
    
    @staticmethod
    def clear_students(db: Session, class_id: Optional[int] = None) -> int:
        """清空学生数据"""
        # 构建查询条件
        query = db.query(User).filter(User.role == "student")
        
        # 根据班级筛选
        if class_id:
            # 检查班级是否存在
            class_item = db.query(Class).filter(Class.id == class_id).first()
            if not class_item:
                return 0
            
            query = query.join(student_class).filter(student_class.c.class_id == class_id)
        
        # 查询要删除的学生
        students = query.all()
        count = len(students)
        
        # 删除学生
        for student in students:
            db.delete(student)
        
        db.commit()
        
        return count
    
    @staticmethod
    def check_username_exists(db: Session, username: str) -> bool:
        """检查用户名是否已存在"""
        return db.query(User).filter(User.username == username).first() is not None
    
    @staticmethod
    def check_teacher_class_permission(db: Session, teacher_id: int, class_id: int) -> bool:
        """检查教师是否有权限操作班级"""
        teacher = db.query(User).filter(User.id == teacher_id, User.role == "teacher").first()
        if not teacher:
            return False
        
        teacher_class_ids = set()
        for course in teacher.courses:
            for cls in course.classes:
                teacher_class_ids.add(cls.id)
        
        return class_id in teacher_class_ids
    
    @staticmethod
    def log_operation(db: Session, user_id: int, operation: str, target: str) -> None:
        """记录操作日志"""
        log = OperationLog(
            user_id=user_id,
            operation=operation,
            target=target
        )
        db.add(log)
        db.commit() 