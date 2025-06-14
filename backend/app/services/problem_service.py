import os
import shutil
import logging
from typing import List, Optional
from app.schemas.problem import ProblemCategory, ProblemInfo

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 题库根目录 - 优先使用Docker挂载路径
PROBLEMS_ROOT = "/app/题库"  # Docker挂载的题库目录

# 如果Docker挂载路径不存在，尝试其他可能的路径
if not os.path.exists(PROBLEMS_ROOT):
    possible_paths = [
        "/app_root/题库",  # Docker挂载的整个项目中的题库
        "../题库",         # 相对于当前目录的父目录下的题库
        "../../题库"       # 再往上一级目录查找
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            PROBLEMS_ROOT = path
            break

logger.info(f"设置题库根目录为: {PROBLEMS_ROOT}")
logger.info(f"题库目录是否存在: {os.path.exists(PROBLEMS_ROOT)}")
logger.info(f"当前工作目录: {os.getcwd()}")

class ProblemService:
    @staticmethod
    def get_problem_categories() -> List[ProblemCategory]:
        """获取所有题库分类"""
        categories = []
        
        # 确保题库目录存在
        if not os.path.exists(PROBLEMS_ROOT):
            logger.error(f"题库目录不存在: {PROBLEMS_ROOT}")
            logger.info(f"当前工作目录: {os.getcwd()}")
            logger.info(f"目录内容: {os.listdir('.')}")
            
            # 尝试列出父目录内容
            try:
                parent_dir = os.path.dirname(os.getcwd())
                logger.info(f"父目录: {parent_dir}")
                logger.info(f"父目录内容: {os.listdir(parent_dir)}")
                
                # 尝试列出项目根目录
                try:
                    root_dir = os.path.dirname(parent_dir)
                    logger.info(f"项目根目录: {root_dir}")
                    logger.info(f"项目根目录内容: {os.listdir(root_dir)}")
                except Exception as e:
                    logger.error(f"无法列出项目根目录内容: {str(e)}")
            except Exception as e:
                logger.error(f"无法列出父目录内容: {str(e)}")
                
            raise FileNotFoundError(f"题库目录不存在: {PROBLEMS_ROOT}")
        
        logger.info(f"题库目录存在，开始扫描子目录")
        
        # 遍历题库根目录下的所有子目录
        for base_dir in os.listdir(PROBLEMS_ROOT):
            base_path = os.path.join(PROBLEMS_ROOT, base_dir)
            if os.path.isdir(base_path):
                logger.info(f"扫描基础题库: {base_dir}")
                # 遍历基础题库下的分类目录
                for category_dir in os.listdir(base_path):
                    category_path = os.path.join(base_path, category_dir)
                    if os.path.isdir(category_path):
                        # 提取分类名称（如"1.顺序结构"中的"顺序结构"）
                        category_name = category_dir
                        if "." in category_dir:
                            parts = category_dir.split(".", 1)
                            if len(parts) > 1:
                                category_name = parts[1]
                        
                        logger.info(f"找到分类: {category_name}, 路径: {os.path.join(base_dir, category_dir)}")
                        categories.append(ProblemCategory(
                            name=category_name,
                            path=os.path.join(base_dir, category_dir)
                        ))
        
        logger.info(f"共找到 {len(categories)} 个题库分类")
        return categories
    
    @staticmethod
    def get_problems_by_category(category_path: str) -> List[ProblemInfo]:
        """获取指定分类下的所有试题"""
        problems = []
        full_path = os.path.join(PROBLEMS_ROOT, category_path)
        
        logger.info(f"获取分类 {category_path} 下的试题，完整路径: {full_path}")
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            logger.error(f"题库分类不存在: {full_path}")
            raise FileNotFoundError(f"题库分类不存在: {category_path}")
        
        # 遍历分类目录下的所有试题文件夹
        for problem_dir in os.listdir(full_path):
            problem_path = os.path.join(full_path, problem_dir)
            if os.path.isdir(problem_path):
                # 读取Question.INF文件
                inf_path = os.path.join(problem_path, "Question.INF")
                if os.path.exists(inf_path):
                    logger.info(f"找到试题: {problem_dir}, 正在解析 Question.INF")
                    problem_info = ProblemService.parse_question_inf(inf_path, problem_dir, category_path)
                    if problem_info:
                        problems.append(problem_info)
        
        logger.info(f"分类 {category_path} 下共找到 {len(problems)} 个试题")
        return problems
    
    @staticmethod
    def delete_problem(problem_path: str) -> str:
        """删除试题"""
        full_path = os.path.join(PROBLEMS_ROOT, problem_path)
        
        logger.info(f"尝试删除试题: {problem_path}, 完整路径: {full_path}")
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            logger.error(f"试题不存在: {full_path}")
            raise FileNotFoundError(f"试题不存在: {problem_path}")
        
        # 删除试题文件夹
        shutil.rmtree(full_path)
        logger.info(f"试题 {problem_path} 已成功删除")
        return f"试题 {problem_path} 已成功删除"
    
    @staticmethod
    def parse_question_inf(inf_path: str, problem_name: str, category_path: str) -> Optional[ProblemInfo]:
        """解析Question.INF文件，提取试题信息"""
        chinese_name = ""
        time_limit = ""
        memory_limit = ""
        
        try:
            with open(inf_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("试题中文名称="):
                        chinese_name = line.split("=", 1)[1].strip('"')
                    elif line.startswith("时间限制="):
                        time_limit = line.split("=", 1)[1].split("//")[0].strip()
                    elif line.startswith("内存限制="):
                        memory_limit = line.split("=", 1)[1].split("//")[0].strip()
            
            logger.info(f"解析试题成功: {problem_name}, 中文名称: {chinese_name}")
            return ProblemInfo(
                name=problem_name,
                chinese_name=chinese_name,
                time_limit=time_limit,
                memory_limit=memory_limit,
                data_path=os.path.join(category_path, problem_name),
                category=category_path.split("/")[-1] if "/" in category_path else category_path
            )
        except Exception as e:
            logger.error(f"解析试题信息失败: {str(e)}")
            return None 