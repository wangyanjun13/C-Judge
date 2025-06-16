<template>
  <div class="problem-selector-container">
    <div class="header-section">
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
      <div class="action-buttons">
        <button @click="selectAll" class="btn btn-secondary">全选</button>
        <button @click="deselectAll" class="btn btn-secondary">全清</button>
        <button @click="confirmSelection" class="btn btn-primary">确定</button>
        <button @click="cancel" class="btn btn-cancel">取消</button>
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
            <th style="width: 50px">选择</th>
            <th>序号</th>
            <th>试题名称</th>
            <th>试题中文名称</th>
            <th>时间限制</th>
            <th>内存限制</th>
            <th>数据路径</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(problem, index) in problems" :key="problem.name">
            <td>
              <input 
                type="checkbox" 
                :value="problem" 
                v-model="selectedProblems"
                @change="updateSelectedCount"
              />
            </td>
            <td>{{ index + 1 }}</td>
            <td>{{ problem.name }}</td>
            <td>{{ problem.chinese_name }}</td>
            <td>{{ problem.time_limit }}</td>
            <td>{{ problem.memory_limit }}</td>
            <td>{{ problem.data_path }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="selection-info">
      已选择 {{ selectedProblems.length }} 道题目
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getProblemCategories, getProblemsByCategory } from '../api/problems';

// 组件接收的属性
const props = defineProps({
  exerciseId: {
    type: [String, Number],
    required: true
  }
});

// 组件触发的事件
const emit = defineEmits(['confirm', 'cancel']);

// 状态变量
const categories = ref([]);
const selectedCategory = ref('');
const problems = ref([]);
const selectedProblems = ref([]);
const loading = ref(false);
const error = ref(null);

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
    // 重置选择
    selectedProblems.value = [];
  } catch (err) {
    console.error('加载试题列表失败:', err);
    error.value = '加载试题列表失败';
    ElMessage.error('加载试题列表失败');
  } finally {
    loading.value = false;
  }
};

// 全选
const selectAll = () => {
  selectedProblems.value = [...problems.value];
};

// 全清
const deselectAll = () => {
  selectedProblems.value = [];
};

// 更新选择计数
const updateSelectedCount = () => {
  console.log(`已选择 ${selectedProblems.value.length} 道题目`);
};

// 确认选择
const confirmSelection = () => {
  if (selectedProblems.value.length === 0) {
    ElMessage.warning('请至少选择一道题目');
    return;
  }
  
  // 为选中的题目添加分数设置，但保留原始的时间限制和内存限制
  const problems = selectedProblems.value.map(problem => {
    return {
      ...problem,
      code_check_score: problem.code_check_score || 20,
      runtime_score: problem.runtime_score || 80,
      score_method: 'sum'
    };
  });
  
  // 触发确认事件，将选择的题目传递给父组件
  emit('confirm', {
    exerciseId: props.exerciseId,
    problems: problems
  });
};

// 取消选择
const cancel = () => {
  emit('cancel');
};

// 页面加载时获取题库分类
onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.problem-selector-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-section {
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

.action-buttons {
  display: flex;
  gap: 10px;
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
  margin-bottom: 20px;
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

.selection-info {
  text-align: right;
  margin-top: 10px;
  color: #606266;
  font-weight: 500;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-primary:hover {
  background-color: #66b1ff;
}

.btn-secondary {
  background-color: #909399;
  color: white;
}

.btn-secondary:hover {
  background-color: #a6a9ad;
}

.btn-cancel {
  background-color: #f0f0f0;
  color: #606266;
}

.btn-cancel:hover {
  background-color: #e0e0e0;
}
</style> 