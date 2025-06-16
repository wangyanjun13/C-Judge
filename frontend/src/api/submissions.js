import axios from '../utils/axios'

/**
 * 提交代码
 * @param {Number} userId - 用户ID
 * @param {Number} problemId - 问题ID
 * @param {Number} exerciseId - 练习ID (可选)
 * @param {String} code - 源代码
 * @param {String} language - 编程语言
 * @returns {Promise} - 提交结果
 */
export const submitCode = async (userId, problemId, exerciseId, code, language = 'c') => {
  try {
    const response = await axios.post('/api/submissions', {
      user_id: userId,
      problem_id: problemId,
      exercise_id: exerciseId,
      code: code,
      language: language
    });
    
    return response.data;
  } catch (error) {
    console.error('提交代码失败:', error);
    throw error;
  }
}

/**
 * 获取提交记录详情
 * @param {Number} submissionId - 提交记录ID
 * @returns {Promise} - 提交记录详情
 */
export const getSubmissionDetail = async (submissionId) => {
  try {
    const response = await axios.get(`/api/submissions/${submissionId}`);
    return response.data;
  } catch (error) {
    console.error('获取提交记录详情失败:', error);
    throw error;
  }
}

/**
 * 获取提交记录列表
 * @param {Object} filters - 筛选条件
 * @param {Number} filters.userId - 用户ID
 * @param {Number} filters.problemId - 问题ID
 * @param {Number} filters.exerciseId - 练习ID
 * @returns {Promise} - 提交记录列表
 */
export const getSubmissions = async (filters = {}) => {
  try {
    const { userId, problemId, exerciseId } = filters;
    
    let url = '/api/submissions?';
    if (userId) url += `user_id=${userId}&`;
    if (problemId) url += `problem_id=${problemId}&`;
    if (exerciseId) url += `exercise_id=${exerciseId}&`;
    
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('获取提交记录列表失败:', error);
    throw error;
  }
} 