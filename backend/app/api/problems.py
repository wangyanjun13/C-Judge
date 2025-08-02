from fastapi import APIRouter, HTTPException, Response
from typing import List, Optional
from app.schemas.problem import ProblemCategory, ProblemInfo, ProblemDelete, ProblemDetail
from app.services.problem_service import ProblemService
from app.models import get_db, Problem
from sqlalchemy.orm import Session
from fastapi import Depends, Query
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
    tag_type_id: Optional[int] = Query(None, description="按标签类型ID过滤"),
    db: Session = Depends(get_db)
):
    """获取指定分类下的所有试题，可以按标签或标签类型过滤"""
    try:
        # 首先获取分类下的所有试题
        problems = ProblemService.get_problems_by_category(category_path)
        
        # 如果指定了标签ID，则过滤出包含该标签的试题
        if tag_id is not None:
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
    except FileNotFoundError as e:
        # 返回空列表而不是抛出异常
        logger.warning(f"题库分类不存在: {category_path}, 错误: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"读取试题列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取试题列表失败: {str(e)}")

@router.delete("/{problem_path:path}", response_model=ProblemDelete)
async def delete_problem(problem_path: str):
    """删除试题"""
    try:
        message = ProblemService.delete_problem(problem_path)
        return ProblemDelete(message=message)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除试题失败: {str(e)}")

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