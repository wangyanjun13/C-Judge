<template>
  <div class="problem-tag-dialog">
    <!-- 关闭按钮 -->
    <div class="close-button" @click="handleCancel">
      <span>✕</span>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    <div v-else class="dialog-content">
      <!-- 左侧：题目内容和测试用例 -->
      <div class="problem-content">
        <h3>{{ problem.chinese_name || problem.name }}</h3>
        <div class="problem-html" v-html="problem.html_content"></div>
        
        <!-- 测试用例部分 -->
        <div v-if="testCases.length > 0" class="testcases-section">
          <h4>📝 测试用例</h4>
          <div class="testcases-list">
            <div v-for="testCase in testCases" :key="testCase.test_case" class="testcase-item">
              <div class="testcase-header">
                <span class="testcase-number">测试用例 {{ testCase.test_case }}</span>
              </div>
              <div class="testcase-content">
                <div class="input-section">
                  <h5>📥 输入</h5>
                  <pre class="testcase-data">{{ testCase.input || '（无输入数据）' }}</pre>
                </div>
                <div class="output-section">
                  <h5>📤 期望输出</h5>
                  <pre class="testcase-data">{{ testCase.output || '（无输出数据）' }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 参考代码部分 -->
        <div v-if="referenceAnswer" class="reference-answer-section">
          <h4>💻 参考代码</h4>
          <div class="reference-answer-content">
            <pre class="reference-code">{{ referenceAnswer }}</pre>
          </div>
        </div>
        <div v-else class="reference-answer-section">
          <h4>💻 参考代码</h4>
          <div class="reference-answer-content">
            <p class="no-reference">暂无参考代码</p>
          </div>
        </div>
      </div>
      
      <!-- 右侧：标签选择、显示或审核 -->
      <div class="tags-section">
        <h4>{{ reviewMode ? '标签审核' : (viewOnly ? '题目标签' : '设置标签') }}</h4>
        
        <!-- 审核模式：显示申请的标签和审核选项 -->
        <div v-if="reviewMode" class="review-mode-display">
          <div class="applied-tags-section">
            <h5>申请的标签：</h5>
            <div class="applied-tags">
              <span 
                v-for="tagId in reviewRequest?.tag_ids" 
                :key="tagId"
                class="tag-badge applied-tag"
                :style="{ backgroundColor: getTagColorById(tagId) }">
                {{ getTagNameById(tagId) }}
              </span>
            </div>
          </div>
          
          <div v-if="reviewRequest?.request_message" class="request-reason">
            <h5>申请理由：</h5>
            <p>{{ reviewRequest.request_message }}</p>
          </div>
          
          <div class="review-form">
            <h5>审核决定：</h5>
            <div class="review-options">
              <label class="review-option">
                <input type="radio" v-model="reviewData.status" value="approved" />
                <span class="option-text approve">✅ 批准</span>
              </label>
              <label class="review-option">
                <input type="radio" v-model="reviewData.status" value="rejected" />
                <span class="option-text reject">❌ 拒绝</span>
              </label>
            </div>
            
            <div class="review-message-input">
              <label for="review-message">审核意见（可选）：</label>
              <textarea 
                id="review-message"
                v-model="reviewData.review_message" 
                placeholder="请输入审核意见..."
                rows="3">
              </textarea>
            </div>
          </div>
        </div>
        
        <!-- 只查看模式：显示现有标签 -->
        <div v-else-if="viewOnly" class="existing-tags-display">
          <div v-if="selectedTags.length > 0" class="existing-tags">
            <div v-for="tagType in tagTypes" :key="tagType.id" class="tag-type-section">
              <template v-if="getTagsByType(tagType.id).some(tag => selectedTags.includes(tag.id))">
                <h5>{{ tagType.name }}</h5>
                <div class="tag-list">
                  <div 
                    v-for="tag in getTagsByType(tagType.id)" 
                    :key="tag.id" 
                    v-show="selectedTags.includes(tag.id)"
                    class="tag-item selected"
                  >
                    {{ tag.name }}
                  </div>
                </div>
              </template>
            </div>
          </div>
          <div v-else class="no-tags-display">
            <p>该题目暂未设置标签</p>
          </div>
        </div>
        
        <!-- 编辑模式：标签选择 -->
        <div v-else class="tag-selection">
          <div v-for="tagType in tagTypes" :key="tagType.id" class="tag-type-section">
            <h5>{{ tagType.name }}</h5>
            <div class="tag-list">
              <div 
                v-for="tag in getTagsByType(tagType.id)" 
                :key="tag.id" 
                class="tag-item"
                :class="{ selected: selectedTags.includes(tag.id) }"
                @click="toggleTag(tag.id)"
              >
                {{ tag.name }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="dialog-actions">
          <button @click="handleCancel" class="btn btn-cancel">
            {{ viewOnly ? '关闭' : '取消' }}
          </button>
          <button v-if="reviewMode" @click="submitReview" class="btn btn-primary" :disabled="!reviewData.status">
            {{ reviewData.status ? '提交审核' : '请先选择审核结果' }}
          </button>
          <button v-else-if="!viewOnly && !reviewMode" @click="saveTags" class="btn btn-primary">
            {{ isAdmin ? '直接保存' : '提交审核' }}
          </button>
        </div>
        
        <!-- 审核请求说明 -->
        <div v-if="!isAdmin && !viewOnly && !reviewMode" class="request-message">
          <label for="request-message">申请说明（可选）：</label>
          <textarea 
            id="request-message"
            v-model="requestMessage" 
            placeholder="请简要说明为什么要为此题目添加这些标签..."
            rows="3">
          </textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, getCurrentInstance, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getProblemDetail } from '../api/exercises';
import { getTagTypes, getTags, getProblemTags, setProblemTags, createTagApprovalRequest, approveTagRequest } from '../api/tags';
import { getProblemReferenceAnswer } from '../api/problems';
import { useAuthStore } from '../store/auth';

const props = defineProps({
  problemInfo: {
    type: Object,
    required: true
  },
  viewOnly: {
    type: Boolean,
    default: false
  },
  reviewMode: {
    type: Boolean,
    default: false
  },
  reviewRequest: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['cancel', 'saved', 'reviewed']);

const authStore = useAuthStore();
const problem = ref({});
const loading = ref(true);
const error = ref(null);
const tagTypes = ref([]);
const allTags = ref([]);
const selectedTags = ref([]);
const requestMessage = ref('');
const testCases = ref([]);
const referenceAnswer = ref('');
  
// 审核相关状态
const reviewData = ref({
  status: '',
  review_message: ''
});

// 计算属性：判断当前用户是否为管理员
const isAdmin = computed(() => {
  return authStore.isAdmin;
});

// 根据标签类型获取标签
const getTagsByType = (tagTypeId) => {
  return allTags.value.filter(tag => tag.tag_type_id === tagTypeId);
};

// 切换标签选择状态
const toggleTag = (tagId) => {
  const index = selectedTags.value.indexOf(tagId);
  if (index === -1) {
    selectedTags.value.push(tagId);
  } else {
    selectedTags.value.splice(index, 1);
  }
};

// 审核功能相关方法
const getTagNameById = (tagId) => {
  const tag = allTags.value.find(t => t.id === tagId);
  return tag ? tag.name : '未知标签';
};

const getTagColorById = (tagId) => {
  const tag = allTags.value.find(t => t.id === tagId);
  return tag ? getTagColor(tag.tag_type_id) : '#909399';
};

const getTagColor = (tagTypeId) => {
  const colors = [
    '#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399',
    '#9c27b0', '#2196f3', '#ff9800', '#795548', '#607d8b'
  ];
  const index = ((tagTypeId || 0) % colors.length);
  return colors[index];
};

// 提交审核结果
const submitReview = async () => {
  if (!reviewData.value.status) {
    ElMessage.warning('请选择审核结果');
    return;
  }
  
  try {
    // 这里应该调用审核API
    await approveTagRequest(props.reviewRequest.id, {
      status: reviewData.value.status,
      review_message: reviewData.value.review_message.trim() || null
    });
    
    ElMessage.success('审核完成');
    handleReviewed(reviewData.value);
  } catch (error) {
    console.error('审核失败:', error);
    ElMessage.error('审核失败');
  }
};

// 保存标签
const saveTags = async () => {
  try {
    const problemPath = props.problemInfo.data_path;
    
    if (isAdmin.value) {
      // 管理员直接保存标签 - 不要在这里编码，让API函数处理
      await setProblemTags(problemPath, selectedTags.value);
      ElMessage.success('标签设置成功');
      handleSaved(selectedTags.value);
    } else {
      // 教师提交审核请求
      const requestData = {
        problem_data_path: problemPath,
        tag_ids: selectedTags.value,
        request_message: requestMessage.value.trim() || null
      };
      
      await createTagApprovalRequest(requestData);
      ElMessage.success('标签审核请求已提交，等待管理员审核');
      handleSaved(selectedTags.value);
    }
  } catch (error) {
    console.error('操作失败:', error);
    if (isAdmin.value) {
      ElMessage.error('设置问题标签失败');
    } else {
      ElMessage.error('提交审核请求失败');
    }
  }
};

// 加载数据
const loadData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // 加载标签类型和标签
    const [tagTypesData, tagsData] = await Promise.all([
      getTagTypes(),
      getTags()
    ]);
    
    tagTypes.value = tagTypesData;
    allTags.value = tagsData;
    
    // 根据data_path构建题目详情
    if (props.problemInfo.data_path) {
      // 从题库路径生成HTML内容的API调用
      try {
        const response = await fetch(`/api/problems/html/${encodeURIComponent(props.problemInfo.data_path)}`);
        if (response.ok) {
          const htmlContent = await response.text();
          problem.value = {
            ...props.problemInfo,
            html_content: htmlContent
          };
        } else {
          // 如果获取HTML失败，至少显示基本信息
          problem.value = {
            ...props.problemInfo,
            html_content: `<h3>${props.problemInfo.chinese_name || props.problemInfo.name}</h3><p>题目详情加载失败</p>`
          };
        }
      } catch (err) {
        console.error('获取题目HTML内容失败:', err);
        problem.value = {
          ...props.problemInfo,
          html_content: `<h3>${props.problemInfo.chinese_name || props.problemInfo.name}</h3><p>题目详情加载失败</p>`
        };
      }
      
      // 获取已有标签
      try {
        const existingTags = await getProblemTags(props.problemInfo.data_path);
        selectedTags.value = existingTags.map(tag => tag.id);
      } catch (err) {
        console.error('获取已有标签失败:', err);
        selectedTags.value = [];
      }
      
      // 获取测试用例
      try {
        const response = await fetch(`/api/problems/testcases/${encodeURIComponent(props.problemInfo.data_path)}`);
        if (response.ok) {
          const data = await response.json();
          testCases.value = data.test_cases || [];
        } else {
          console.error('获取测试用例失败:', response.status);
          testCases.value = [];
        }
      } catch (err) {
        console.error('获取测试用例失败:', err);
        testCases.value = [];
      }
      
      // 获取参考代码
      try {
        const refData = await getProblemReferenceAnswer(props.problemInfo.data_path);
        referenceAnswer.value = refData.reference_answer || '';
      } catch (err) {
        console.error('获取参考代码失败:', err);
        referenceAnswer.value = '';
      }
    }
  } catch (err) {
    console.error('加载数据失败:', err);
    error.value = '加载数据失败';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadData();
  // 阻止body滚动
  document.body.style.overflow = 'hidden';
});

