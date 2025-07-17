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
    </div>

    <!-- 题库维护 -->
    <div v-if="activeTab === 'problems'" class="tab-content">
      <div class="filter-section">
        <!-- 移除题库分类筛选框 -->
        <!-- 动态显示所有标签类型 -->
        <div v-for="tagType in tagTypes" :key="tagType.id" class="filter-item">
          <label>{{ tagType.name }}标签：</label>
          <select v-model="selectedTagIds[tagType.id]" @change="loadProblems">
            <option value="">全部</option>
            <option v-for="tag in getTagsByType(tagType.id)" :key="tag.id" :value="tag.id">
              {{ tag.name }}
            </option>
          </select>
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
              <th>时间限制</th>
              <th>内存限制</th>
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
              <td>{{ problem.time_limit }}</td>
              <td>{{ problem.memory_limit }}</td>
              <td class="tags-cell">
                <div v-if="problemTags[problem.data_path]" class="problem-tags">
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
    
    <!-- 打标签对话框 -->
    <div v-if="showTagDialog" class="modal-overlay">
      <div class="modal">
        <h3>为"{{ selectedProblem?.chinese_name }}"设置标签</h3>
        <div class="tag-dialog-content">
          <div v-for="tagType in tagTypes" :key="tagType.id" class="tag-type-section">
            <h4>{{ tagType.name }}</h4>
            <div class="tag-list">
              <div 
                v-for="tag in getTagsByType(tagType.id)" 
                :key="tag.id" 
                class="tag-item"
                :class="{ selected: selectedTagsForProblem.includes(tag.id) }"
                @click="toggleTag(tag.id)"
              >
                {{ tag.name }}
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="closeTagDialog" class="btn">取消</button>
          <button @click="saveProblemTags" class="btn btn-primary">保存</button>
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
import { getTagTypes, getTags, getProblemTags, setProblemTags, getBatchProblemTags } from '../../api/tags';

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

// 加载题库分类
const loadCategories = async () => {
  try {
    categories.value = await getProblemCategories();
    if (categories.value.length === 0) {
      ElMessage.warning('未找到题库分类，请确保题库目录已正确配置');
    } else {
      // 默认选择"全部"选项
      selectedCategory.value = 'all';
      loadProblems();
    }
  } catch (err) {
    console.error('加载题库分类失败:', err);
    ElMessage.error('加载题库分类失败');
  }
};

