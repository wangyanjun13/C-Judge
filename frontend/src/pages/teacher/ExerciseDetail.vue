<template>
  <div class="exercise-detail-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack" class="btn btn-primary">返回练习列表</button>
    </div>
    <template v-else>
      <div class="header">
        <h2>{{ exercise.name }} 
          <span class="time-info" v-if="isExerciseStarted && !isExerciseEnded">
            ({{ formatTimeRemaining() }}后结束)
          </span>
          <span class="time-info" v-else-if="!isExerciseStarted">
            ({{ formatTimeRemaining() }}后开始)
          </span>
          <span class="time-info" v-else-if="isExerciseEnded">
            (已结束)
          </span>
        </h2>
        <div class="actions">
          <button @click="goBack" class="btn btn-back">返回</button>
        </div>
      </div>
      
      <div class="problems-section">
        <div class="section-header">
          <h3>题目列表</h3>
          <div class="action-buttons">
            <button @click="showAddProblemModal" class="btn btn-primary">添加题目</button>
            <button @click="showStatisticsModal" class="btn btn-info">试题答题统计</button>
            <button @click="evaluateExercise" class="btn btn-success">测评练习</button>
            <button @click="checkPlagiarism" class="btn btn-warning">查抄袭</button>
            <button @click="clearExercise" class="btn btn-danger">清空</button>
          </div>
        </div>
        
        <div v-if="exercise.problems && exercise.problems.length > 0">
          <table class="problems-table">
            <thead>
              <tr>
                <th>序号</th>
                <th>题目名称</th>
                <th>题目标题</th>
                <th>得分</th>
                <th>时间限制</th>
                <th>内存限制</th>
                <th>代码检查总分</th>
                <th>运行总分</th>
                <th>总分计算方法</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(problem, index) in exercise.problems" :key="problem.id">
                <td>{{ index + 1 }}</td>
                <td>{{ problem.name }}</td>
                <td>{{ problem.chinese_name }}</td>
                <td>{{ problem.score || 0 }}</td>
                <td>{{ problem.time_limit }}ms</td>
                <td>{{ problem.memory_limit }}MB</td>
                <td>{{ problem.code_review_score || 0 }}</td>
                <td>{{ problem.runtime_score || 0 }}</td>
                <td>{{ problem.score_calculation_method || '取综合' }}</td>
                <td>
                  <button @click="viewProblem(problem.id)" class="btn btn-primary">查看</button>
                  <button @click="showEditProblemModal(problem)" class="btn btn-edit">修改</button>
                  <button @click="removeProblem(problem.id)" class="btn btn-danger">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-problems">
          <p>该练习暂无题目，请添加题目</p>
        </div>
      </div>
    </template>
    
    <!-- 添加题目对话框 -->
    <div v-if="addProblemModalVisible" class="modal-overlay" @click="addProblemModalVisible = false">
      <div class="modal" @click.stop>
        <h3>添加题目</h3>
        <p>此功能正在开发中...</p>
        <div class="form-actions">
          <button @click="addProblemModalVisible = false" class="btn btn-primary">关闭</button>
        </div>
      </div>
    </div>

    <!-- 编辑题目对话框 -->
    <div v-if="editProblemModalVisible" class="modal-overlay" @click="editProblemModalVisible = false">
      <div class="modal" @click.stop>
        <h3>修改题目</h3>
        <form @submit.prevent="submitEditProblemForm">
          <div class="form-section">
            <h4>基本内容</h4>
            <div class="form-group">
              <label for="problem-name">试题名称</label>
              <input id="problem-name" v-model="editProblemForm.name" required />
            </div>
            <div class="form-row">
              <div class="form-group half">
                <label for="problem-time-limit">时间限制 (ms)</label>
                <input id="problem-time-limit" type="number" v-model="editProblemForm.time_limit" required />
              </div>
              <div class="form-group half">
                <label for="problem-memory-limit">空间限制 (MB)</label>
                <input id="problem-memory-limit" type="number" v-model="editProblemForm.memory_limit" required />
              </div>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="editProblemForm.apply_limits_to_all" />
                应用时限和空限到所有试题
              </label>
            </div>
          </div>

          <div class="form-section">
            <h4>得分计算方法</h4>
            <div class="form-group">
              <label for="score-calculation-method">计算方法</label>
              <select id="score-calculation-method" v-model="editProblemForm.score_calculation_method">
                <option value="综合">取综合</option>
                <option value="较大者">取较大者</option>
              </select>
            </div>
            <div class="form-row">
              <div class="form-group half">
                <label for="code-review-score">代码检查总分</label>
                <input id="code-review-score" type="number" v-model="editProblemForm.code_review_score" required />
              </div>
              <div class="form-group half">
                <label for="runtime-score">运行总分</label>
                <input id="runtime-score" type="number" v-model="editProblemForm.runtime_score" required />
              </div>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="editProblemForm.apply_score_method_to_all" />
                应用得分计算方法到所有试题
              </label>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="editProblemModalVisible = false" class="btn btn-cancel">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 试题答题统计对话框 -->
    <div v-if="statisticsModalVisible" class="modal-overlay" @click="statisticsModalVisible = false">
      <div class="modal large-modal" @click.stop>
        <h3>试题答题统计</h3>
        <p>此功能正在开发中...</p>
        <div class="form-actions">
          <button @click="statisticsModalVisible = false" class="btn btn-primary">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getExerciseDetail, updateExercise, removeProblemFromExercise, updateProblem } from '../../api/exercises';

