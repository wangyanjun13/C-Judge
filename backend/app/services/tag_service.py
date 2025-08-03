from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.models import Tag, TagType, Problem, TagApprovalRequest, User
from app.schemas.tag import TagCreate, TagUpdate, TagTypeCreate, TagTypeUpdate, TagApprovalRequestCreate, TagApprovalRequestUpdate
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
        logger.info(f"查找问题路径: {problem_path}")
        
        # 尝试使用原始路径和URL解码后的路径
        from urllib.parse import unquote
        
        # 尝试直接匹配
        problem = db.query(Problem).filter(Problem.data_path == problem_path).first()
        if problem:
            logger.info(f"直接匹配成功: {problem_path}")
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
        
        logger.warning(f"问题路径未找到: {problem_path}")
        return None
    
    @staticmethod
    def _create_problem_from_filesystem(db: Session, problem_path: str) -> Optional[Problem]:
        """从文件系统创建题目记录"""
        import os
        from urllib.parse import unquote
        from app.services.problem_service import ProblemService
        
        # 解码路径
        decoded_path = unquote(problem_path)
        logger.info(f"创建题目记录，解码后路径: {decoded_path}")
        
        # 题库根目录
        PROBLEMS_ROOT = "/app_root/题库"
        
        # 构建完整路径
        full_path = os.path.join(PROBLEMS_ROOT, decoded_path)
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            logger.warning(f"题目目录不存在: {full_path}")
            return None
        
        # 查找Question.INF文件
        inf_path = os.path.join(full_path, "Question.INF")
        if not os.path.exists(inf_path):
            logger.warning(f"Question.INF文件不存在: {inf_path}")
            # 使用目录名作为题目名称
            problem_name = os.path.basename(decoded_path)
            chinese_name = problem_name
            time_limit = 1000
            memory_limit = 134217728  # 128MB in bytes
        else:
            # 解析Question.INF文件
            try:
                problem_info = ProblemService.parse_question_inf(
                    inf_path, 
                    os.path.basename(decoded_path),
                    os.path.dirname(decoded_path)
                )
                if not problem_info:
                    logger.warning(f"无法解析Question.INF文件: {inf_path}")
                    return None
                
                problem_name = problem_info.name
                chinese_name = problem_info.chinese_name
                
                # 解析时间限制（从"1000ms"中提取数字）
                time_limit_str = problem_info.time_limit or "1000ms"
                import re
                time_match = re.search(r'(\d+)', time_limit_str)
                time_limit = int(time_match.group(1)) if time_match else 1000
                
                # 解析内存限制（从"256M"中提取数字，转换为字节）
                memory_limit_str = problem_info.memory_limit or "256M"
                memory_match = re.search(r'(\d+)', memory_limit_str)
                memory_mb = int(memory_match.group(1)) if memory_match else 256
                memory_limit = memory_mb * 1024 * 1024  # 转换为字节
                
            except Exception as e:
                logger.error(f"解析Question.INF文件失败: {e}")
                return None
        
        # 创建题目记录
        try:
            new_problem = Problem(
                name=problem_name,
                chinese_name=chinese_name,
                time_limit=time_limit,
                memory_limit=memory_limit,
                data_path=decoded_path,
                category=os.path.dirname(decoded_path) if '/' in decoded_path else '',
                is_shared=True,
                owner_id=None  # 系统自动创建的题目没有所有者
            )
            
            db.add(new_problem)
            db.flush()  # 获取ID但不提交事务
            
            logger.info(f"成功创建题目记录: {new_problem.name} (ID: {new_problem.id})")
            return new_problem
            
        except Exception as e:
            logger.error(f"创建题目记录失败: {e}")
            db.rollback()
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
        logger.info(f"设置问题标签: problem_path={problem_id_or_path}, tag_ids={tag_ids}")
        
        try:
            # 尝试将参数解析为整数ID
            problem_id = int(problem_id_or_path)
            problem = db.query(Problem).filter(Problem.id == problem_id).first()
            logger.info(f"通过ID查找问题: {problem_id}, 找到: {problem is not None}")
        except ValueError:
            # 如果不是整数，则视为data_path
            logger.info(f"通过路径查找问题: {problem_id_or_path}")
            problem = TagService.get_problem_by_path(db, problem_id_or_path)
            logger.info(f"通过路径查找结果: {problem is not None}")
            
            # 如果数据库中不存在，尝试从文件系统创建
            if not problem:
                logger.info(f"数据库中不存在，尝试从文件系统创建题目记录: {problem_id_or_path}")
                problem = TagService._create_problem_from_filesystem(db, problem_id_or_path)
        
        if not problem:
            logger.error(f"问题未找到且无法创建: {problem_id_or_path}")
            return False
        
        # 清除所有标签
        problem.tags = []
        
        # 添加新标签
        for tag_id in tag_ids:
            tag = db.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                problem.tags.append(tag)
        
        db.commit()
        logger.info(f"成功为题目 {problem.name} 设置了 {len(tag_ids)} 个标签")
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
    
    # 标签审核请求相关方法
    @staticmethod
    def create_tag_approval_request(db: Session, request_data: TagApprovalRequestCreate, user_id: int) -> TagApprovalRequest:
        """创建标签审核请求"""
        # 检查是否已有该问题的待审核请求
        existing_request = db.query(TagApprovalRequest).filter(
            and_(
                TagApprovalRequest.problem_data_path == request_data.problem_data_path,
                TagApprovalRequest.status == 'pending'
            )
        ).first()
        
        if existing_request:
            # 更新现有请求
            existing_request.tag_ids = request_data.tag_ids
            existing_request.request_message = request_data.request_message
            existing_request.created_at = datetime.now()
            db.commit()
            db.refresh(existing_request)
            
            return existing_request
        
        # 创建新请求
        db_request = TagApprovalRequest(
            problem_data_path=request_data.problem_data_path,
            requestor_id=user_id,
            tag_ids=request_data.tag_ids,
            request_message=request_data.request_message
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        
        return db_request
    
    @staticmethod
    def get_approval_requests(db: Session, status: Optional[str] = None) -> List[TagApprovalRequest]:
        """获取审核请求列表"""
        query = db.query(TagApprovalRequest)
        if status:
            query = query.filter(TagApprovalRequest.status == status)
        
        requests = query.order_by(TagApprovalRequest.created_at.desc()).all()
        return requests
    
    @staticmethod
    def approve_tag_request(db: Session, request_id: int, reviewer_id: int, 
                           update_data: TagApprovalRequestUpdate) -> Optional[TagApprovalRequest]:
        """审核标签请求"""
        request = db.query(TagApprovalRequest).filter(TagApprovalRequest.id == request_id).first()
        if not request:
            return None
        
        # 更新审核状态
        request.status = update_data.status
        request.review_message = update_data.review_message
        request.reviewer_id = reviewer_id
        request.reviewed_at = datetime.now()
        
        # 先提交审核状态
        db.commit()
        db.refresh(request)
        
        # 如果批准，尝试应用标签到问题
        if update_data.status == 'approved':
            logger.info(f"开始应用标签到问题: {request.problem_data_path}, 标签IDs: {request.tag_ids}")
            try:
                success = TagService.set_problem_tags(db, request.problem_data_path, request.tag_ids)
                if not success:
                    logger.error(f"应用标签失败: 问题路径={request.problem_data_path}, 标签IDs={request.tag_ids}")
                    # 更新审核状态为失败，但不返回None
                    request.review_message = f"审核通过，但应用标签失败。原因：未找到对应问题。{update_data.review_message or ''}"
                    db.commit()
                    db.refresh(request)
                else:
                    logger.info(f"标签应用成功: {request.problem_data_path}")
            except Exception as e:
                logger.error(f"应用标签时发生异常: {str(e)}")
                request.review_message = f"审核通过，但应用标签时发生错误：{str(e)}。{update_data.review_message or ''}"
                db.commit()
                db.refresh(request)
        
        return request
    
    @staticmethod
    def get_user_approval_requests(db: Session, user_id: int) -> List[TagApprovalRequest]:
        """获取用户的审核请求历史"""
        requests = db.query(TagApprovalRequest).filter(
            TagApprovalRequest.requestor_id == user_id
        ).order_by(TagApprovalRequest.created_at.desc()).all()
        return requests