// 加载标签类型和标签
const loadTags = async () => {
  try {
    // 加载标签类型
    tagTypes.value = await getTagTypes();
    
    // 加载所有标签
    allTags.value = await getTags();
    
    // 初始化selectedTagIds对象和tagTypeMap
    tagTypes.value.forEach(tagType => {
      selectedTagIds.value[tagType.id] = '';
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

// 加载试题列表
const loadProblems = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // 构建过滤选项
    const options = {};
    
    // 查找第一个被选中的标签
    for (const tagTypeId in selectedTagIds.value) {
      if (selectedTagIds.value[tagTypeId]) {
        options.tagId = selectedTagIds.value[tagTypeId];
        break; // 只使用第一个被选中的标签进行过滤
      }
    }
    
    // 获取所有题库，不再根据分类筛选
    let allProblems = [];
    if (categories.value.length > 0) {
      for (const category of categories.value) {
        const categoryProblems = await getProblemsByCategory(category.path, options);
        allProblems = [...allProblems, ...categoryProblems];
      }
    } else {
      // 如果没有分类，尝试获取默认题库
      allProblems = await getProblemsByCategory('', options);
    }
    problems.value = allProblems;
    
    // 加载每个问题的标签
    await loadProblemTags();
  } catch (err) {
    console.error('加载试题列表失败:', err);
    error.value = '加载试题列表失败';
    ElMessage.error('加载试题列表失败');
  } finally {
    loading.value = false;
  }
};

// 加载所有问题的标签
const loadProblemTags = async () => {
  if (problems.value.length === 0) return;
  
  try {
    // 收集所有问题的data_path，但仅包括那些在problemTags中不存在的
    const missingPaths = problems.value
      .filter(problem => problem.data_path && !problemTags.value[problem.data_path])
      .map(problem => encodeURIComponent(problem.data_path));
    
    if (missingPaths.length === 0) {
      console.log('所有问题标签已在本地缓存中，无需请求');
      return; // 如果所有问题的标签都已经在本地缓存中，则不发起请求
    }
    
    // 批量获取缺失的问题标签
    console.log(`批量获取${missingPaths.length}个问题的标签`);
    const batchTags = await getBatchProblemTags(missingPaths);
    
    // 将结果合并到problemTags中
    for (const problem of problems.value) {
      if (problem.data_path) {
        const encodedPath = encodeURIComponent(problem.data_path);
        if (batchTags[encodedPath] && batchTags[encodedPath].length > 0) {
          problemTags.value[problem.data_path] = batchTags[encodedPath];
        }
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
const openTagDialog = async (problem) => {
  selectedProblem.value = problem;
  showTagDialog.value = true;
  
  try {
    // 使用data_path作为唯一标识符
    if (!problem.data_path) {
      console.error('问题缺少data_path字段:', problem);
      ElMessage.error('无法获取问题标识符');
      return;
    }
    
    // 获取问题已有的标签
    const problemPath = encodeURIComponent(problem.data_path);
    const problemTags = await getProblemTags(problemPath);
    selectedTagsForProblem.value = problemTags.map(tag => tag.id);
  } catch (error) {
    console.error('获取问题标签失败:', error);
    selectedTagsForProblem.value = [];
  }
};

// 关闭标签对话框
const closeTagDialog = () => {
  showTagDialog.value = false;
  selectedProblem.value = null;
  selectedTagsForProblem.value = [];
};

// 切换标签选择状态
const toggleTag = (tagId) => {
  const index = selectedTagsForProblem.value.indexOf(tagId);
  if (index === -1) {
    // 如果标签不在选中列表中，则添加
    selectedTagsForProblem.value.push(tagId);
  } else {
    // 如果标签已在选中列表中，则移除
    selectedTagsForProblem.value.splice(index, 1);
  }
};

// 保存问题标签
const saveProblemTags = async () => {
  if (!selectedProblem.value || !selectedProblem.value.data_path) return;
  
  try {
    const problemPath = encodeURIComponent(selectedProblem.value.data_path);
    await setProblemTags(problemPath, selectedTagsForProblem.value);
    ElMessage.success('标签设置成功');
    logUserOperation(OperationType.UPDATE_PROBLEM_TAGS, `试题: ${selectedProblem.value.chinese_name}`);
    
    // 更新本地标签缓存
    if (selectedTagsForProblem.value.length > 0) {
      const selectedTags = allTags.value.filter(tag => selectedTagsForProblem.value.includes(tag.id));
      problemTags.value[selectedProblem.value.data_path] = selectedTags;
    } else {
      delete problemTags.value[selectedProblem.value.data_path];
    }
    
    closeTagDialog();
  } catch (error) {
    console.error('设置问题标签失败:', error);
    ElMessage.error('设置问题标签失败');
  }
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
  // 重新加载标签和题目列表
  await loadTags();
  await loadProblems();
};

// 监听路由参数变化
watch(() => route.query.tab, (newTab) => {
  if (newTab === 'upload') {
    activeTab.value = 'upload';
  } else if (newTab === 'tags') {
    activeTab.value = 'tags';
  } else {
    activeTab.value = 'problems';
  }
}, { immediate: true });

// 页面加载时获取题库分类和标签
onMounted(async () => {
  await loadCategories();
  await loadTags();
  await loadProblems(); // 直接加载所有题目
});
</script>

<style scoped>
.maintenance-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 60px;
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

.filter-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.filter-item {
  margin-right: 20px;
  display: flex;
  align-items: center;
}

.filter-item label {
  margin-right: 10px;
}

.filter-item select {
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  width: 200px;
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
  max-width: 300px;
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

.tag-item {
  padding: 6px 12px;
  background-color: #f4f4f5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.tag-item:hover {
  background-color: #e9e9eb;
}

.tag-item.selected {
  background-color: #409eff;
  color: white;
}

.dialog-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 