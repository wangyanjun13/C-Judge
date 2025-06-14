<template>
  <div class="maintenance-container">
    <div class="tab-header">
      <div class="tab" :class="{ active: activeTab === 'problems' }" @click="activeTab = 'problems'">
        题库维护
      </div>
      <div class="tab" :class="{ active: activeTab === 'upload' }" @click="activeTab = 'upload'">
        上传题库
      </div>
    </div>

    <!-- 题库维护 -->
    <div v-if="activeTab === 'problems'" class="tab-content">
      <div class="filter-section">
        <div class="filter-item">
          <label>题库分类：</label>
          <select v-model="selectedCategory" @change="loadProblems">
            <option v-for="category in categories" :key="category.path" :value="category.path">
              {{ category.name }}
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
      <div v-else-if="!selectedCategory" class="empty-state">
        请选择一个题库分类
      </div>
      <div v-else-if="problems.length === 0" class="empty-state">
        该分类下暂无试题
      </div>
      <div v-else class="problems-table-container">
        <table class="problems-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>操作</th>
              <th>试题名称</th>
              <th>试题中文名称</th>
              <th>所有者</th>
              <th>状态</th>
              <th>时间限制</th>
              <th>内存限制</th>
              <th>数据路径</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(problem, index) in problems" :key="problem.name">
              <td>{{ index + 1 }}</td>
              <td>
                <button @click="updateProblem(problem)" class="btn btn-edit">更新</button>
                <button @click="confirmDelete(problem)" class="btn btn-delete">删除</button>
              </td>
              <td>{{ problem.name }}</td>
              <td>{{ problem.chinese_name }}</td>
              <td>{{ problem.owner }}</td>
              <td>{{ problem.is_shared ? '共享' : '私有' }}</td>
              <td>{{ problem.time_limit }}</td>
              <td>{{ problem.memory_limit }}</td>
              <td>{{ problem.data_path }}</td>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getProblemCategories, getProblemsByCategory, updateProblem as updateProblemAPI, deleteProblem as deleteProblemAPI } from '../../api/problems';

// 状态变量
const activeTab = ref('problems');
const categories = ref([]);
const selectedCategory = ref('');
const problems = ref([]);
const loading = ref(false);
const error = ref(null);
const selectedFile = ref(null);
const uploadStatus = ref('');

// 加载题库分类
const loadCategories = async () => {
  try {
    categories.value = await getProblemCategories();
    if (categories.value.length === 0) {
      ElMessage.warning('未找到题库分类，请确保题库目录已正确配置');
    } else {
      // 自动选择第一个分类
      selectedCategory.value = categories.value[0].path;
      loadProblems();
    }
  } catch (err) {
    console.error('加载题库分类失败:', err);
    ElMessage.error('加载题库分类失败');
  }
};

// 加载试题列表
const loadProblems = async () => {
  if (!selectedCategory.value) {
    problems.value = [];
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  try {
    problems.value = await getProblemsByCategory(selectedCategory.value);
  } catch (err) {
    console.error('加载试题列表失败:', err);
    error.value = '加载试题列表失败';
    ElMessage.error('加载试题列表失败');
  } finally {
    loading.value = false;
  }
};

// 更新试题
const updateProblem = (problem) => {
  ElMessage.info('更新试题功能正在开发中...');
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
  // 此处实现文件上传逻辑
};

// 页面加载时获取题库分类
onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.maintenance-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
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
</style> 