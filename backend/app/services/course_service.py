from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import User, Course, Class, OperationLog

class CourseService:
    """课程服务类"""
    
    @staticmethod
    def get_courses(db: Session, user_id: int) -> List[Course]:
        """获取课程列表"""
        # 获取用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # 根据用户角色返回不同范围的课程
        if user.role == "admin":
            # 管理员可以查看所有课程
            courses = db.query(Course).all()
        elif user.role == "teacher":
            # 教师只能查看自己的课程
            courses = user.courses
        else:
            # 学生只能查看自己班级关联的课程
            student_class_ids = [cls.id for cls in user.classes]
            courses = []
            if student_class_ids:
                courses = db.query(Course).filter(
                    Course.classes.any(Class.id.in_(student_class_ids))
                ).all()
        
        return courses
    
    @staticmethod
    def create_course(db: Session, name: str, teacher_id: int, category: Optional[str], class_ids: List[int]) -> Optional[Course]:
        """创建课程"""
        # 检查班级是否存在
        class_items = []
        for class_id in class_ids:
            class_item = db.query(Class).filter(Class.id == class_id).first()
            if not class_item:
                return None
            class_items.append(class_item)
        
        # 创建课程
        new_course = Course(
            name=name,
            teacher_id=teacher_id,
            category=category
        )
        db.add(new_course)
        db.flush()  # 分配ID但不提交事务
        
        # 添加班级关联
        for class_item in class_items:
            new_course.classes.append(class_item)
        
        db.commit()
        db.refresh(new_course)
        
        return new_course
    
    @staticmethod
    def update_course(db: Session, course_id: int, update_data: dict) -> Optional[Course]:
        """更新课程"""
        # 查询课程
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None
        
        # 更新课程信息
        if 'name' in update_data and update_data['name']:
            course.name = update_data['name']
        
        if 'category' in update_data:
            course.category = update_data['category']
        
        # 如果提供了教师ID，更新教师
        if 'teacher_id' in update_data and update_data['teacher_id']:
            teacher = db.query(User).filter(
                User.id == update_data['teacher_id'],
                User.role == "teacher"
            ).first()
            if not teacher:
                return None
            course.teacher_id = update_data['teacher_id']
        
        # 如果提供了班级ID列表，更新班级关联
        if 'class_ids' in update_data and update_data['class_ids'] is not None:
            # 检查班级是否存在
            class_items = []
            for class_id in update_data['class_ids']:
                class_item = db.query(Class).filter(Class.id == class_id).first()
                if not class_item:
                    return None
                class_items.append(class_item)
            
            # 清除现有班级关联
            course.classes = []
            
            # 添加新班级关联
            for class_item in class_items:
                course.classes.append(class_item)
        
        db.commit()
        db.refresh(course)
        
        return course
    
    @staticmethod
    def delete_course(db: Session, course_id: int) -> bool:
        """删除课程"""
        # 查询课程
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return False
        
        # 检查课程是否有关联的练习
        if course.exercises:
            return False
        
        # 删除课程（会自动清除课程-班级关联）
        db.delete(course)
        db.commit()
        
        return True
    
    @staticmethod
    def check_teacher_permission(db: Session, teacher_id: int, course_id: int) -> bool:
        """检查教师是否有权限管理课程"""
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return False
        
        return course.teacher_id == teacher_id
    
    @staticmethod
    def log_operation(db: Session, user_id: int, operation: str, target: str) -> None:
        """记录操作日志"""
        log = OperationLog(
            user_id=user_id,
            operation=operation,
            target=target,
            created_at=datetime.now()  # 明确设置当前时间
        )
        db.add(log)
        db.commit() 