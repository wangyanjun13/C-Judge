import axios from '../utils/axios'

/**
 * 提交代码
 * @param {Number} userId - 用户ID
 * @param {Number} problemId - 题目ID
 * @param {Number} exerciseId - 练习ID（可选）
 * @param {String} code - 代码内容
 * @param {String} language - 编程语言
 * @returns {Promise} - 返回提交结果
 */
export const submitCode = (userId, problemId, exerciseId, code, language) => {
  const data = {
    user_id: userId,
    problem_id: problemId,
    exercise_id: exerciseId,
    code: code,
    language: language
  };
  
  return axios.post('/api/submissions', data)
    .then(response => {
      return response.data;
    })
    .catch(error => {
      console.error('提交代码失败:', error);
      // 提取错误信息
      const errorMsg = error.response?.data?.detail || '提交失败，请稍后重试';
      throw new Error(errorMsg);
    });
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

/**
 * 获取题目在班级中的排名
 * @param {number} problemId - 题目ID
 * @param {number} exerciseId - 练习ID
 * @param {number} classId - 班级ID (可选)
 * @returns {Promise<Object>} - 排名数据
 */
export const getProblemRanking = async (problemId, exerciseId, classId = null) => {
  try {
    let url = `/api/submissions/problem-ranking/${problemId}?exercise_id=${exerciseId}`;
    if (classId) {
      url += `&class_id=${classId}`;
    }
    
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('获取题目排名失败:', error);
    throw error;
  }
}; 

/**
 * 获取当前用户的所有答题记录
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回记录数量限制
 * @param {number} params.offset - 偏移量，用于分页
 * @param {string} params.sort - 排序方式：asc（升序）或desc（降序）
 * @returns {Promise<Array>} - 答题记录列表，包含题目、练习、课程、班级名称
 */
export const getMySubmissions = async (params = {}) => {
  try {
    const response = await axios.get('/api/submissions/my-submissions', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取我的答题记录失败:', error);
    throw error;
  }
}; 

/**
 * 获取所有提交记录（管理员/教师权限）
 * @param {Object} params - 查询参数
 * @returns {Promise<Array>} - 提交记录列表
 */
export const getAllSubmissions = async (params = {}) => {
  try {
    const response = await axios.get('/api/submissions/', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取所有提交记录失败:', error);
    throw error;
  }
};

/**
 * 获取学生列表（管理员/教师权限）
 * @param {number} classId - 班级ID（可选）
 * @returns {Promise<Array>} - 学生列表
 */
export const getStudents = async (classId = null) => {
  try {
    const params = classId ? { class_id: classId } : {};
    const response = await axios.get('/api/users/students', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取学生列表失败:', error);
    throw error;
  }
}; 