onUnmounted(() => {
  // 恢复body滚动
  document.body.style.overflow = '';
});

// 包装emit函数以在关闭时恢复滚动
const handleCancel = () => {
  document.body.style.overflow = '';
  emit('cancel');
};

const handleSaved = (data) => {
  document.body.style.overflow = '';
  emit('saved', data);
};

const handleReviewed = (data) => {
  document.body.style.overflow = '';
  emit('reviewed', data);
};
</script>

<style scoped>
.problem-tag-dialog {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background-color: white;
}

/* 关闭按钮样式 */
.close-button {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 20px;
  font-weight: bold;
  z-index: 1001;
  transition: all 0.3s ease;
}

.close-button:hover {
  background-color: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

.loading, .error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  color: #909399;
  font-size: 18px;
}

.error {
  color: #f56c6c;
}

.dialog-content {
  display: flex;
  flex: 1;
  gap: 20px;
  overflow: hidden;
  min-height: 0;
  height: 100vh;
}

.problem-content {
  flex: 2;
  overflow-y: auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 0;
  box-shadow: none;
  border: none;
  min-width: 60%;
  height: 100%;
}

.problem-content h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 10px;
}

.problem-html {
  line-height: 1.6;
  color: #303133;
  overflow-wrap: break-word;
}

.problem-html :deep(p) {
  margin: 1em 0;
}

