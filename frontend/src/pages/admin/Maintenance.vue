<template>
  <div class="maintenance-container">
    <div class="tab-header">
      <div class="tab" :class="{ active: activeTab === 'problems' }" @click="activeTab = 'problems'">
        题库维护
      </div>
      <div class="tab" :class="{ active: activeTab === 'upload' }" @click="activeTab = 'upload'">
        上传题库
      </div>
      <div class="tab" :class="{ active: activeTab === 'tags' }" @click="activeTab = 'tags'">
        标签管理
      </div>
      <div class="tab" :class="{ active: activeTab === 'approval' }" @click="activeTab = 'approval'">
        标签审核
      </div>
    </div>

    <!-- 题库维护 -->
    <div v-if="activeTab === 'problems'" class="tab-content">
      <!-- 新的标签筛选布局 -->
      <div class="tags-filter-container">
        <div v-for="tagType in tagTypes" :key="tagType.id" class="tag-type-row">
          <div class="tag-type-label">{{ tagType.name }}：</div>
          <div class="tag-items">
            <div 
              class="tag-item" 
              :class="{ active: selectedTagIds[tagType.id] === '' }"
              @click="selectTag(tagType.id, '')">
              全部
            </div>
            <div 
              v-for="tag in getTagsByType(tagType.id)" 
              :key="tag.id" 
              class="tag-item"
              :class="{ active: selectedTagIds[tagType.id] === tag.id }"
              :style="{ '--tag-color': tag.tag_type_id ? `var(--tag-color-${tag.tag_type_id % 10})` : '#409eff' }"
              @click="selectTag(tagType.id, tag.id)">
              {{ tag.name }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">
        加载中...
      </div>
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      <div v-else-if="problems.length === 0" class="empty-state">
        暂无试题
      </div>
      <div v-else class="problems-table-container">
        <table class="problems-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>操作</th>
              <th>试题名称</th>
              <th>试题中文名称</th>
              <th>标签</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(problem, index) in problems" :key="problem.name">
              <td>{{ index + 1 }}</td>
              <td>
                <button @click="openTagDialog(problem)" class="btn btn-edit">打标签</button>
                <button @click="confirmDelete(problem)" class="btn btn-delete">删除</button>
              </td>
              <td>{{ problem.name }}</td>
              <td>{{ problem.chinese_name }}</td>
              <td class="tags-cell">
                <div v-if="problemTags[problem.data_path] && problemTags[problem.data_path].length > 0" class="problem-tags">
                  <template v-for="(tags, tagType) in groupTagsByType(problemTags[problem.data_path])" :key="tagType">
                    <div class="tag-group">
                      <span class="tag-type">{{ tagType }}:</span>
                      <span 
                        v-for="tag in tags" 
                        :key="tag.id" 
                        class="tag-badge"
                        :style="{ backgroundColor: getTagColor(tag.tag_type_id) }"
                      >
                        {{ tag.name }}
                      </span>
                    </div>
                  </template>
                </div>
                <span v-else class="no-tags">暂无标签</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 上传题库 -->
    <div v-if="activeTab === 'upload'" class="tab-content">
      <div class="upload-section">
        <h3>上传题库</h3>
        <p>请选择题库文件（ZIP格式）进行上传</p>
        <div class="upload-form">
          <input type="file" accept=".zip" @change="handleFileChange" />
          <button @click="uploadProblemBank" class="btn btn-primary" :disabled="!selectedFile">
            上传
          </button>
        </div>
        <div v-if="uploadStatus" class="upload-status">
          {{ uploadStatus }}
        </div>
      </div>
    </div>
    
    <!-- 标签管理 -->
    <div v-if="activeTab === 'tags'" class="tab-content">
      <div class="tags-section">
        <TagManager @update="handleTagsUpdate" />
      </div>
    </div>
    
    <!-- 标签审核 -->
    <div v-if="activeTab === 'approval'" class="tab-content">
      <div class="approval-section">
        <div class="approval-header">
          <h3>标签审核管理</h3>
          <div class="filter-tabs">
            <div 
              class="filter-tab"
              :class="{ active: approvalFilter === 'pending' }"
              @click="approvalFilter = 'pending'; loadApprovalRequests()">
              待审核 ({{ pendingCount }})
            </div>
            <div 
              class="filter-tab"
              :class="{ active: approvalFilter === 'all' }"
              @click="approvalFilter = 'all'; loadApprovalRequests()">
              全部
            </div>
          </div>
        </div>
        
        <div v-if="approvalLoading" class="loading">
          加载中...
        </div>
        
        <div v-else-if="approvalRequests.length === 0" class="empty-state">
          暂无审核请求
        </div>
        
        <div v-else class="approval-list">
          <div 
            v-for="request in approvalRequests" 
            :key="request.id" 
            class="approval-item"
            :class="{ 'pending': request.status === 'pending' }">
            
            <div class="approval-header-info">
              <div class="request-info">
                <div class="problem-info-section">
                  <div class="problem-names">
                    <span class="problem-name-cn">{{ getProblemChineseName(request.problem_data_path) }}</span>
                    <span class="problem-name-en">{{ request.problem_data_path.split('/').pop() }}</span>
                  </div>
                </div>
                <div class="meta-info">
                <span class="status-badge" :class="request.status">
                  {{ getStatusText(request.status) }}
                </span>
                <span class="requestor">
                  申请人: {{ request.requestor?.real_name || request.requestor?.username || '未知' }}
                </span>
                <span class="request-time">
                  {{ formatTime(request.created_at) }}
                </span>
                </div>
              </div>
            </div>
            
            <div class="approval-content">
              <div class="request-tags">
                <strong>申请标签:</strong>
                <div class="tag-list">
                  <span 
                    v-for="tagId in request.tag_ids" 
                    :key="tagId"
                    class="tag-badge"
                    :style="{ backgroundColor: getTagColorById(tagId) }">
                    {{ getTagNameById(tagId) }}
                  </span>
                </div>
              </div>
              
              <div v-if="request.request_message" class="request-message">
                <strong>申请说明:</strong>
                <p>{{ request.request_message }}</p>
              </div>
              
              <div v-if="request.review_message" class="review-message">
                <strong>审核意见:</strong>
                <p>{{ request.review_message }}</p>
                <span class="reviewer">
                  审核人: {{ request.reviewer?.real_name || request.reviewer?.username || '未知' }}
                  ({{ formatTime(request.reviewed_at) }})
                </span>
              </div>
              
              <div v-if="request.status === 'pending'" class="approval-actions">
                <button @click="openReviewDialog(request)" class="btn btn-primary">
                  审核
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 审核对话框：使用ProblemTagDialog -->
    <div v-if="showReviewDialog" class="modal-overlay" @click="closeReviewDialog">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h3>审核标签申请</h3>
          <button @click="closeReviewDialog" class="close-btn">✕</button>
        </div>
        <div class="modal-content">
          <ProblemTagDialog 
            v-if="selectedProblemForReview"
            :problemInfo="selectedProblemForReview"
            :reviewMode="true"
            :reviewRequest="currentRequest"
            @cancel="closeReviewDialog"
            @reviewed="handleReviewCompleted"
          />
        </div>
      </div>
    </div>
    
    <!-- 打标签对话框 -->
    <div v-if="showTagDialog" class="modal-overlay" @click="closeTagDialog">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h3>为"{{ selectedProblem?.chinese_name || selectedProblem?.name }}"设置标签</h3>
          <button @click="closeTagDialog" class="close-btn">✕</button>
        </div>
        <div class="modal-content">
          <ProblemTagDialog 
            :problemInfo="selectedProblem"
            @cancel="closeTagDialog"
            @saved="handleTagsSaved"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getProblemCategories, getProblemsByCategory, updateProblem as updateProblemAPI, deleteProblem as deleteProblemAPI } from '../../api/problems';
