import os
import shutil
import logging
from typing import List, Optional, Dict, Any
from app.schemas.problem import ProblemCategory, ProblemInfo, ProblemDetail
from sqlalchemy.orm import Session
from app.models import Problem, Tag, TagType

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 题库根目录 - 只使用项目根目录下的题库路径
PROBLEMS_ROOT = "/app_root/题库"  # Docker挂载的项目根目录下的题库

logger.info(f"题库根目录: {PROBLEMS_ROOT}")

class ProblemService:
    @staticmethod
    def get_problem_categories() -> List[ProblemCategory]:
        """获取所有题库分类"""
        categories = []
        
        # 确保题库目录存在，但不创建
        if not os.path.exists(PROBLEMS_ROOT):
            logger.error(f"题库目录不存在: {PROBLEMS_ROOT}")
            return categories
        
        # 递归查找所有包含试题的目录
        ProblemService._find_categories(PROBLEMS_ROOT, "", categories)
        
        return categories
    
    @staticmethod
    def _find_categories(current_path: str, relative_path: str, categories: List[ProblemCategory]) -> None:
        """递归查找所有题库分类"""
        # 检查当前目录是否包含试题
        has_problems = False
        for item in os.listdir(current_path):
            item_path = os.path.join(current_path, item)
            if os.path.isdir(item_path):
                inf_path = os.path.join(item_path, "Question.INF")
                if os.path.exists(inf_path):
                    has_problems = True
                    break
        
        # 如果当前目录包含试题，将其添加为一个分类
        if has_problems:
            # 处理分类名称，过滤掉"题库X.X"这样的最高层目录
            path_parts = relative_path.split(os.sep)
            if path_parts and path_parts[0].startswith("题库"):
                # 如果第一部分是"题库X.X"，则从第二部分开始显示
                if len(path_parts) > 1:
                    category_name = os.sep.join(path_parts[1:])
                else:
                    category_name = relative_path
            else:
                category_name = relative_path
            
            logger.info(f"添加题库分类: {category_name}, 路径: {relative_path}")
            categories.append(ProblemCategory(
                name=category_name,
                path=relative_path
            ))
        else:
            # 如果当前目录不包含试题，继续递归查找子目录
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    new_relative_path = os.path.join(relative_path, item) if relative_path else item
                    ProblemService._find_categories(item_path, new_relative_path, categories)
    
    @staticmethod
    def get_problems_by_category(category_path: str) -> List[ProblemInfo]:
        """获取指定分类下的所有试题"""
        problems = []
        full_path = os.path.join(PROBLEMS_ROOT, category_path)
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            logger.error(f"题库分类不存在: {full_path}")
            return problems
        
        # 遍历分类目录下的所有试题文件夹
        for problem_dir in os.listdir(full_path):
            problem_path = os.path.join(full_path, problem_dir)
            if os.path.isdir(problem_path):
                # 读取Question.INF文件
                inf_path = os.path.join(problem_path, "Question.INF")
                if os.path.exists(inf_path):
                    problem_info = ProblemService.parse_question_inf(inf_path, problem_dir, category_path)
                    if problem_info:
                        problems.append(problem_info)
        
        return problems
    
    @staticmethod
    def delete_problem(problem_path: str) -> str:
        """删除试题"""
        full_path = os.path.join(PROBLEMS_ROOT, problem_path)
        
        logger.info(f"删除试题: {problem_path}")
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            logger.error(f"试题不存在: {full_path}")
            raise FileNotFoundError(f"试题不存在: {problem_path}")
        
        # 删除试题文件夹
        shutil.rmtree(full_path)
        return f"试题 {problem_path} 已成功删除"
    
    @staticmethod
    def parse_question_inf(inf_path: str, problem_name: str, category_path: str) -> Optional[ProblemInfo]:
        """解析Question.INF文件，提取试题信息"""
        chinese_name = ""
        time_limit = ""
        memory_limit = ""
        
        # 首先尝试二进制方式读取文件，检查文件头
        try:
            with open(inf_path, "rb") as f:
                raw_data = f.read()
                # 检查是否有BOM标记
                if raw_data.startswith(b'\xef\xbb\xbf'):
                    content = raw_data[3:].decode('utf-8')
                # 检查是否有其他编码标记
                elif raw_data.startswith(b'\xff\xfe'):
                    content = raw_data[2:].decode('utf-16-le')
                elif raw_data.startswith(b'\xfe\xff'):
                    content = raw_data[2:].decode('utf-16-be')
                else:
                    # 尝试不同的编码
                    for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']:
                        try:
                            content = raw_data.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # 如果所有编码都失败，使用latin1（不会失败，但可能乱码）
                        logger.warning(f"文件 {inf_path} 编码识别失败，使用latin1作为后备")
                        content = raw_data.decode('latin1')
                
                # 解析文件内容
                for line in content.splitlines():
                    line = line.strip()
                    
                    if line.startswith("试题中文名称="):
                        value = line[len("试题中文名称="):].strip()
                        if value.startswith('"') and value.endswith('"'):
                            chinese_name = value[1:-1]
                        else:
                            chinese_name = value.split("//")[0].strip()
                    
                    elif line.startswith("时间限制="):
                        value = line[len("时间限制="):].strip()
                        time_limit = value.split("//")[0].strip()
                    
                    elif line.startswith("内存限制="):
                        value = line[len("内存限制="):].strip()
                        memory_limit = value.split("//")[0].strip()
                
                return ProblemInfo(
                    name=problem_name,
                    chinese_name=chinese_name if chinese_name else problem_name,
                    time_limit=time_limit if time_limit else "1000ms",
                    memory_limit=memory_limit if memory_limit else "256M",
                    data_path=os.path.join(category_path, problem_name),
                    category=os.path.basename(category_path)
                )
        except Exception as e:
            logger.error(f"解析试题信息失败: {str(e)}")
            return None

    @staticmethod
    def get_problem_detail(db: Session, problem_id: int) -> Optional[ProblemDetail]:
        """获取题目详情，包括HTML内容"""
        try:
            # 从数据库获取问题基本信息
            problem = db.query(Problem).filter(Problem.id == problem_id).first()
            if not problem:
                logger.error(f"题目不存在: ID {problem_id}")
                return None
            
            # 获取题目的HTML内容
            html_content = ProblemService.get_problem_html_content(problem.data_path)
            
            # 构建并返回问题详情
            return ProblemDetail(
                id=problem.id,
                name=problem.name,
                chinese_name=problem.chinese_name,
                time_limit=problem.time_limit,
                memory_limit=problem.memory_limit,
                html_content=html_content,
                data_path=problem.data_path,
                category=problem.category,
                code_check_score=problem.code_check_score,
                runtime_score=problem.runtime_score,
                score_method=problem.score_method
            )
        except Exception as e:
            logger.error(f"获取题目详情失败: {str(e)}")
            raise
    
    @staticmethod
    def get_problems_by_tag(db: Session, tag_id: int) -> List[Problem]:
        """根据标签获取问题列表"""
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            logger.error(f"标签不存在: ID {tag_id}")
            return []
        
        return tag.problems
    
    @staticmethod
    def get_problems_by_tag_type(db: Session, tag_type_id: int) -> List[Problem]:
        """根据标签类型获取问题列表"""
        # 获取该标签类型下的所有标签
        tags = db.query(Tag).filter(Tag.tag_type_id == tag_type_id).all()
        if not tags:
            logger.error(f"标签类型下没有标签: ID {tag_type_id}")
            return []
        
        # 获取所有问题
        problems = []
        for tag in tags:
            for problem in tag.problems:
                if problem not in problems:  # 避免重复
                    problems.append(problem)
        
        return problems
    
    @staticmethod
    def get_problem_html_content(data_path: str) -> str:
        """获取问题的HTML内容"""
        if not data_path:
            logger.warning("题目数据路径为空")
            return "<p>题目内容不可用</p>"
            
        # 构建可能的HTML文件路径
        problem_dir = os.path.join(PROBLEMS_ROOT, data_path)
        possible_html_paths = [
            os.path.join(problem_dir, f"{os.path.basename(data_path)}.htm"),  # Ex1.htm
            os.path.join(problem_dir, f"{os.path.basename(data_path)}.html"),  # Ex1.html
            os.path.join(problem_dir, "problem.htm"),  # problem.htm
            os.path.join(problem_dir, "problem.html"),  # problem.html
            os.path.join(problem_dir, "Question.htm"),  # Question.htm
            os.path.join(problem_dir, "Question.html")   # Question.html
        ]
        
        # 尝试找到并读取HTML文件
        html_content = "<p>题目内容不可用</p>"
        for html_path in possible_html_paths:
            if os.path.exists(html_path):
                try:
                    # 尝试以不同编码读取文件
                    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']
                    for encoding in encodings:
                        try:
                            with open(html_path, "r", encoding=encoding) as f:
                                html_content = f.read()
                                logger.info(f"成功读取题目HTML文件: {html_path}，使用编码: {encoding}")
                                break  # 成功读取，退出编码循环
                        except UnicodeDecodeError:
                            continue  # 尝试下一种编码
                    break  # 文件读取成功，退出文件路径循环
                except Exception as e:
                    logger.error(f"读取题目HTML文件失败: {str(e)}")
                    continue  # 尝试下一个可能的文件路径
        
        logger.info(f"HTML文件路径尝试完成，最终使用: {html_content[:100]}...")
        
        return html_content 