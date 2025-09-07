import axios from '../utils/axios'

/**
 * 获取题库分类列表
 * @returns {Promise} - 返回题库分类列表
 */
export const getProblemCategories = async () => {
  try {
    const response = await axios.get('/api/problems/categories');
    console.log('题库分类API响应:', response.data);
    // 确保返回数据是数组
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取题库分类列表失败:', error);
    return [];
  }
}

/**
 * 获取指定分类下的试题列表
 * @param {String} categoryPath - 分类路径
 * @param {Object} options - 过滤选项
 * @param {Number} options.tagId - 按标签ID过滤（可选）
 * @param {Array} options.tagIds - 按多个标签ID过滤，取交集（可选）
 * @param {Number} options.tagTypeId - 按标签类型ID过滤（可选）
 * @returns {Promise} - 返回试题列表
 */
export const getProblemsByCategory = async (categoryPath, options = {}) => {
  try {
    console.log('请求分类下的试题:', categoryPath);
    const params = {};
    
    // 添加过滤参数
    if (options.tagIds && Array.isArray(options.tagIds) && options.tagIds.length > 0) {
      params.tag_ids = options.tagIds.join(',');
    } else if (options.tagId) {
      params.tag_id = options.tagId;
    }
    if (options.tagTypeId) {
      params.tag_type_id = options.tagTypeId;
    }
    
    const response = await axios.get(`/api/problems/list/${encodeURIComponent(categoryPath)}`, { params });
    console.log('试题列表API响应:', response.data);
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取试题列表失败:', error);
    return [];
  }
}

/**
 * 更新试题信息
 * @param {String} problemPath - 试题路径
 * @param {Object} problemData - 试题更新数据
 * @returns {Promise} - 返回更新后的试题
 */
export const updateProblem = async (problemPath, problemData) => {
  try {
    const response = await axios.put(`/api/problems/${encodeURIComponent(problemPath)}`, problemData);
    return response.data;
  } catch (error) {
    console.error('更新试题失败:', error);
    throw error;
  }
}

// 注意：setProblemTags函数已移至tags.js，避免重复定义

/**
 * 删除试题
 * @param {String} problemPath - 试题路径
 * @returns {Promise} - 返回删除结果
 */
export const deleteProblem = async (problemPath) => {
  try {
    const response = await axios.delete(`/api/problems/${encodeURIComponent(problemPath)}`);
    return response.data;
  } catch (error) {
    console.error('删除试题失败:', error);
    throw error;
  }
}

/**
 * 一次性获取所有题库数据（优化版本，减少并发请求）
 * @param {Object} options - 过滤选项
 * @param {Number} options.tagId - 按标签ID过滤（可选）
 * @param {Array} options.tagIds - 按多个标签ID过滤，取交集（可选）
 * @param {Number} options.tagTypeId - 按标签类型ID过滤（可选）
 * @param {Boolean} options.includeTagData - 是否包含标签数据（默认true）
 * @returns {Promise<Object>} - 返回包含所有数据的对象
 */
export const getAllProblemsData = async (options = {}) => {
  try {
    console.log('开始获取所有题库数据（优化版本）');
    const params = {};
    
    // 添加过滤参数
    if (options.tagIds && Array.isArray(options.tagIds) && options.tagIds.length > 0) {
      params.tag_ids = options.tagIds.join(',');
    } else if (options.tagId) {
      params.tag_id = options.tagId;
    }
    if (options.tagTypeId) {
      params.tag_type_id = options.tagTypeId;
    }
    
    // 默认包含标签数据
    if (options.includeTagData !== false) {
      params.include_tags = true;
    }
    
    const response = await axios.get('/api/problems/all-data', { params });
    
    console.log('所有题库数据API响应:', {
      categories: response.data.categories?.length || 0,
      problems: response.data.problems?.length || 0,
      tagTypes: response.data.tag_types?.length || 0,
      tags: response.data.tags?.length || 0
    });
    
    return {
      categories: Array.isArray(response.data.categories) ? response.data.categories : [],
      problems: Array.isArray(response.data.problems) ? response.data.problems : [],
      tagTypes: Array.isArray(response.data.tag_types) ? response.data.tag_types : [],
      tags: Array.isArray(response.data.tags) ? response.data.tags : [],
      problemTags: response.data.problem_tags || {}
    };
  } catch (error) {
    console.error('获取所有题库数据失败:', error);
    // 返回空的结构，避免前端报错
    return {
      categories: [],
      problems: [],
      tagTypes: [],
      tags: [],
      problemTags: {}
    };
  }
} 