import { useRoute } from 'vue-router';
import { logUserOperation, OperationType } from '../../utils/logger';
import TagManager from '../../components/TagManager.vue';
import ProblemTagDialog from '../../components/ProblemTagDialog.vue';
import { getTagTypes, getTags, getProblemTags, setProblemTags, getBatchProblemTags, getApprovalRequests, approveTagRequest } from '../../api/tags';
import enhancedProblemsAPI from '../../api/enhancedProblems';

// 获取路由参数
const route = useRoute();

// 状态变量
const activeTab = ref('problems');
const categories = ref([]);
const selectedCategory = ref('');
const problems = ref([]);
const loading = ref(false);
const error = ref(null);
const selectedFile = ref(null);
const uploadStatus = ref('');

// 打标签相关状态
const showTagDialog = ref(false);
const selectedProblem = ref(null);
const selectedTagsForProblem = ref([]);

// 标签相关状态
const tagTypes = ref([]);
const allTags = ref([]); // 存储所有标签
const selectedTagIds = ref({}); // 存储每种标签类型的选中值
const problemTags = ref({}); // 存储每个问题的标签
const tagTypeMap = ref({}); // 存储标签类型ID到名称的映射

// 审核相关状态
const approvalRequests = ref([]);
const approvalLoading = ref(false);
const approvalFilter = ref('pending');
const pendingCount = ref(0);
const showReviewDialog = ref(false);
const currentRequest = ref(null);
const selectedProblemForReview = ref(null);

