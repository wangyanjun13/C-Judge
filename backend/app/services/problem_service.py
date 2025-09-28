import os
import shutil
import logging
import re
import html
from typing import List, Optional, Dict, Any
from app.schemas.problem import ProblemCategory, ProblemInfo, ProblemDetail, CustomProblemCreate, CustomProblemResponse
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
        # 构建完整的题目路径
        full_path = os.path.join(PROBLEMS_ROOT, problem_path)
        
        # 检查路径是否存在
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"试题路径不存在: {problem_path}")
        
        # 删除试题目录
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
            logger.info(f"成功删除试题目录: {problem_path}")
            return f"成功删除试题: {problem_path}"
        else:
            raise ValueError(f"路径不是有效的试题目录: {problem_path}")

    @staticmethod
    def get_all_problems_data(
        db: Session,
        tag_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None,
        tag_type_id: Optional[int] = None,
        include_tags: bool = True
    ) -> Dict[str, Any]:
        """
        一次性获取所有题库数据（优化版本）
        减少多次API调用，提高性能
        
        Args:
            db: 数据库会话
            tag_id: 按标签ID过滤（可选）
            tag_ids: 按多个标签ID交集过滤（可选）
            tag_type_id: 按标签类型ID过滤（可选）
            include_tags: 是否包含标签数据
            
        Returns:
            包含所有数据的字典
        """
        try:
            logger.info("开始获取所有题库数据（服务层）")
            
            # 初始化结果
            result = {
                'categories': [],
                'problems': [],
                'tag_types': [],
                'tags': [],
                'problem_tags': {}
            }
            
            # 1. 获取所有分类
            result['categories'] = ProblemService.get_problem_categories()
            logger.info(f"获取到 {len(result['categories'])} 个分类")
            
            # 2. 获取所有题目（根据过滤条件）
            all_problems = []
            
            if tag_ids is not None and len(tag_ids) > 0:
                # 按多个标签ID交集过滤
                # 先获取所有题目，然后进行交集过滤
                for category in result['categories']:
                    try:
                        category_problems = ProblemService.get_problems_by_category(category.path)
                        all_problems.extend(category_problems)
                    except Exception as e:
                        logger.warning(f"获取分类 {category.path} 的题目失败: {str(e)}")
                        continue
                
                # 进行多标签交集过滤
                all_problems = ProblemService.filter_problems_by_tags_intersection(db, all_problems, tag_ids)
                        
            elif tag_id is not None:
                # 按标签ID过滤
                tag_problems = ProblemService.get_problems_by_tag(db, tag_id)
                tag_problem_paths = [p.data_path for p in tag_problems if p.data_path]
                
                # 从所有分类中获取题目，然后过滤
                for category in result['categories']:
                    try:
                        category_problems = ProblemService.get_problems_by_category(category.path)
                        filtered_problems = [p for p in category_problems if p.data_path in tag_problem_paths]
                        all_problems.extend(filtered_problems)
                    except Exception as e:
                        logger.warning(f"获取分类 {category.path} 的题目失败: {str(e)}")
                        continue
                        
            elif tag_type_id is not None:
                # 按标签类型ID过滤
                type_problems = ProblemService.get_problems_by_tag_type(db, tag_type_id)
                type_problem_paths = [p.data_path for p in type_problems if p.data_path]
                
                # 从所有分类中获取题目，然后过滤
                for category in result['categories']:
                    try:
                        category_problems = ProblemService.get_problems_by_category(category.path)
                        filtered_problems = [p for p in category_problems if p.data_path in type_problem_paths]
                        all_problems.extend(filtered_problems)
                    except Exception as e:
                        logger.warning(f"获取分类 {category.path} 的题目失败: {str(e)}")
                        continue
            else:
                # 获取所有题目
                for category in result['categories']:
                    try:
                        category_problems = ProblemService.get_problems_by_category(category.path)
                        all_problems.extend(category_problems)
                    except Exception as e:
                        logger.warning(f"获取分类 {category.path} 的题目失败: {str(e)}")
                        continue
            
            # 去重（基于data_path）
            unique_problems = {}
            for problem in all_problems:
                if problem.data_path and problem.data_path not in unique_problems:
                    unique_problems[problem.data_path] = problem
            
            result['problems'] = list(unique_problems.values())
            logger.info(f"获取到 {len(result['problems'])} 个唯一题目")
            
            # 3. 如果需要标签数据，获取标签类型和标签
            if include_tags:
                try:
                    # 获取所有标签类型
                    result['tag_types'] = db.query(TagType).all()
                    logger.info(f"获取到 {len(result['tag_types'])} 个标签类型")
                    
                    # 获取所有标签
                    result['tags'] = db.query(Tag).all()
                    logger.info(f"获取到 {len(result['tags'])} 个标签")
                    
                    # 4. 批量获取题目标签关系
                    if result['problems']:
                        problem_paths = [p.data_path for p in result['problems'] if p.data_path]
                        
                        # 批量查询题目标签关系
                        from app.models import problem_tag  # 关联表
                        
                        # 查询所有相关的题目记录
                        db_problems = db.query(Problem).filter(Problem.data_path.in_(problem_paths)).all()
                        
                        # 为每个题目获取标签
                        for db_problem in db_problems:
                            if db_problem.data_path:
                                # 获取该题目的所有标签
                                problem_tag_objs = db.query(Tag).join(problem_tag).filter(
                                    problem_tag.c.problem_id == db_problem.id
                                ).all()
                                
                                result['problem_tags'][db_problem.data_path] = [
                                    {
                                        'id': tag.id,
                                        'name': tag.name,
                                        'tag_type_id': tag.tag_type_id
                                    }
                                    for tag in problem_tag_objs
                                ]
                        
                        logger.info(f"获取到 {len(result['problem_tags'])} 个题目的标签关系")
                
                except Exception as e:
                    logger.error(f"获取标签数据失败: {str(e)}")
                    # 标签数据获取失败不影响主要功能，继续返回其他数据
                    pass
            
            logger.info("所有题库数据获取完成（服务层）")
            return result
            
        except Exception as e:
            logger.error(f"获取所有题库数据失败（服务层）: {str(e)}")
            raise e
    
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
                    # 二进制读取，检测BOM
                    with open(html_path, "rb") as f:
                        raw_data = f.read()
                        if raw_data.startswith(b'\xff\xfe'):  # UTF-16 LE
                            content = raw_data[2:].decode('utf-16-le')
                        elif raw_data.startswith(b'\xef\xbb\xbf'):  # UTF-8
                            content = raw_data[3:].decode('utf-8')
                        else:
                            # 尝试编码
                            for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']:
                                try:
                                    content = raw_data.decode(encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                content = raw_data.decode('latin1')
                    
                    html_content = content
                    logger.info(f"成功读取题目HTML文件: {html_path}")
                    break  # 文件读取成功，退出文件路径循环
                except Exception as e:
                    logger.error(f"读取题目HTML文件失败: {str(e)}")
                    continue  # 尝试下一个可能的文件路径
        
        logger.info(f"HTML文件路径尝试完成，最终使用: {html_content[:100]}...")
        
        return html_content 

    @staticmethod
    def filter_problems_by_tags_intersection(db: Session, problems: List[ProblemInfo], tag_ids: List[int]) -> List[ProblemInfo]:
        """
        根据多个标签ID进行交集过滤，只返回同时包含所有指定标签的题目
        
        Args:
            db: 数据库会话
            problems: 待过滤的题目列表
            tag_ids: 标签ID列表
            
        Returns:
            过滤后的题目列表
        """
        if not tag_ids or not problems:
            return problems
        
        # 获取所有题目的data_path
        problem_paths = [p.data_path for p in problems if p.data_path]
        if not problem_paths:
            return []
        
        # 查询所有涉及的问题和标签关系
        from app.models.problem import Problem, problem_tag
        from app.models.tag import Tag
        
        # 对于每个标签，查找包含该标签的问题
        filtered_paths_sets = []
        
        for tag_id in tag_ids:
            # 查询包含当前标签的所有问题的data_path
            tag_problem_paths = db.query(Problem.data_path).join(
                problem_tag, Problem.id == problem_tag.c.problem_id
            ).filter(
                problem_tag.c.tag_id == tag_id,
                Problem.data_path.in_(problem_paths)
            ).all()
            
            # 提取data_path列表
            paths_set = set(path[0] for path in tag_problem_paths if path[0])
            filtered_paths_sets.append(paths_set)
        
        # 计算所有标签的交集
        if filtered_paths_sets:
            intersection_paths = set.intersection(*filtered_paths_sets)
            # 返回在交集中的题目
            return [p for p in problems if p.data_path in intersection_paths]
        
        return [] 

    @staticmethod
    def create_custom_problem(problem_data: CustomProblemCreate, db: Session = None) -> CustomProblemResponse:
        """
        创建自定义题目，生成符合现有系统的文件结构
        
        Args:
            problem_data: 题目创建数据
            db: 数据库会话（用于设置标签）
            
        Returns:
            创建结果响应
        """
        try:
            logger.info(f"开始创建自定义题目: {problem_data.name}")
            
            # 1. 数据验证
            validation_result = ProblemService._validate_custom_problem_data(problem_data)
            if not validation_result["valid"]:
                return CustomProblemResponse(
                    success=False,
                    message=validation_result["message"]
                )
            
            # 2. 确保题目名称唯一
            unique_name = ProblemService._ensure_unique_problem_name(problem_data.name)
            
            # 3. 构建题目路径
            custom_category_path = "自定义题库"
            problem_dir = os.path.join(PROBLEMS_ROOT, custom_category_path, unique_name)
            
            # 4. 创建题目目录
            os.makedirs(problem_dir, exist_ok=True)
            logger.info(f"创建题目目录: {problem_dir}")
            
            # 5. 生成Question.INF文件
            ProblemService._create_question_inf(problem_dir, unique_name, problem_data.chinese_name)
            
            # 6. 生成HTML文件
            ProblemService._create_problem_html(problem_dir, unique_name, problem_data.description, problem_data.chinese_name)
            
            # 7. 生成测试用例文件
            ProblemService._create_test_cases(problem_dir, problem_data.testcases)
            
            # 8. 计算相对路径
            relative_path = os.path.join(custom_category_path, unique_name)
            
            # 9. 如果有数据库会话，保存题目信息到数据库
            if db:
                try:
                    # 创建数据库记录
                    from app.models.problem import Problem
                    problem = Problem(
                        name=unique_name,
                        chinese_name=problem_data.chinese_name,
                        data_path=relative_path,
                        category=custom_category_path,
                        is_shared=False,
                        reference_answer=problem_data.reference_answer  # 保存参考答案
                    )
                    db.add(problem)
                    db.commit()
                    logger.info(f"题目记录已保存到数据库: ID {problem.id}")
                except Exception as e:
                    logger.error(f"保存题目到数据库失败: {str(e)}")
                    db.rollback()
                    # 数据库保存失败不影响文件创建，继续执行
            
            # 10. 如果有标签且数据库会话可用，设置标签
            if problem_data.tag_ids and db:
                try:
                    from app.services.tag_service import TagService
                    TagService.set_problem_tags(db, relative_path, problem_data.tag_ids)
                    logger.info(f"为题目 {relative_path} 设置标签: {problem_data.tag_ids}")
                except Exception as e:
                    logger.warning(f"设置标签失败: {str(e)}")
            
            logger.info(f"自定义题目创建成功: {relative_path}")
            
            return CustomProblemResponse(
                success=True,
                message=f"题目 '{problem_data.chinese_name}' 创建成功",
                problem_path=relative_path
            )
            
        except Exception as e:
            logger.error(f"创建自定义题目失败: {str(e)}")
            return CustomProblemResponse(
                success=False,
                message=f"创建题目失败: {str(e)}"
            )

    @staticmethod
    def _validate_custom_problem_data(problem_data: CustomProblemCreate) -> Dict[str, Any]:
        """验证自定义题目数据"""
        
        # 验证题目名称
        if not problem_data.name or not problem_data.name.strip():
            return {"valid": False, "message": "题目名称不能为空"}
        
        if len(problem_data.name) > 50:
            return {"valid": False, "message": "题目名称不能超过50个字符"}
        
        if not re.match(r'^[a-zA-Z0-9_]+$', problem_data.name):
            return {"valid": False, "message": "题目名称只能包含字母、数字和下划线"}
        
        # 验证中文名称
        if not problem_data.chinese_name or not problem_data.chinese_name.strip():
            return {"valid": False, "message": "题目中文名称不能为空"}
        
        if len(problem_data.chinese_name) > 100:
            return {"valid": False, "message": "题目中文名称不能超过100个字符"}
        
        # 验证描述
        if not problem_data.description or not problem_data.description.strip():
            return {"valid": False, "message": "题目描述不能为空"}
        
        if len(problem_data.description) > 10000:
            return {"valid": False, "message": "题目描述不能超过10000个字符"}
        
        # 验证测试用例
        if not problem_data.testcases or len(problem_data.testcases) == 0:
            return {"valid": False, "message": "至少需要一个测试用例"}
        
        if len(problem_data.testcases) > 20:
            return {"valid": False, "message": "测试用例数量不能超过20个"}
        
        for i, testcase in enumerate(problem_data.testcases):
            # 允许输入和输出都为空
            # 只有当输入不为空时才检查长度
            if testcase.input and len(testcase.input) > 2000:
                return {"valid": False, "message": f"第{i+1}个测试用例的输入不能超过2000个字符"}
            
            # 只有当输出不为空时才检查长度
            if testcase.output and len(testcase.output) > 2000:
                return {"valid": False, "message": f"第{i+1}个测试用例的输出不能超过2000个字符"}
        
        return {"valid": True, "message": "验证通过"}

    @staticmethod
    def _ensure_unique_problem_name(name: str) -> str:
        """确保题目名称唯一，如果重复则添加数字后缀"""
        custom_category_path = os.path.join(PROBLEMS_ROOT, "自定义题库")
        
        # 创建自定义题库目录（如果不存在）
        os.makedirs(custom_category_path, exist_ok=True)
        
        base_name = name
        counter = 1
        current_name = base_name
        
        while os.path.exists(os.path.join(custom_category_path, current_name)):
            current_name = f"{base_name}_{counter}"
            counter += 1
        
        return current_name

    @staticmethod
    def _create_question_inf(problem_dir: str, name: str, chinese_name: str):
        """创建Question.INF文件"""
        inf_content = f"""试题中文名称={chinese_name}
时间限制=1000ms
内存限制=256M
"""
        
        inf_path = os.path.join(problem_dir, "Question.INF")
        
        # 使用UTF-8编码写入文件
        with open(inf_path, "w", encoding="utf-8") as f:
            f.write(inf_content)
        
        logger.info(f"创建Question.INF文件: {inf_path}")

    @staticmethod
    def _create_problem_html(problem_dir: str, name: str, description: str, chinese_name: str):
        """创建题目HTML文件"""
        
        print(f"=== 开始创建HTML文件 ===")
        print(f"题目名称: {name}")
        print(f"描述内容: {repr(description)}")
        
        # 解析描述中的结构化信息
        parsed_sections = ProblemService._parse_description(description)
        
        # 生成统一格式的HTML
        html_content = ProblemService._generate_problem_html({
            'name': name,
            'chinese_name': chinese_name,
            **parsed_sections
        })
        
        html_path = os.path.join(problem_dir, f"{name}.htm")
        
        # 使用UTF-8编码写入文件以保持兼容性
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"创建HTML文件: {html_path}")

    @staticmethod
    def _parse_description(description: str) -> dict:
        """解析题目描述，提取结构化信息"""
        if not description:
            return {'description': ''}
        
        sections = {}
        lines = description.split('\n')
        current_section = 'description'
        content = []
        
        # 常见的章节标识符 - 按优先级排序，更具体的模式在前
        section_patterns = {
            'sample_input': r'^(输入示例)[:：]?',
            'sample_output': r'^(输出示例)[:：]?',
            'input_format': r'^(输入)[:：]?',
            'output_format': r'^(输出)[:：]?',
            'description': r'^(题目描述)[:：]?',
            'data_range': r'^(数据范围)[:：]?',
            'note': r'^(注意)[:：]?'
        }
        
        import re
        
        for line in lines:
            trimmed_line = line.strip()
            
            # 检查是否是新的章节
            found_section = None
            for section, pattern in section_patterns.items():
                if re.match(pattern, trimmed_line, re.IGNORECASE):
                    found_section = section
                    break
            
            if found_section:
                # 保存当前章节内容
                if content:
                    sections[current_section] = '\n'.join(content).strip()
                
                # 开始新章节
                current_section = found_section
                content = []
                
                # 如果这行除了标题还有内容，也要包含进去
                content_after_title = re.sub(section_patterns[found_section], '', trimmed_line, flags=re.IGNORECASE).strip()
                if content_after_title:
                    content.append(content_after_title)
            else:
                # 添加到当前章节
                content.append(line)
        
        # 保存最后一个章节
        if content:
            sections[current_section] = '\n'.join(content).strip()
        
        # 调试日志：显示解析结果
        print(f"=== 解析结果 ===")
        for key, value in sections.items():
            print(f"{key}: {repr(value)}")
        print(f"================")
        
        return sections

    @staticmethod
    def _generate_problem_html(problem_data: dict) -> str:
        """生成统一格式的题目HTML"""
        name = problem_data.get('name', '')
        chinese_name = problem_data.get('chinese_name', '')
        description = problem_data.get('description', '')
        input_format = problem_data.get('input_format', '')
        output_format = problem_data.get('output_format', '')
        sample_input = problem_data.get('sample_input', '')
        sample_output = problem_data.get('sample_output', '')
        data_range = problem_data.get('data_range', '')
        note = problem_data.get('note', '')
        
        # 转义HTML特殊字符
        def escape_html(text):
            if not text:
                return ''
            return (html.escape(text)
                   .replace('\n', '</br>　　'))
        
        # 转义不带换行的文本
        def escape_simple(text):
            if not text:
                return ''
            return html.escape(text)
        
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>题目</title>
    <style type="text/css">
        .SimSun
        {{
            font-size: 14px;
            font-family: 宋体;
        }}
        body {{
            background: #FFFFFF;
            margin: 0;
            padding: 0;
        }}
        .container {{
            margin: 0px auto;
            width: 1000px;
            padding: 20px;
        }}
        .title {{
            font-family: 宋体;
            font-size: 18px;
            font-weight: bold;
            color: Green;
            text-align: center;
            margin-bottom: 20px;
        }}
        .section-title {{
            font-family: 宋体;
            font-size: 16px;
            font-weight: bold;
            color: Green;
            margin-left: 20px;
            margin-top: 15px;
            margin-bottom: 5px;
        }}
        .content {{
            line-height: 22px;
            margin-left: 20px;
            margin-right: 20px;
            text-indent: 2em;
        }}
        .note-text {{
            color: #FF0000;
        }}
        .sample-data {{
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 5px;
            border: 1px solid #ddd;
            margin: 5px 0;
            text-indent: 0;
        }}
    </style>
