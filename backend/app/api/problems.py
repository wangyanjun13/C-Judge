from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.problem import ProblemCategory, ProblemInfo, ProblemDelete, ProblemDetail
from app.services.problem_service import ProblemService
from app.models import get_db, Problem
from sqlalchemy.orm import Session
from fastapi import Depends
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
async def get_problems_by_category(category_path: str):
    """获取指定分类下的所有试题"""
    try:
        return ProblemService.get_problems_by_category(category_path)
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