// 选择标签
const selectTag = (tagTypeId, tagId) => {
  selectedTagIds.value[tagTypeId] = tagId;
  loadProblems();
};

// 加载所有数据（优化版本）
const loadAllData = async (options = {}) => {
  loading.value = true;
  error.value = null;
  
  try {
    console.log('开始加载所有数据（优化版本）');
    
    // 构建过滤选项
    const filterOptions = {};
    
    // 查找第一个被选中的标签
    for (const tagTypeId in selectedTagIds.value) {
      if (selectedTagIds.value[tagTypeId]) {
        filterOptions.tagId = selectedTagIds.value[tagTypeId];
        break; // 只使用第一个被选中的标签进行过滤
      }
    }
    
    // 如果有强制刷新选项，传递给API
    if (options.forceRefresh) {
      filterOptions.forceRefresh = true;
    }
    
    // 一次性获取所有数据
    const allData = await enhancedProblemsAPI.getAllData(filterOptions);
    
    // 更新状态
    categories.value = allData.categories;
    problems.value = allData.problems;
    tagTypes.value = allData.tagTypes;
    allTags.value = allData.tags;
    problemTags.value = allData.problemTags;
    
    // 初始化selectedTagIds对象和tagTypeMap
    tagTypes.value.forEach(tagType => {
      if (!(tagType.id in selectedTagIds.value)) {
        selectedTagIds.value[tagType.id] = '';
      }
      tagTypeMap.value[tagType.id] = tagType.name;
    });
    
    console.log('所有数据加载完成:', {
      categories: categories.value.length,
      problems: problems.value.length,
      tagTypes: tagTypes.value.length,
      tags: allTags.value.length,
      problemTags: Object.keys(problemTags.value).length
    });
    
  } catch (err) {
    console.error('加载所有数据失败:', err);
    error.value = '加载数据失败';
    ElMessage.error('加载数据失败');
  } finally {
    loading.value = false;
  }
};

// 兼容的加载分类函数（已被loadAllData替代，但保留用于向后兼容）
const loadCategories = async () => {
  try {
    categories.value = await enhancedProblemsAPI.getCategories();
    if (categories.value.length === 0) {
      ElMessage.warning('未找到题库分类，请确保题库目录已正确配置');
    }
  } catch (err) {
    console.error('加载题库分类失败:', err);
    ElMessage.error('加载题库分类失败');
  }
};

// 兼容的加载标签函数（已被loadAllData替代，但保留用于向后兼容）
const loadTags = async () => {
  try {
    const tagsData = await enhancedProblemsAPI.getTagsData();
    tagTypes.value = tagsData.tagTypes;
    allTags.value = tagsData.tags;
    
    // 初始化selectedTagIds对象和tagTypeMap
    tagTypes.value.forEach(tagType => {
      if (!(tagType.id in selectedTagIds.value)) {
      selectedTagIds.value[tagType.id] = '';
      }
      tagTypeMap.value[tagType.id] = tagType.name;
    });
  } catch (err) {
    console.error('加载标签失败:', err);
    ElMessage.error('加载标签失败');
  }
};

// 根据标签类型获取标签
const getTagsByType = (tagTypeId) => {
  return allTags.value.filter(tag => tag.tag_type_id === tagTypeId);
};

// 加载试题列表（优化版本）
const loadProblems = async () => {
  // 直接调用loadAllData，因为它已经包含了过滤逻辑
  await loadAllData();
};
    