.problem-html :deep(pre) {
  background-color: #f8f8f9;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

/* 测试用例样式 */
.testcases-section {
  margin-top: 30px;
  border-top: 2px solid #e4e7ed;
  padding-top: 20px;
}

.testcases-section h4 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.testcases-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.testcase-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: #fafbfc;
  overflow: hidden;
}

.testcase-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 14px;
}

.testcase-number {
  display: flex;
  align-items: center;
  gap: 8px;
}

.testcase-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}

.input-section, .output-section {
  padding: 16px;
  border-right: 1px solid #e4e7ed;
}

.output-section {
  border-right: none;
}

.input-section h5, .output-section h5 {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.testcase-data {
  background-color: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  color: #303133;
  min-height: 60px;
  max-height: 200px;
  overflow-y: auto;
}

.tags-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #ebeef5;
  padding: 20px;
  min-width: 300px;
  max-width: 400px;
  overflow: hidden;
  height: 100%;
}

.tags-section h4 {
  margin-top: 0;
  color: #606266;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
  flex-shrink: 0;
}

.tag-selection, .existing-tags-display, .review-mode-display {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
  min-height: 0;
  height: 100%;
}

.tag-type-section {
  margin-bottom: 20px;
}

.tag-type-section h5 {
  margin: 0 0 10px;
  color: #606266;
  font-size: 14px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  padding: 6px 12px;
  background-color: #f4f4f5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 13px;
  border: 1px solid #dcdfe6;
}

