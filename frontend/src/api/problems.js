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
 * @param {Number} options.tagTypeId - 按标签类型ID过滤（可选）
 * @returns {Promise} - 返回试题列表
 */
export const getProblemsByCategory = async (categoryPath, options = {}) => {
  try {
    console.log('请求分类下的试题:', categoryPath);
    const params = {};
    
    // 添加过滤参数
    if (options.tagId) {
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