/**
 * 创建自定义题目
 * @param {Object} problemData - 题目数据
 * @param {String} problemData.name - 题目名称（英文）
 * @param {String} problemData.chineseName - 题目中文名称
 * @param {String} problemData.description - 题目描述
 * @param {Array} problemData.testcases - 测试用例数组
 * @param {String} problemData.reference_answer - 参考答案（可选）
 * @returns {Promise<Object>} - 返回创建结果
 */
export const createCustomProblem = async (problemData) => {
  try {
    console.log('开始创建自定义题目:', problemData.name);
    
    // 数据验证
    if (!problemData.name || !problemData.chineseName || !problemData.description) {
      throw new Error('题目名称、中文名称和描述都不能为空');
    }
    
    if (!problemData.testcases || problemData.testcases.length === 0) {
      throw new Error('至少需要一个测试用例');
    }
    
    // 验证测试用例
    for (let i = 0; i < problemData.testcases.length; i++) {
      const testcase = problemData.testcases[i];
      if (!testcase.input || !testcase.output) {
        throw new Error(`第${i + 1}个测试用例的输入和输出都不能为空`);
      }
    }
    
    // 构造请求数据
    const requestData = {
      name: problemData.name.trim(),
      chinese_name: problemData.chineseName.trim(),
      description: problemData.description.trim(),
      testcases: problemData.testcases.map(tc => ({
        input: tc.input.trim(),
        output: tc.output.trim()
      })),
      tag_ids: problemData.tag_ids || [],  // 添加标签ID列表
      reference_answer: problemData.reference_answer || null  // 添加参考答案
    };
    
    console.log('发送创建自定义题目请求:', requestData);
    
    const response = await axios.post('/api/problems/custom', requestData);
    
    console.log('创建自定义题目响应:', response.data);
    
    return response.data;
    
  } catch (error) {
    console.error('创建自定义题目失败:', error);
    
    // 处理不同类型的错误
    if (error.response && error.response.data && error.response.data.detail) {
      throw new Error(error.response.data.detail);
    } else if (error.message) {
      throw new Error(error.message);
    } else {
      throw new Error('创建题目失败，请重试');
    }
  }
} 

/**
 * 获取题目的参考代码
 * @param {String} problemPath - 题目路径
 * @returns {Promise<Object>} - 返回参考代码信息
 */
export const getProblemReferenceAnswer = async (problemPath) => {
  try {
    const response = await axios.get(`/api/problems/reference-answer/${encodeURIComponent(problemPath)}`);
    return response.data;
  } catch (error) {
    console.error('获取题目参考代码失败:', error);
    return { reference_answer: null };
  }
}

// 收藏相关API
/**
 * 添加或取消收藏题目
 * @param {Number} problemId - 题目ID
 * @returns {Promise<Object>} - 返回收藏操作结果
 */
export const toggleFavoriteProblem = async (problemId) => {
  try {
    const response = await axios.post(`/api/problems/favorites/toggle/${problemId}`);
    return response.data;
  } catch (error) {
    console.error('收藏操作失败:', error);
    throw error;
  }
}

/**
 * 获取题目收藏状态
 * @param {Number} problemId - 题目ID
 * @returns {Promise<Object>} - 返回收藏状态
 */
export const getFavoriteStatus = async (problemId) => {
  try {
    const response = await axios.get(`/api/problems/favorites/status/${problemId}`);
    return response.data;
  } catch (error) {
    console.error('获取收藏状态失败:', error);
    return { is_favorited: false, favorite_count: 0 };
  }
}

/**
 * 批量获取多个题目的收藏状态
 * @param {Array} problemIds - 题目ID数组
 * @returns {Promise<Object>} - 返回收藏状态映射
 */
export const getBatchFavoriteStatus = async (problemIds) => {
  try {
    if (!problemIds || problemIds.length === 0) return {};
    const response = await axios.post('/api/problems/favorites/batch-status', problemIds);
    return response.data;
  } catch (error) {
    console.error('批量获取收藏状态失败:', error);
    return {};
  }
} 