.tag-item:hover {
  background-color: #e9e9eb;
}

.tag-item.selected {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.dialog-actions {
  padding: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-shrink: 0;
  margin-top: auto;
  background-color: white;
  position: sticky;
  bottom: 0;
  z-index: 10;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-primary:hover {
  background-color: #66b1ff;
}

.btn-primary:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: #909399;
  color: white;
}

.btn-cancel:hover {
  background-color: #a6a9ad;
}

.request-message {
  margin-top: 15px;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.request-message label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.request-message textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  min-height: 60px;
  font-family: inherit;
  transition: border-color 0.3s;
}

.request-message textarea:focus {
  outline: none;
  border-color: #409eff;
}

.request-message textarea::placeholder {
  color: #c0c4cc;
}

/* 只查看模式样式 */
.existing-tags {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.no-tags-display {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #909399;
  font-style: italic;
}

.no-tags-display p {
  margin: 0;
  font-size: 16px;
}

/* 审核模式样式 */
.review-mode-display {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.applied-tags-section h5,
.request-reason h5,
.review-form h5 {
  margin: 0 0 10px;
  color: #606266;
  font-size: 14px;
  font-weight: 600;
}

.applied-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-badge.applied-tag {
  padding: 6px 12px;
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: 500;
}

.request-reason p {
  margin: 0;
  color: #303133;
  line-height: 1.5;
  background-color: #f8f9fa;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.review-options {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.review-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.review-option input[type="radio"] {
  margin: 0;
}

.option-text.approve {
  color: #67c23a;
  font-weight: 500;
}

.option-text.reject {
  color: #f56c6c;
  font-weight: 500;
}

.review-message-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.review-message-input label {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.review-message-input textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  transition: border-color 0.3s;
}

.review-message-input textarea:focus {
  outline: none;
  border-color: #409eff;
}

.review-message-input textarea::placeholder {
  color: #c0c4cc;
}

/* 参考代码样式 */
.reference-answer-section {
  margin-top: 30px;
  border-top: 2px solid #e4e7ed;
  padding-top: 20px;
}

.reference-answer-section h4 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.reference-answer-content {
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
}

.reference-code {
  margin: 0;
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
}

.no-reference {
  color: #909399;
  font-style: italic;
  margin: 0;
}
</style> 