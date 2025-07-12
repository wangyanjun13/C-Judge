import axios from '../utils/axios'

/**
 * 获取学生练习列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回练习列表
 */
export const getStudentExercises = async (params = {}) => {
  try {
    const response = await axios.get('/api/exercises/student', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取学生练习列表失败:', error);
    return [];
  }
}

/**
 * 获取教师练习列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回练习列表
 */
export const getTeacherExercises = async (params = {}) => {
  try {
    const response = await axios.get('/api/exercises/teacher', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取教师练习列表失败:', error);
    return [];
  }
}

/**
 * 获取管理员练习列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回练习列表
 */
export const getAdminExercises = async (params = {}) => {
  try {
    const response = await axios.get('/api/exercises/admin', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取管理员练习列表失败:', error);
    return [];
  }
}

/**
 * 获取练习详情
 * @param {Number} exerciseId - 练习ID
 * @returns {Promise} - 返回练习详情
 */
export const getExerciseDetail = async (exerciseId) => {
  try {
    const response = await axios.get(`/api/exercises/${exerciseId}`);
    return response.data;
  } catch (error) {
    console.error('获取练习详情失败:', error);
    throw error;
  }
}

/**
 * 创建练习
 * @param {Object} exerciseData - 练习数据
 * @returns {Promise} - 返回创建的练习
 */
export const createExercise = (exerciseData) => {
  // 确保截止时间有值
  if (!exerciseData.deadline) {
    throw new Error('截止时间不能为空');
  }
  
  // 创建一个新对象，将deadline字段转换为end_time
  const apiData = {
    ...exerciseData,
    end_time: exerciseData.deadline
  };
  delete apiData.deadline;
  // 删除note字段
  delete apiData.note;
  
  return axios.post('/api/exercises', apiData)
    .then(response => {
      return response.data;
    })
    .catch(error => {
      throw error;
    });
}

/**
 * 更新练习
 * @param {Number} exerciseId - 练习ID
 * @param {Object} exerciseData - 练习更新数据
 * @returns {Promise} - 返回更新后的练习
 */
export const updateExercise = (exerciseId, exerciseData) => {
  // 创建一个新对象，将deadline字段转换为end_time
  const apiData = {...exerciseData};
  if (apiData.deadline) {
    apiData.end_time = apiData.deadline;
    delete apiData.deadline;
  }
  // 确保start_time字段被正确传递
  if (apiData.start_time) {
    apiData.start_time = apiData.start_time;
  }
  // 删除note字段
  delete apiData.note;
  
  return axios.put(`/api/exercises/${exerciseId}`, apiData);
}

/**
 * 删除练习
 * @param {Number} exerciseId - 练习ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteExercise = (exerciseId) => {
  return axios.delete(`/api/exercises/${exerciseId}`)
    .then(response => {
      return response.data;
    })
    .catch(error => {
      throw error;
    });
}

/**
 * 获取课程列表
 * @returns {Promise} - 返回课程列表
 */
export const getCourses = () => {
  return axios.get('/api/courses')
}

/**
 * 更新题目
 * @param {Number} exerciseId - 练习ID
 * @param {Number} problemId - 题目ID
 * @param {Object} problemData - 题目更新数据
 * @returns {Promise} - 返回更新后的题目
 */
export const updateProblem = (exerciseId, problemId, problemData) => {
  return axios.put(`/api/exercises/${exerciseId}/problems/${problemId}`, problemData)
    .then(response => {
      return response.data;
    })
    .catch(error => {
      throw error;
    });
}

/**
 * 从练习中移除题目
 * @param {Number} exerciseId - 练习ID
 * @param {Number} problemId - 题目ID
 * @returns {Promise} - 返回操作结果
 */
export const removeProblemFromExercise = (exerciseId, problemId) => {
  return axios.delete(`/api/exercises/${exerciseId}/problems/${problemId}`)
    .then(response => {
      return response.data;
    })
    .catch(error => {
      throw error;
    });
}

/**
 * 向练习添加题目
 * @param {Number} exerciseId - 练习ID
 * @param {Array} problems - 题目数组，包含题目信息
 * @returns {Promise} - 返回添加结果
 */
export const addProblemsToExercise = (exerciseId, problems) => {
  // 转换题目数据格式，只保留必要的字段并确保格式正确
  const problemsData = problems.map(problem => {
    // 提取时间限制的纯数字部分
    let timeLimit = "1000ms";
    if (problem.time_limit) {
      const timeMatch = /(\d+)/.exec(problem.time_limit);
      if (timeMatch) {
        timeLimit = `${timeMatch[1]}ms`;
      }
    }
    
    // 提取内存限制的纯数字部分
    let memoryLimit = "256MB";
    if (problem.memory_limit) {
      const memMatch = /(\d+)/.exec(problem.memory_limit);
      if (memMatch) {
        memoryLimit = `${memMatch[1]}MB`;
      }
    }
    
    // 确保data_path是字符串类型
    const dataPath = String(problem.data_path || "");
    
    return {
      name: problem.name || "",
      chinese_name: problem.chinese_name || problem.name || "",
      time_limit: timeLimit,
      memory_limit: memoryLimit,
      data_path: dataPath,
      category: problem.category || ""
    };
  });
  
  const requestData = { problems: problemsData };
  
  return axios.post(`/api/exercises/${exerciseId}/problems`, requestData)
    .then(response => {
      return response.data;
    })
    .catch(error => {
      throw error;
    });
}

/**
 * 清空练习中的所有题目
 * @param {Number} exerciseId - 练习ID
 * @returns {Promise} - 返回操作结果
 */
export const clearExerciseProblems = (exerciseId) => {
  return axios.delete(`/api/exercises/${exerciseId}/problems`)
    .then(response => {
      return response.data;
    })
    .catch(error => {
      throw error;
    });
}

/**
 * 获取题目详情
 * @param {Number} problemId - 题目ID
 * @returns {Promise} - 返回题目详情
 */
export const getProblemDetail = async (problemId) => {
  try {
    const response = await axios.get(`/api/problems/${problemId}`);
    return response.data;
  } catch (error) {
    console.error('获取题目详情失败:', error);
    throw error;
  }
}

/**
 * 获取练习的答题统计数据
 * @param {number} exerciseId - 练习ID
 * @param {number} classId - 班级ID（可选）
 * @param {boolean} includeSpecialUsers - 是否包含管理员和教师的答题情况（可选，默认为true）
 * @returns {Promise<Object>} - 统计数据
 */
export const getExerciseStatistics = async (exerciseId, classId = null, includeSpecialUsers = true) => {
  try {
    const params = { 
      ...(classId ? { class_id: classId } : {}),
      include_special_users: includeSpecialUsers
    };
    const response = await axios.get(`/api/exercises/${exerciseId}/statistics`, { params });
    return response.data;
  } catch (error) {
    console.error('获取练习统计数据失败:', error);
    throw error;
  }
};

/**
 * 获取练习的活跃学生列表
 * @param {number} exerciseId - 练习ID
 * @param {number} classId - 班级ID（可选）
 * @returns {Promise<Array>} - 活跃学生列表
 */
export const getExerciseActiveStudents = async (exerciseId, classId = null) => {
  try {
    const params = classId ? { class_id: classId } : {};
    const response = await axios.get(`/api/exercises/${exerciseId}/active-students`, { params });
    return response.data;
  } catch (error) {
    console.error('获取练习活跃学生数据失败:', error);
    throw error;
  }
}; 