const route = useRoute();
const router = useRouter();
const exerciseId = route.params.id;

const exercise = ref({});
const loading = ref(true);
const error = ref(null);
const addProblemModalVisible = ref(false);
const editProblemModalVisible = ref(false);
const statisticsModalVisible = ref(false);

// 编辑题目表单
const editProblemForm = ref({
  id: '',
  name: '',
  chinese_name: '',
  time_limit: '',
  memory_limit: '',
  apply_limits_to_all: false,
  score_calculation_method: '综合',
  code_review_score: '',
  runtime_score: '',
  apply_score_method_to_all: false
});

// 添加题目表单
const addProblemForm = ref({
  name: '',
  chinese_name: '',
  time_limit: '',
  memory_limit: '',
  apply_limits_to_all: false,
  score_calculation_method: '综合',
  code_review_score: '',
  runtime_score: '',
  apply_score_method_to_all: false
});

// 在script setup部分添加计算练习时间的函数
const isExerciseStarted = computed(() => {
  if (!exercise.value || !exercise.value.publish_time) return false;
  return new Date(exercise.value.publish_time) <= new Date();
});

const isExerciseEnded = computed(() => {
  if (!exercise.value || !exercise.value.end_time) return false;
  return new Date(exercise.value.end_time) <= new Date();
});

const formatTimeRemaining = () => {
  if (!exercise.value) return '';
  
  const now = new Date();
  let targetDate;
  
  if (!isExerciseStarted.value) {
    // 未开始，计算距离开始的时间
    targetDate = new Date(exercise.value.publish_time);
  } else if (!isExerciseEnded.value) {
    // 已开始但未结束，计算距离结束的时间
    targetDate = new Date(exercise.value.end_time);
  } else {
    return '已结束';
  }
  
  const diffMs = Math.abs(targetDate - now);
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  
  if (diffDays > 0) {
    return `${diffDays}天${diffHours}小时`;
  } else {
    return `${diffHours}小时`;
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 格式化日期为输入框格式
const formatDateForInput = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}T${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 格式化语言
const formatLanguages = (languages) => {
  if (!languages) return '无';
  
  const languageMap = {
    'c': 'C',
    'cpp': 'C++',
    'java': 'Java',
    'python': 'Python'
  };
  
  return languages.split(',').map(lang => languageMap[lang] || lang).join(', ');
};

// 获取练习详情
const fetchExerciseDetail = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await getExerciseDetail(exerciseId);
    exercise.value = result;
  } catch (err) {
    console.error('获取练习详情失败', err);
    error.value = '获取练习详情失败，请稍后重试';
    ElMessage.error('获取练习详情失败');
  } finally {
    loading.value = false;
  }
};

// 查看题目
const viewProblem = (problemId) => {
  router.push(`/teacher/problem/${problemId}?exercise_id=${exerciseId}`);
};

// 返回练习列表
const goBack = () => {
  router.push('/teacher/exercises');
};

// 显示添加题目对话框
const showAddProblemModal = () => {
  addProblemModalVisible.value = true;
};

// 移除题目
const removeProblem = async (problemId) => {
  try {
    await ElMessageBox.confirm('确定要从练习中移除该题目吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    await removeProblemFromExercise(exerciseId, problemId);
    ElMessage.success('题目已成功移除');
    fetchExerciseDetail(); // 重新获取练习详情
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除题目失败', error);
      ElMessage.error('移除题目失败');
    }
  }
};