</head>

<body>
    <div class="container">
        <p class="title">{escape_simple(chinese_name or name)}</p>"""
        
        if description:
            html_template += f"""
        
        <p class="section-title">题目描述</p>
        <p class="SimSun content">{escape_html(description)}</p>"""
        
        if input_format:
            html_template += f"""
        
        <p class="section-title">输入</p>
        <p class="SimSun content">{escape_html(input_format)}</p>"""
        
        if output_format:
            html_template += f"""
        
        <p class="section-title">输出</p>
        <p class="SimSun content">{escape_html(output_format)}</p>"""
        
        if sample_input:
            html_template += f"""
        
        <p class="section-title">输入示例</p>
        <p class="SimSun content">{escape_html(sample_input)}</p>"""
        
        if sample_output:
            html_template += f"""
        
        <p class="section-title">输出示例</p>
        <p class="SimSun content">{escape_html(sample_output)}</p>"""
        
        if data_range:
            html_template += f"""
        
        <p class="section-title">数据范围</p>
        <p class="SimSun content">{escape_html(data_range)}</p>"""
        
        if note:
            html_template += f"""
        
        <p class="section-title">注意</p>
        <p class="SimSun content"><span class="note-text">{escape_html(note)}</span></p>"""
        
        html_template += """
    </div>