// 兼容的加载问题标签函数（已被loadAllData替代，但保留用于向后兼容）
const loadProblemTags = async () => {
  if (problems.value.length === 0) return;
  
  try {
    // 收集所有问题的data_path
    const allPaths = problems.value
      .filter(problem => problem.data_path)
      .map(problem => problem.data_path);
    
    if (allPaths.length === 0) return;
    
    // 使用增强API批量获取所有问题的标签
    console.log(`批量获取${allPaths.length}个问题的标签`);
    const encodedPaths = allPaths.map(path => encodeURIComponent(path));
    const batchTags = await enhancedProblemsAPI.getBatchProblemTags(encodedPaths);
    
    // 为所有问题设置标签数据，包括没有标签的题目
    for (const problem of problems.value) {
      if (problem.data_path) {
        const encodedPath = encodeURIComponent(problem.data_path);
        // 关键修复：即使没有标签也要设置为空数组，而不是跳过
        problemTags.value[problem.data_path] = batchTags[encodedPath] || [];
      }
    }
  } catch (err) {
    console.error(`批量获取问题标签失败:`, err);
  }
};

// 根据标签类型分组标签
const groupTagsByType = (tags) => {
  const grouped = {};
  
  if (!tags) return grouped;
  
  tags.forEach(tag => {
    const typeName = tag.tag_type_id ? (tagTypeMap.value[tag.tag_type_id] || '未分类') : '未分类';
    if (!grouped[typeName]) {
      grouped[typeName] = [];
    }
    grouped[typeName].push(tag);
  });
  
  return grouped;
};

// 根据标签类型生成颜色
const getTagColor = (tagTypeId) => {
  // 预定义一组好看的颜色
  const colors = [
    '#409eff', // 蓝色
    '#67c23a', // 绿色
    '#e6a23c', // 橙色
    '#f56c6c', // 红色
    '#909399', // 灰色
    '#9c27b0', // 紫色
    '#2196f3', // 浅蓝
    '#ff9800', // 橙黄
    '#795548', // 棕色
    '#607d8b'  // 蓝灰
  ];
  
  // 使用标签类型ID作为索引来选择颜色
  const index = ((tagTypeId || 0) % colors.length);
  return colors[index];
};

// 打开标签对话框
const openTagDialog = (problem) => {
    if (!problem.data_path) {
      console.error('问题缺少data_path字段:', problem);
      ElMessage.error('无法获取问题标识符');
      return;
    }
  selectedProblem.value = problem;
  showTagDialog.value = true;
};

// 关闭标签对话框
const closeTagDialog = () => {
  showTagDialog.value = false;
  selectedProblem.value = null;
  selectedTagsForProblem.value = [];
};

// 处理标签保存成功
const handleTagsSaved = (selectedTagIds) => {
    logUserOperation(OperationType.UPDATE_PROBLEM_TAGS, `试题: ${selectedProblem.value.chinese_name}`);
    
    // 更新本地标签缓存
  if (selectedTagIds.length > 0) {
    const selectedTags = allTags.value.filter(tag => selectedTagIds.includes(tag.id));
      problemTags.value[selectedProblem.value.data_path] = selectedTags;
    } else {
      delete problemTags.value[selectedProblem.value.data_path];
    }
    
    closeTagDialog();
};

