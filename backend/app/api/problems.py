from fastapi import APIRouter, HTTPException, Response
from typing import List, Optional
from app.schemas.problem import ProblemCategory, ProblemInfo, ProblemDelete, ProblemDetail, CustomProblemCreate, CustomProblemResponse
from app.services.problem_service import ProblemService
from app.models import get_db, Problem
from sqlalchemy.orm import Session
from fastapi import Depends, Query
from app.utils.auth import get_teacher_user, get_admin_user
from app.models import User
import logging

# 创建路由
router = APIRouter(prefix="/problems", tags=["problems"])

logger = logging.getLogger(__name__)

@router.get("/categories", response_model=List[ProblemCategory])
async def get_problem_categories():
    """获取所有题库分类"""
    try:
        return ProblemService.get_problem_categories()
    except FileNotFoundError as e:
        # 返回空列表而不是抛出异常
        logger.warning(f"题库目录不存在: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"读取题库分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取题库分类失败: {str(e)}")

@router.get("/list/{category_path:path}", response_model=List[ProblemInfo])
async def get_problems_by_category(
    category_path: str,
    tag_id: Optional[int] = Query(None, description="按标签ID过滤"),
    tag_ids: Optional[str] = Query(None, description="按多个标签ID过滤（逗号分隔），取交集"),
    tag_type_id: Optional[int] = Query(None, description="按标签类型ID过滤"),
    db: Session = Depends(get_db)
):
    """获取指定分类下的所有试题，可以按标签或标签类型过滤"""
    try:
        # 首先获取分类下的所有试题
        problems = ProblemService.get_problems_by_category(category_path)
        
        # 解析tag_ids参数
        if tag_ids:
            try:
                parsed_tag_ids = [int(x.strip()) for x in tag_ids.split(',') if x.strip()]
                if parsed_tag_ids:
                    # 多标签交集过滤
                    problems = ProblemService.filter_problems_by_tags_intersection(db, problems, parsed_tag_ids)
            except ValueError:
                raise HTTPException(status_code=400, detail="tag_ids参数格式无效，应为逗号分隔的整数")
        # 如果指定了标签ID，则过滤出包含该标签的试题
        elif tag_id is not None:
            tag_problems = ProblemService.get_problems_by_tag(db, tag_id)
            # 获取数据路径列表，用于过滤
            tag_problem_paths = [p.data_path for p in tag_problems if p.data_path]
            # 过滤问题列表
            problems = [p for p in problems if p.data_path in tag_problem_paths]
        
        # 如果指定了标签类型ID，则过滤出包含该类型标签的试题
        elif tag_type_id is not None:
            type_problems = ProblemService.get_problems_by_tag_type(db, tag_type_id)
            # 获取数据路径列表，用于过滤
            type_problem_paths = [p.data_path for p in type_problems if p.data_path]
            # 过滤问题列表
            problems = [p for p in problems if p.data_path in type_problem_paths]
        
        return problems
    except Exception as e:
        logger.error(f"获取分类{category_path}下的试题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取试题失败: {str(e)}")

@router.put("/{problem_path:path}")
async def update_problem(problem_path: str, problem_data: dict, db: Session = Depends(get_db)):
    """更新试题信息"""
    try:
        # 这里添加更新试题的逻辑
        # 目前只是一个占位符
        return {"message": "试题更新成功", "problem_path": problem_path}
    except Exception as e:
        logger.error(f"更新试题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新试题失败: {str(e)}")

@router.delete("/{problem_path:path}")
async def delete_problem(problem_path: str, db: Session = Depends(get_db)):
    """删除试题"""
    try:
        # 这里需要实现删除试题的逻辑
        # 目前只是一个占位符
        return {"message": "试题删除成功", "problem_path": problem_path}
    except Exception as e:
        logger.error(f"删除试题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除试题失败: {str(e)}")

@router.get("/all-data")
async def get_all_problems_data(
    tag_id: Optional[int] = Query(None, description="按标签ID过滤"),
    tag_ids: Optional[str] = Query(None, description="按多个标签ID过滤（逗号分隔），取交集"),
    tag_type_id: Optional[int] = Query(None, description="按标签类型ID过滤"),
    include_tags: bool = Query(True, description="是否包含标签数据"),
    db: Session = Depends(get_db)
):
    """
    一次性获取所有题库数据（优化版本）
    包括分类、题目、标签类型、标签和题目标签关系
    """
    try:
        logger.info("开始获取所有题库数据（优化版本）")
        
        # 解析tag_ids参数
        parsed_tag_ids = None
        if tag_ids:
            try:
                parsed_tag_ids = [int(x.strip()) for x in tag_ids.split(',') if x.strip()]
            except ValueError:
                raise HTTPException(status_code=400, detail="tag_ids参数格式无效，应为逗号分隔的整数")
        
        # 获取所有数据
        all_data = ProblemService.get_all_problems_data(
            db=db,
            tag_id=tag_id,
            tag_ids=parsed_tag_ids,
            tag_type_id=tag_type_id,
            include_tags=include_tags
        )
        
        logger.info(f"获取所有数据完成: 分类={len(all_data['categories'])}, "
                   f"题目={len(all_data['problems'])}, "
                   f"标签类型={len(all_data['tag_types'])}, "
                   f"标签={len(all_data['tags'])}, "
                   f"题目标签关系={len(all_data['problem_tags'])}")
        
        return all_data
        
    except Exception as e:
        logger.error(f"获取所有题库数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取所有题库数据失败: {str(e)}")



@router.get("/html/{problem_path:path}")
async def get_problem_html_content(problem_path: str):
    """根据题目路径获取HTML内容"""
    try:
        html_content = ProblemService.get_problem_html_content(problem_path)
        return Response(content=html_content, media_type="text/html")
    except Exception as e:
        logger.error(f"获取题目HTML内容失败: {str(e)}")
        return Response(content="<p>题目内容加载失败</p>", media_type="text/html")

@router.get("/{problem_id}", response_model=ProblemDetail)
async def get_problem_detail(
    problem_id: int, 
    db: Session = Depends(get_db)
):
    """获取题目详情，包括HTML内容"""
    try:
        problem_detail = ProblemService.get_problem_detail(db, problem_id)
        if not problem_detail:
            raise HTTPException(status_code=404, detail=f"题目不存在: ID {problem_id}")
        return problem_detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取题目详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取题目详情失败: {str(e)}") 

@router.post("/custom", response_model=CustomProblemResponse)
async def create_custom_problem(
    problem_data: CustomProblemCreate,
    current_user: User = Depends(get_teacher_user)  # 需要教师或管理员权限
):
    """
    创建自定义题目
    
    Args:
        problem_data: 题目创建数据
        current_user: 当前用户（需要教师或管理员权限）
        
    Returns:
        创建结果
    """
    try:
        logger.info(f"用户 {current_user.username} 开始创建自定义题目: {problem_data.name}")
        
        # 调用服务层创建题目
        result = ProblemService.create_custom_problem(problem_data)
        
        if result.success:
            logger.info(f"用户 {current_user.username} 创建自定义题目成功: {result.problem_path}")
        else:
            logger.warning(f"用户 {current_user.username} 创建自定义题目失败: {result.message}")
        
        return result
        
    except Exception as e:
        logger.error(f"创建自定义题目API失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建题目失败: {str(e)}") 