</body>
</html>"""
        
        return html_template

    @staticmethod
    def _create_test_cases(problem_dir: str, testcases: List):
        """创建测试用例文件"""
        for i, testcase in enumerate(testcases, 1):
            # 创建输入文件
            input_path = os.path.join(problem_dir, f"{i}.in")
            with open(input_path, "w", encoding="utf-8") as f:
                f.write(testcase.input)
            
            # 创建输出文件
            output_path = os.path.join(problem_dir, f"{i}.out")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(testcase.output)
            
            logger.info(f"创建测试用例 {i}: {input_path}, {output_path}")
        
        logger.info(f"总共创建了 {len(testcases)} 组测试用例") 



    @staticmethod
    def check_favorite_status(db: Session, user_id: int, problem_id: int) -> dict:
        """
        检查题目的收藏状态
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            problem_id: 题目ID
            
        Returns:
            收藏状态和收藏总数
        """
        try:
            from app.models import user_favorites
            
            # 检查当前用户是否收藏了该题目
            is_favorited = db.query(user_favorites).filter(
                user_favorites.c.user_id == user_id,
                user_favorites.c.problem_id == problem_id
            ).first() is not None
            
            # 获取该题目的总收藏数
            favorite_count = db.query(user_favorites).filter(
                user_favorites.c.problem_id == problem_id
            ).count()
            
            return {
                "is_favorited": is_favorited,
                "favorite_count": favorite_count
            }
            
        except Exception as e:
            logger.error(f"检查收藏状态失败: {str(e)}")
            return {"is_favorited": False, "favorite_count": 0}

    @staticmethod
    def get_batch_favorite_status(db: Session, user_id: int, problem_ids: List[int]) -> dict:
        """
        批量获取题目的收藏状态
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            problem_ids: 题目ID列表
            
        Returns:
            题目ID到收藏状态的映射
        """
        try:
            from app.models import user_favorites
            
            # 查询用户收藏的题目
            favorited_problems = db.query(user_favorites.c.problem_id).filter(
                user_favorites.c.user_id == user_id,
                user_favorites.c.problem_id.in_(problem_ids)
            ).all()
            
            favorited_ids = {row[0] for row in favorited_problems}
            
            # 构建结果字典
            result = {}
            for problem_id in problem_ids:
                result[problem_id] = {
                    "is_favorited": problem_id in favorited_ids
                }
            
            return result
            
        except Exception as e:
            logger.error(f"批量获取收藏状态失败: {str(e)}")
            return {}

    @staticmethod
    def toggle_favorite(db: Session, user_id: int, problem_id: int) -> dict:
        """
        切换题目的收藏状态
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            problem_id: 题目ID
            
        Returns:
            操作结果字典
        """
        try:
            from app.models import Problem, User, user_favorites
            
            # 验证用户和题目是否存在
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "用户不存在"}
            
            problem = db.query(Problem).filter(Problem.id == problem_id).first()
            if not problem:
                return {"success": False, "message": "题目不存在"}
            
            # 检查当前收藏状态
            existing = db.query(user_favorites).filter(
                user_favorites.c.user_id == user_id,
                user_favorites.c.problem_id == problem_id
            ).first()
            
            if existing:
                # 已收藏，取消收藏
                stmt = user_favorites.delete().where(
                    user_favorites.c.user_id == user_id,
                    user_favorites.c.problem_id == problem_id
                )
                db.execute(stmt)
                db.commit()
                
                logger.info(f"用户 {user_id} 取消收藏题目 {problem_id}")
                return {"success": True, "message": "取消收藏成功", "is_favorited": False}
            else:
                # 未收藏，添加收藏
                stmt = user_favorites.insert().values(user_id=user_id, problem_id=problem_id)
                db.execute(stmt)
                db.commit()
                
                logger.info(f"用户 {user_id} 收藏了题目 {problem_id}")
                return {"success": True, "message": "收藏成功", "is_favorited": True}
                
        except Exception as e:
            logger.error(f"切换收藏状态失败: {str(e)}")
            db.rollback()
            return {"success": False, "message": f"操作失败: {str(e)}"}

    @staticmethod
    def get_user_favorite_problems(db: Session, user_id: int) -> List[dict]:
        """
        获取用户收藏的题目列表，包含得分、练习、课程等信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            收藏的题目列表，包含额外的提交信息
        """
        try:
            from app.models import Problem, user_favorites, Submission, Exercise, Course
            from sqlalchemy import func, desc
            
            # 查询用户收藏的题目，按收藏时间倒序排列
            favorites = db.query(
                Problem,
                user_favorites.c.created_at.label('favorite_time')
            ).join(
                user_favorites, Problem.id == user_favorites.c.problem_id
            ).filter(
                user_favorites.c.user_id == user_id
            ).order_by(
                user_favorites.c.created_at.desc()
            ).all()
            
            # 组装返回数据
            favorite_list = []
            for problem, favorite_time in favorites:
                # 获取该用户在此题目上的最佳得分
                best_submission = db.query(Submission).filter(
                    Submission.user_id == user_id,
                    Submission.problem_id == problem.id
                ).order_by(desc(Submission.total_score)).first()
                
                # 获取最近一次提交的练习和课程信息
                recent_submission = db.query(Submission).filter(
                    Submission.user_id == user_id,
                    Submission.problem_id == problem.id
                ).order_by(desc(Submission.submitted_at)).first()
                
                exercise_name = None
                course_name = None
                exercise_id = None
                course_id = None
                
                if recent_submission and recent_submission.exercise_id:
                    exercise = db.query(Exercise).filter(Exercise.id == recent_submission.exercise_id).first()
                    if exercise:
                        exercise_name = exercise.name
                        exercise_id = exercise.id
                        if exercise.course_id:
                            course = db.query(Course).filter(Course.id == exercise.course_id).first()
                            if course:
                                course_name = course.name
                                course_id = course.id
                
                favorite_item = {
                    "id": problem.id,
                    "name": problem.name,
                    "chinese_name": problem.chinese_name,
                    "category": problem.category,
                    "data_path": problem.data_path,
                    "time_limit": problem.time_limit,
                    "memory_limit": problem.memory_limit,
                    "code_check_score": problem.code_check_score,
                    "runtime_score": problem.runtime_score,
                    "score_method": problem.score_method,
                    "is_shared": problem.is_shared,
                    "created_at": problem.created_at,
                    "favorite_time": favorite_time,
                    # 添加提交相关信息
                    "best_score": best_submission.total_score if best_submission else None,
                    "exercise_id": exercise_id,
                    "exercise_name": exercise_name,
                    "course_id": course_id,
                    "course_name": course_name
                }
                favorite_list.append(favorite_item)
            
            logger.info(f"获取用户 {user_id} 的收藏列表，共 {len(favorite_list)} 个题目")
            return favorite_list
            
        except Exception as e:
            logger.error(f"获取用户收藏列表失败: {str(e)}")
            return []

 