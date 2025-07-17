import axios from "../utils/axios"

/**
 * 获取所有标签类型
 * @returns {Promise} - 返回标签类型列表
 */
export const getTagTypes = async () => {
  try {
    const response = await axios.get("/api/tags/types");
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error("获取标签类型失败:", error);
    return [];
  }
}

/**
 * 创建标签类型
 * @param {Object} tagTypeData - 标签类型数据
 * @returns {Promise} - 返回创建的标签类型
 */
export const createTagType = async (tagTypeData) => {
  try {
    const response = await axios.post('/api/tags/types', tagTypeData);
    return response.data;
  } catch (error) {
    console.error('创建标签类型失败:', error);
    throw error;
  }
}

/**
 * 更新标签类型
 * @param {Number} tagTypeId - 标签类型ID
 * @param {Object} tagTypeData - 标签类型更新数据
 * @returns {Promise} - 返回更新后的标签类型
 */
export const updateTagType = async (tagTypeId, tagTypeData) => {
  try {
    const response = await axios.put(`/api/tags/types/${tagTypeId}`, tagTypeData);
    return response.data;
  } catch (error) {
    console.error('更新标签类型失败:', error);
    throw error;
  }
}

/**
 * 删除标签类型
 * @param {Number} tagTypeId - 标签类型ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteTagType = async (tagTypeId) => {
  try {
    const response = await axios.delete(`/api/tags/types/${tagTypeId}`);
    return response.data;
  } catch (error) {
    console.error('删除标签类型失败:', error);
    throw error;
  }
}

/**
 * 获取所有标签
 * @param {Number} tagTypeId - 标签类型ID（可选）
 * @returns {Promise} - 返回标签列表
 */
export const getTags = async (tagTypeId = null) => {
  try {
    const params = tagTypeId ? { tag_type_id: tagTypeId } : {};
    const response = await axios.get('/api/tags', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取标签失败:', error);
    return [];
  }
}

/**
 * 创建标签
 * @param {Object} tagData - 标签数据
 * @returns {Promise} - 返回创建的标签
 */
export const createTag = async (tagData) => {
  try {
    const response = await axios.post('/api/tags', tagData);
    return response.data;
  } catch (error) {
    console.error('创建标签失败:', error);
    throw error;
  }
}

/**
 * 更新标签
 * @param {Number} tagId - 标签ID
 * @param {Object} tagData - 标签更新数据
 * @returns {Promise} - 返回更新后的标签
 */
export const updateTag = async (tagId, tagData) => {
  try {
    const response = await axios.put(`/api/tags/${tagId}`, tagData);
    return response.data;
  } catch (error) {
    console.error('更新标签失败:', error);
    throw error;
  }
}

/**
 * 删除标签
 * @param {Number} tagId - 标签ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteTag = async (tagId) => {
  try {
    const response = await axios.delete(`/api/tags/${tagId}`);
    return response.data;
  } catch (error) {
    console.error('删除标签失败:', error);
    throw error;
  }
}

/**
 * 获取问题的标签
 * @param {String} problemPath - 问题路径
 * @returns {Promise} - 返回标签列表
 */
export const getProblemTags = async (problemPath) => {
  try {
    const encodedPath = encodeURIComponent(problemPath);
    const response = await axios.get(`/api/tags/problem/${encodedPath}`);
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取问题标签失败:', error);
    return [];
  }
}

/**
 * 为问题添加标签
 * @param {String} problemPath - 问题路径
 * @param {Number} tagId - 标签ID
 * @returns {Promise} - 返回操作结果
 */
export const addTagToProblem = async (problemPath, tagId) => {
  try {
    const encodedPath = encodeURIComponent(problemPath);
    const response = await axios.post(`/api/tags/problem/${encodedPath}/tag/${tagId}`);
    return response.data;
  } catch (error) {
    console.error('添加标签到问题失败:', error);
    throw error;
  }
}

/**
 * 从问题中移除标签
 * @param {String} problemPath - 问题路径
 * @param {Number} tagId - 标签ID
 * @returns {Promise} - 返回操作结果
 */
export const removeTagFromProblem = async (problemPath, tagId) => {
  try {
    const encodedPath = encodeURIComponent(problemPath);
    const response = await axios.delete(`/api/tags/problem/${encodedPath}/tag/${tagId}`);
    return response.data;
  } catch (error) {
    console.error('从问题中移除标签失败:', error);
    throw error;
  }
}

/**
 * 设置问题的标签
 * @param {String} problemPath - 问题路径
 * @param {Array} tagIds - 标签ID数组
 * @returns {Promise} - 返回操作结果
 */
export const setProblemTags = async (problemPath, tagIds) => {
  try {
    const encodedPath = encodeURIComponent(problemPath);
    const response = await axios.put(`/api/tags/problem/${encodedPath}/tags`, tagIds);
    return response.data;
  } catch (error) {
    console.error('设置问题标签失败:', error);
    throw error;
  }
}

/**
 * 批量获取多个问题的标签
 * @param {Array} problemPaths - 问题路径数组
 * @returns {Promise} - 返回每个问题的标签映射对象
 */
export const getBatchProblemTags = async (problemPaths) => {
  try {
    // 如果路径数组为空，直接返回空对象
    if (!problemPaths || problemPaths.length === 0) {
      return {};
    }
    
    // 每批处理的最大路径数
    const BATCH_SIZE = 30;
    
    // 如果路径数量超过批处理大小，则分批处理
    if (problemPaths.length > BATCH_SIZE) {
      console.log(`路径数量(${problemPaths.length})超过批处理大小(${BATCH_SIZE})，进行分批处理`);
      
      // 将路径数组分割成多个批次
      const batches = [];
      for (let i = 0; i < problemPaths.length; i += BATCH_SIZE) {
        batches.push(problemPaths.slice(i, i + BATCH_SIZE));
      }
      
      // 合并所有批次的结果
      let result = {};
      for (let i = 0; i < batches.length; i++) {
        console.log(`处理第 ${i+1}/${batches.length} 批路径，数量: ${batches[i].length}`);
        const batchResult = await getBatchProblemTags(batches[i]);
        result = { ...result, ...batchResult };
      }
      
      return result;
    }
    
    // 正常处理单批路径
    const response = await axios.post('/api/tags/problems/batch-tags', problemPaths);
    return response.data;
  } catch (error) {
    console.error('批量获取问题标签失败:', error);
    return {};
  }
}