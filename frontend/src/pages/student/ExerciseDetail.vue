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
            <button @click="showStatisticsModal" class="btn btn-info">试题答题统计</button>
          </div>
        </div>
        
        <div v-if="exercise.problems && exercise.problems.length > 0">
          <table class="problems-table">
            <thead>
              <tr>
                <th>序号</th>
                <th>试题名称</th>
                <th>试题中文名称</th>
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
                <td>{{ formatChineseName(problem.chinese_name) }}</td>
                <td>{{ calculateTotalScore(problem) }}</td>
                <td>{{ problem.time_limit }}ms</td>
                <td>{{ problem.memory_limit }}MB</td>
                <td>{{ problem.code_check_score }}</td>
                <td>{{ problem.runtime_score }}</td>
                <td>{{ formatScoreMethod(problem.score_method) }}</td>
                <td>
                  <button @click="viewProblem(problem.id)" class="btn btn-primary">查看</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-problems">
          <p>该练习暂无题目</p>
        </div>
      </div>
    </template>

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
import { ElMessage } from 'element-plus';
import { getExerciseDetail } from '../../api/exercises';

const route = useRoute();
const router = useRouter();
const exerciseId = route.params.id;

const exercise = ref({});
const loading = ref(true);
const error = ref(null);
const statisticsModalVisible = ref(false);

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

// 格式化中文名称（去除引号）
const formatChineseName = (chineseName) => {
  if (!chineseName) return '';
  return chineseName.replace(/^"(.+)"$/, '$1');
};

// 格式化总分计算方法
const formatScoreMethod = (method) => {
  if (!method) return '取综合';
  if (method === 'sum') return '取综合';
  if (method === 'max') return '取较大者';
  return method;
};

// 计算题目总分
const calculateTotalScore = (problem) => {
  if (!problem) return 0;
  const codeScore = problem.code_check_score || 0;
  const runtimeScore = problem.runtime_score || 0;
  
  if (problem.score_method === 'max') {
    return Math.max(codeScore, runtimeScore);
  }
  return codeScore + runtimeScore;
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
  router.push(`/student/problem/${problemId}?exercise_id=${exerciseId}`);
};

// 返回练习列表
const goBack = () => {
  router.push('/student/exercises');
};

// 显示试题答题统计对话框
const showStatisticsModal = () => {
  statisticsModalVisible.value = true;
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

.exercise-info {
  margin-bottom: 30px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  margin-bottom: 10px;
}

.label {
  font-weight: 500;
  width: 100px;
  color: #606266;
}

.value {
  flex: 1;
  color: #303133;
}

.value.note {
  white-space: pre-wrap;
}

.problems-section {
  margin-top: 30px;
}

.problems-section h3 {
  margin-bottom: 15px;
  color: #303133;
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

.btn-back {
  background-color: #f4f4f5;
  color: #606266;
}

.btn-back:hover {
  background-color: #e9e9eb;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.btn-info {
  background-color: #909399;
  color: white;
}

.btn-info:hover {
  background-color: #a6a9ad;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  max-width: 80%;
  width: 100%;
}

.large-modal {
  width: 80%;
  max-height: 80vh;
  overflow-y: auto;
}

.form-actions {
  text-align: right;
  margin-top: 20px;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-primary:hover {
  background-color: #66b1ff;
}
</style> 