// 确认删除试题
const confirmDelete = (problem) => {
  ElMessageBox.confirm(`确定要删除试题 "${problem.chinese_name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteProblem(problem);
  }).catch(() => {
    // 取消删除
  });
};

// 删除试题
const deleteProblem = async (problem) => {
  try {
    await deleteProblemAPI(problem.data_path);
    ElMessage.success('删除试题成功');
    logUserOperation(OperationType.DELETE_PROBLEM, `试题: ${problem.chinese_name}`);
    loadProblems(); // 重新加载试题列表
  } catch (err) {
    console.error('删除试题失败:', err);
    ElMessage.error('删除试题失败');
  }
};

// 处理文件选择
const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
  uploadStatus.value = '';
};

// 上传题库
const uploadProblemBank = () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件');
    return;
  }
  
  uploadStatus.value = '上传中...';
  ElMessage.info('上传题库功能正在开发中...');
  logUserOperation(OperationType.UPLOAD_PROBLEM_BANK, `文件: ${selectedFile.value.name}`);
  // 此处实现文件上传逻辑
};

// 处理标签更新
const handleTagsUpdate = async () => {
  ElMessage.success('标签更新成功');
  // 使用增强API的缓存失效功能，然后重新加载所有数据
  enhancedProblemsAPI.invalidateAfterUpdate('tag');
  await loadAllData({ forceRefresh: true });
};

// 审核相关方法
const loadApprovalRequests = async () => {
  approvalLoading.value = true;
  try {
    const status = approvalFilter.value === 'pending' ? 'pending' : null;
    const requests = await getApprovalRequests(status);
    
    // 用户信息已在后端处理，无需额外处理
    
    approvalRequests.value = requests;
    pendingCount.value = requests.filter(r => r.status === 'pending').length;
  } catch (error) {
    console.error('加载审核请求失败:', error);
    ElMessage.error('加载审核请求失败');
  } finally {
    approvalLoading.value = false;
  }
};

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待审核',
    'approved': '已批准',
    'rejected': '已拒绝'
  };
  return statusMap[status] || '未知';
};

const formatTime = (timeStr) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  return date.toLocaleString('zh-CN');
};

const getTagNameById = (tagId) => {
  const tag = allTags.value.find(t => t.id === tagId);
  return tag ? tag.name : '未知标签';
};

const getTagColorById = (tagId) => {
  const tag = allTags.value.find(t => t.id === tagId);
  return tag ? getTagColor(tag.tag_type_id) : '#909399';
};

const openReviewDialog = (request) => {
  currentRequest.value = request;
  // 构造题目信息对象，供ProblemTagDialog使用
  selectedProblemForReview.value = {
    name: request.problem_data_path.split('/').pop(),
    chinese_name: getProblemChineseName(request.problem_data_path),
    data_path: request.problem_data_path,
    // 添加其他可能需要的字段
    time_limit: '1000ms',
    memory_limit: '256M'
  };
  showReviewDialog.value = true;
};

const closeReviewDialog = () => {
  showReviewDialog.value = false;
  currentRequest.value = null;
  selectedProblemForReview.value = null;
};

const handleReviewCompleted = async (reviewResult) => {
  try {
    await approveTagRequest(currentRequest.value.id, {
      status: reviewResult.status,
      review_message: reviewResult.review_message || null
    });
    
    ElMessage.success(`标签申请已${reviewResult.status === 'approved' ? '批准' : '拒绝'}`);
    closeReviewDialog();
    await loadApprovalRequests();
    
    // 如果批准，重新加载题目列表
    if (reviewResult.status === 'approved') {
      await loadProblems();
    }
  } catch (error) {
    console.error('审核失败:', error);
    ElMessage.error('审核失败');
  }
};

// 获取题目中文名称
const getProblemChineseName = (problemPath) => {
  // 从problems列表中查找对应的题目信息
  const problem = problems.value.find(p => p.data_path === problemPath);
  return problem?.chinese_name || '未知题目';
};

// 监听路由参数变化
watch(() => route.query.tab, (newTab) => {
  if (newTab === 'upload') {
    activeTab.value = 'upload';
  } else if (newTab === 'tags') {
    activeTab.value = 'tags';
  } else if (newTab === 'approval') {
    activeTab.value = 'approval';
    loadApprovalRequests();
  } else {
    activeTab.value = 'problems';
  }
}, { immediate: true });

// 监听activeTab变化，当切换到审核页面时加载数据
watch(activeTab, (newTab) => {
  if (newTab === 'approval') {
    loadApprovalRequests();
  }
});

// 页面加载时获取所有数据（优化版本）
onMounted(async () => {
  // 预加载基础数据到缓存
  await enhancedProblemsAPI.preloadData({ preloadAllProblems: true });
  
  // 加载所有数据到页面
  await loadAllData();
  
  // 记录优化后的加载完成
  console.log('页面数据加载完成，使用了优化的API');
});
</script>

<style scoped>
.maintenance-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 60px;
  --tag-color-0: #409eff; /* 蓝色 */
  --tag-color-1: #67c23a; /* 绿色 */
  --tag-color-2: #e6a23c; /* 橙色 */
  --tag-color-3: #f56c6c; /* 红色 */
  --tag-color-4: #909399; /* 灰色 */
  --tag-color-5: #9c27b0; /* 紫色 */
  --tag-color-6: #2196f3; /* 浅蓝 */
  --tag-color-7: #ff9800; /* 橙黄 */
  --tag-color-8: #795548; /* 棕色 */
  --tag-color-9: #607d8b; /* 蓝灰 */
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #dcdfe6;
  margin-bottom: 20px;
}

.tab {
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-right: 20px;
}

.tab.active {
  border-bottom-color: #409eff;
  color: #409eff;
}

.tab-content {
  padding: 10px 0;
}

/* 新增标签筛选布局样式 */
.tags-filter-container {
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  background-color: #f5f7fa;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.tag-type-row {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.tag-type-row:last-child {
  margin-bottom: 0;
}

.tag-type-label {
  width: 100px;
  text-align: right;
  padding-right: 15px;
  padding-top: 6px;
  font-weight: 500;
  color: #606266;
  flex-shrink: 0;
}

.tag-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex-grow: 1;
}

.tag-item {
  padding: 6px 12px;
  border-radius: 4px;
  background-color: #ffffff;
  border: 1px solid #dcdfe6;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  user-select: none;
}

.tag-item:hover {
  background-color: #ecf5ff;
  color: var(--primary-color);
  border-color: #c6e2ff;
}

.tag-item.active {
  color: #ffffff;
  background-color: var(--tag-color, var(--primary-color));
  border-color: var(--tag-color, var(--primary-color));
}

.loading, .error, .empty-state {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.error {
  color: #f56c6c;
}

.problems-table-container {
  overflow-x: auto;
}

.problems-table {
  width: 100%;
  border-collapse: collapse;
}

.problems-table th, .problems-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.problems-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.tags-cell {
  max-width: 500px; /* 增加标签单元格宽度 */
}

.problem-tags {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
}

.tag-type {
  font-weight: 500;
  font-size: 0.9em;
  color: #606266;
}

.tag-badge {
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-size: 0.85em;
  white-space: nowrap;
}

.no-tags {
  color: #909399;
  font-size: 0.9em;
  font-style: italic;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-edit {
  background-color: #67c23a;
  color: white;
}

.btn-delete {
  background-color: #f56c6c;
  color: white;
}

.upload-section {
  max-width: 600px;
  margin: 0 auto;
}

.upload-form {
  margin: 20px 0;
  display: flex;
  align-items: center;
}

.upload-form input {
  flex-grow: 1;
  margin-right: 10px;
}

.upload-status {
  margin-top: 10px;
  color: #409eff;
}

/* 打标签对话框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.large-modal {
  width: 1200px;
  max-width: 95vw;
  max-height: 90vh;
  overflow: hidden;
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
}

.tag-dialog-content {
  overflow-y: auto;
  max-height: 60vh;
  padding-right: 10px;
}

.tag-type-section {
  margin-bottom: 20px;
}

.tag-type-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #606266;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-list .tag-item {
  padding: 6px 12px;
  background-color: #f4f4f5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.tag-list .tag-item:hover {
  background-color: #e9e9eb;
}

.tag-list .tag-item.selected {
  background-color: #409eff;
  color: white;
}

.dialog-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 审核相关样式 */
.approval-section {
  max-width: 100%;
}

.approval-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.approval-header h3 {
  margin: 0;
  color: #303133;
}

.filter-tabs {
  display: flex;
  gap: 10px;
}

.filter-tab {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  background-color: #fff;
  color: #606266;
  transition: all 0.3s;
}

.filter-tab:hover {
  border-color: #409eff;
  color: #409eff;
}

.filter-tab.active {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.approval-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.approval-item {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.approval-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #e6a23c, #f5b041);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.approval-item.pending::before {
  opacity: 1;
}

.approval-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.approval-item.pending {
  border-left: none;
  background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%);
}

.approval-header-info {
  margin-bottom: 12px;
}

.request-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.problem-info-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}

.problem-names {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.problem-name-cn {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
  line-height: 1.3;
}

.problem-name-en {
  font-size: 13px;
  color: #909399;
  font-family: 'Courier New', monospace;
}

.btn-view-problem {
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-view-problem:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.problem-name {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background-color: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.status-badge.approved {
  background-color: #f0f9ff;
  color: #67c23a;
  border: 1px solid #b3d8ff;
}

.status-badge.rejected {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
}

.requestor, .request-time {
  color: #909399;
  font-size: 14px;
}

.approval-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.request-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.request-tags strong {
  color: #606266;
  font-size: 14px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-badge {
  padding: 6px 12px;
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.tag-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.request-message, .review-message {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.request-message strong, .review-message strong {
  color: #606266;
  font-size: 14px;
}

.request-message p, .review-message p {
  margin: 0;
  color: #303133;
  line-height: 1.5;
  background-color: #f8f9fa;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.reviewer {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

.approval-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f2f5;
}

.approval-actions .btn {
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.approval-actions .btn-primary {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.approval-actions .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

/* 查看题目详情对话框样式 */
.modal-overlay .modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px 8px 0 0;
}

.modal-overlay .modal .modal-header h3 {
  margin: 0;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.modal-overlay .modal .close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: white;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.modal-overlay .modal .close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.modal-overlay .modal .modal-content {
  padding: 0;
  overflow: hidden;
}
</style> 