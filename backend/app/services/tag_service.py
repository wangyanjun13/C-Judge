from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models import Tag, TagType, Problem
from app.schemas.tag import TagCreate, TagUpdate, TagTypeCreate, TagTypeUpdate
import logging

# 配置日志
logger = logging.getLogger(__name__)

class TagService:
    @staticmethod
    def get_tag_types(db: Session) -> List[TagType]:
        """获取所有标签类型"""
        return db.query(TagType).all()
    
    @staticmethod
    def create_tag_type(db: Session, tag_type: TagTypeCreate) -> TagType:
        """创建标签类型"""
        db_tag_type = TagType(name=tag_type.name)
        db.add(db_tag_type)
        db.commit()
        db.refresh(db_tag_type)
        return db_tag_type
    
    @staticmethod
    def get_tag_type(db: Session, tag_type_id: int) -> Optional[TagType]:
        """获取标签类型"""
        return db.query(TagType).filter(TagType.id == tag_type_id).first()
    
    @staticmethod
    def update_tag_type(db: Session, tag_type_id: int, tag_type: TagTypeUpdate) -> Optional[TagType]:
        """更新标签类型"""
        db_tag_type = db.query(TagType).filter(TagType.id == tag_type_id).first()
        if not db_tag_type:
            return None
        
        for key, value in tag_type.dict(exclude_unset=True).items():
            setattr(db_tag_type, key, value)
        
        db.commit()
        db.refresh(db_tag_type)
        return db_tag_type
    
    @staticmethod
    def delete_tag_type(db: Session, tag_type_id: int) -> bool:
        """删除标签类型"""
        db_tag_type = db.query(TagType).filter(TagType.id == tag_type_id).first()
        if not db_tag_type:
            return False
        
        db.delete(db_tag_type)
        db.commit()
        return True
    
    @staticmethod
    def get_tags(db: Session, tag_type_id: Optional[int] = None) -> List[Tag]:
        """获取所有标签，可以按标签类型过滤"""
        query = db.query(Tag)
        if tag_type_id:
            query = query.filter(Tag.tag_type_id == tag_type_id)
        return query.all()
    
    @staticmethod
    def create_tag(db: Session, tag: TagCreate) -> Tag:
        """创建标签"""
        db_tag = Tag(name=tag.name, tag_type_id=tag.tag_type_id)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag
    
    @staticmethod
    def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
        """获取标签"""
        return db.query(Tag).filter(Tag.id == tag_id).first()
    
    @staticmethod
    def update_tag(db: Session, tag_id: int, tag: TagUpdate) -> Optional[Tag]:
        """更新标签"""
        db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not db_tag:
            return None
        
        for key, value in tag.dict(exclude_unset=True).items():
            setattr(db_tag, key, value)
        
        db.commit()
        db.refresh(db_tag)
        return db_tag
    
    @staticmethod
    def delete_tag(db: Session, tag_id: int) -> bool:
        """删除标签"""
        db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not db_tag:
            return False
        
        db.delete(db_tag)
        db.commit()
        return True
    
    @staticmethod
    def get_problem_by_path(db: Session, problem_path: str) -> Optional[Problem]:
        """通过data_path获取问题"""
        # 尝试使用原始路径和URL解码后的路径
        from urllib.parse import unquote
        
        # 尝试直接匹配
        problem = db.query(Problem).filter(Problem.data_path == problem_path).first()
        if problem:
            return problem
            
        # 尝试URL解码后再查询
        decoded_path = unquote(problem_path)
        if decoded_path != problem_path:
            problem = db.query(Problem).filter(Problem.data_path == decoded_path).first()
            if problem:
                return problem
        
        # 避免进行昂贵的模糊匹配，除非绝对必要
        # 如果路径中包含'/'，可能是完整路径，尝试使用最后一部分进行匹配
        if '/' in decoded_path:
            # 尝试使用路径的最后一部分进行匹配
            last_part = decoded_path.split('/')[-1]
            if last_part:
                # 使用精确匹配最后部分，而不是模糊匹配
                problems = db.query(Problem).filter(Problem.data_path.endswith(last_part)).limit(5).all()
                for p in problems:
                    if p.data_path and (decoded_path.endswith(p.data_path) or p.data_path.endswith(decoded_path)):
                        return p
        
        return None
    
    @staticmethod
    def get_problem_tags(db: Session, problem_id_or_path: str) -> List[Tag]:
        """获取问题的标签，支持通过ID或data_path查找"""
        try:
            # 尝试将参数解析为整数ID
            problem_id = int(problem_id_or_path)
            problem = db.query(Problem).filter(Problem.id == problem_id).first()
        except ValueError:
            # 如果不是整数，则视为data_path
            problem = TagService.get_problem_by_path(db, problem_id_or_path)
        
        if not problem:
            return []
        return problem.tags
    
    @staticmethod
    def add_tag_to_problem(db: Session, problem_id_or_path: str, tag_id: int) -> bool:
        """为问题添加标签，支持通过ID或data_path查找"""
        try:
            # 尝试将参数解析为整数ID
            problem_id = int(problem_id_or_path)
            problem = db.query(Problem).filter(Problem.id == problem_id).first()
        except ValueError:
            # 如果不是整数，则视为data_path
            problem = TagService.get_problem_by_path(db, problem_id_or_path)
        
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        
        if not problem or not tag:
            return False
        
        if tag not in problem.tags:
            problem.tags.append(tag)
            db.commit()
        
        return True
    
    @staticmethod
    def remove_tag_from_problem(db: Session, problem_id_or_path: str, tag_id: int) -> bool:
        """从问题中移除标签，支持通过ID或data_path查找"""
        try:
            # 尝试将参数解析为整数ID
            problem_id = int(problem_id_or_path)
            problem = db.query(Problem).filter(Problem.id == problem_id).first()
        except ValueError:
            # 如果不是整数，则视为data_path
            problem = TagService.get_problem_by_path(db, problem_id_or_path)
        
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        
        if not problem or not tag:
            return False
        
        if tag in problem.tags:
            problem.tags.remove(tag)
            db.commit()
        
        return True
    
    @staticmethod
    def set_problem_tags(db: Session, problem_id_or_path: str, tag_ids: List[int]) -> bool:
        """设置问题的标签，支持通过ID或data_path查找"""
        try:
            # 尝试将参数解析为整数ID
            problem_id = int(problem_id_or_path)
            problem = db.query(Problem).filter(Problem.id == problem_id).first()
        except ValueError:
            # 如果不是整数，则视为data_path
            problem = TagService.get_problem_by_path(db, problem_id_or_path)
        
        if not problem:
            return False
        
        # 清除所有标签
        problem.tags = []
        
        # 添加新标签
        for tag_id in tag_ids:
            tag = db.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                problem.tags.append(tag)
        
        db.commit()
        return True
    
    @staticmethod
    def get_problems_by_tag(db: Session, tag_id: int) -> List[Problem]:
        """获取具有特定标签的所有问题"""
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return []
        
        return tag.problems

    @staticmethod
    def get_problems_batch_tags(db: Session, problem_paths: List[str]) -> Dict[str, List[Tag]]:
        """批量获取多个问题的标签，优化数据库查询"""
        if not problem_paths:
            return {}
        
        result = {}
        
        # 创建一个集合来存储已处理的路径，避免重复处理
        unique_paths = set(problem_paths)
        
        # 首先尝试直接匹配所有路径
        problems = db.query(Problem).filter(Problem.data_path.in_(unique_paths)).all()
        
        # 创建路径到问题的映射
        path_to_problem = {p.data_path: p for p in problems if p.data_path}
        
        # 处理已找到的问题
        for path in problem_paths:
            if path in path_to_problem:
                result[path] = path_to_problem[path].tags
        
        # 处理未找到的路径
        missing_paths = [p for p in unique_paths if p not in path_to_problem]
        
        if missing_paths:
            # 对于未找到的路径，尝试URL解码后再查询
            from urllib.parse import unquote
            
            for path in missing_paths:
                decoded_path = unquote(path)
                if decoded_path != path:
                    # 尝试使用解码后的路径查询
                    problem = db.query(Problem).filter(Problem.data_path == decoded_path).first()
                    if problem:
                        result[path] = problem.tags
                        continue
                
                # 如果仍未找到，尝试最后的模糊匹配
                if '/' in decoded_path:
                    last_part = decoded_path.split('/')[-1]
                    if last_part:
                        problem = TagService.get_problem_by_path(db, path)
                        if problem:
                            result[path] = problem.tags
                            continue
                
                # 如果所有尝试都失败，设置为空列表
                result[path] = []
        
        return result