// 显示编辑题目对话框
const showEditProblemModal = (problem) => {
  editProblemForm.value = {
    id: problem.id,
    name: problem.name,
    chinese_name: problem.chinese_name,
    time_limit: problem.time_limit,
    memory_limit: problem.memory_limit,
    apply_limits_to_all: false,
    score_calculation_method: problem.score_calculation_method || '综合',
    code_review_score: problem.code_review_score || 0,
    runtime_score: problem.runtime_score || 0,
    apply_score_method_to_all: false
  };
  editProblemModalVisible.value = true;
};

// 提交编辑题目表单
const submitEditProblemForm = async () => {
  try {
    console.log('提交编辑题目表单:', editProblemForm.value);
    
    // 如果应用到所有题目
    if (editProblemForm.value.apply_limits_to_all || editProblemForm.value.apply_score_method_to_all) {
      const updatedProblems = exercise.value.problems.map(problem => {
        const updatedProblem = { ...problem };
        
        if (editProblemForm.value.apply_limits_to_all) {
          updatedProblem.time_limit = editProblemForm.value.time_limit;
          updatedProblem.memory_limit = editProblemForm.value.memory_limit;
        }
        
        if (editProblemForm.value.apply_score_method_to_all) {
          updatedProblem.score_calculation_method = editProblemForm.value.score_calculation_method;
          updatedProblem.code_review_score = editProblemForm.value.code_review_score;
          updatedProblem.runtime_score = editProblemForm.value.runtime_score;
        }
        
        return updatedProblem;
      });
      
      // 批量更新所有题目
      await updateExercise(exerciseId, { problems: updatedProblems });
    } else {
      // 只更新单个题目
      await updateProblem(exerciseId, editProblemForm.value.id, {
        name: editProblemForm.value.name,
        chinese_name: editProblemForm.value.chinese_name,
        time_limit: editProblemForm.value.time_limit,
        memory_limit: editProblemForm.value.memory_limit,
        score_calculation_method: editProblemForm.value.score_calculation_method,
        code_review_score: editProblemForm.value.code_review_score,
        runtime_score: editProblemForm.value.runtime_score
      });
    }
    
    ElMessage.success('题目更新成功');
    editProblemModalVisible.value = false;
    fetchExerciseDetail(); // 重新获取练习详情
  } catch (error) {
    console.error('更新题目失败', error);
    ElMessage.error('更新题目失败');
  }
};

// 显示试题答题统计对话框
const showStatisticsModal = () => {
  statisticsModalVisible.value = true;
};

// 清空练习
const clearExercise = () => {
  ElMessage.info('清空练习功能正在开发中...');
};

// 测评练习
const evaluateExercise = () => {
  ElMessage.info('测评练习功能正在开发中...');
};

// 检查抄袭
const checkPlagiarism = () => {
  ElMessage.info('检查抄袭功能正在开发中...');
};

onMounted(() => {
  fetchExerciseDetail();
});
</script>

<style scoped>
.exercise-detail-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.loading, .error {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.error {
  color: #f56c6c;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.header h2 {
  margin: 0;
  color: #303133;
  display: flex;
  align-items: center;
}

.time-info {
  font-size: 14px;
  color: #909399;
  margin-left: 10px;
  font-weight: normal;
}

.actions {
  display: flex;
  gap: 10px;
}

.problems-section {
  margin-top: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 10px;
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

.empty-problems {
  text-align: center;
  padding: 20px;
  color: #909399;
  background-color: #f8f8f9;
  border-radius: 4px;
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

.btn-edit {
  background-color: #67c23a;
  color: white;
}

.btn-edit:hover {
  background-color: #85ce61;
}

.btn-danger {
  background-color: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background-color: #f78989;
}

.btn-back {
  background-color: #f4f4f5;
  color: #606266;
}

.btn-back:hover {
  background-color: #e9e9eb;
}

.btn-cancel {
  background-color: #909399;
  color: white;
}

.btn-cancel:hover {
  background-color: #a6a9ad;
}

/* 模态对话框样式 */
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
  z-index: 100;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #606266;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.datetime-input-wrapper {
  position: relative;
}

.datetime-helper {
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
}

.form-section {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-group.half {
  width: calc(50% - 5px);
}

.checkbox-label {
  display: flex;
  align-items: center;
}

.checkbox-label input {
  margin-right: 5px;
}
</style> 