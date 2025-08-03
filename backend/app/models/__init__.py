from app.models.database import Base, get_db
from app.models.user import User
from app.models.class_model import Class, class_course, student_class, teacher_class
from app.models.course import Course
from app.models.exercise import Exercise
from app.models.tag import TagType, Tag, TagApprovalRequest, problem_tag
from app.models.problem import Problem, ProblemCategory
from app.models.submission import Submission
from app.models.operation_log import OperationLog
from app.models.system_setting import SystemSetting

# 导出所有模型
__all__ = [
    "Base", "get_db",
    "User",
    "Class", "class_course", "student_class", "teacher_class",
    "Course",
    "Exercise",
    "TagType", "Tag", "TagApprovalRequest", "problem_tag",
    "Problem", "ProblemCategory",
    "Submission",
    "OperationLog",
    "SystemSetting"
] 