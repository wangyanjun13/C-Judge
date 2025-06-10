from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import User, Class, OperationLog

class ClassService:
    """班级服务类"""
    
    @staticmethod
    def get_classes(db: Session, user_id: int) -> List[dict]:
        """获取班级列表"""
        # 获取用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # 根据用户角色返回不同范围的班级
        if user.role == "admin":
            # 管理员可以查看所有班级
            classes = db.query(Class).all()
        elif user.role == "teacher":
            # 教师只能查看与其课程关联的班级
            teacher_courses = user.courses
            class_ids = set()
            for course in teacher_courses:
                for class_item in course.classes:
                    class_ids.add(class_item.id)
            
            classes = db.query(Class).filter(Class.id.in_(class_ids)).all() if class_ids else []
        else:
            # 学生只能查看自己所在的班级
            classes = user.classes
        
        # 处理返回数据，添加学生数量
        result = []
        for class_item in classes:
            student_count = len(class_item.students)
            class_dict = {
                "id": class_item.id,
                "name": class_item.name,
                "created_at": class_item.created_at,
                "student_count": student_count
            }
            result.append(class_dict)
        
        return result
    
    @staticmethod
    def create_class(db: Session, name: str) -> Class:
        """创建班级"""
        # 创建班级
        new_class = Class(name=name)
        db.add(new_class)
        db.commit()
        db.refresh(new_class)
        
        return new_class
    
    @staticmethod
    def update_class(db: Session, class_id: int, name: str) -> Optional[Class]:
        """更新班级"""
        # 查询班级
        class_item = db.query(Class).filter(Class.id == class_id).first()
        if not class_item:
            return None
        
        # 更新班级
        class_item.name = name
        db.commit()
        db.refresh(class_item)
        
        return class_item
    
    @staticmethod
    def delete_class(db: Session, class_id: int) -> bool:
        """删除班级"""
        # 查询班级
        class_item = db.query(Class).filter(Class.id == class_id).first()
        if not class_item:
            return False
        
        # 检查是否有学生在该班级
        if class_item.students:
            return False
        
        # 检查是否有课程关联该班级
        if class_item.courses:
            return False
        
        # 删除班级
        db.delete(class_item)
        db.commit()
        
        return True
    
    @staticmethod
    def check_class_name_exists(db: Session, name: str, exclude_id: Optional[int] = None) -> bool:
        """检查班级名称是否已存在"""
        query = db.query(Class).filter(Class.name == name)
        if exclude_id:
            query = query.filter(Class.id != exclude_id)
        
        return query.first() is not None
    
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