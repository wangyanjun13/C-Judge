<template>
  <div class="exercise-detail-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack" class="btn btn-primary">返回练习列表</button>
    </div>
    <template v-else>
      <div class="header">
        <h2>{{ exercise.name }}</h2>
        <button @click="goBack" class="btn btn-back">返回</button>
      </div>
      
      <div class="exercise-info">
        <div class="info-item">
          <span class="label">所属课程:</span>
          <span class="value">{{ exercise.course_name }}</span>
        </div>
        <div class="info-item">
          <span class="label">发布时间:</span>
          <span class="value">{{ formatDate(exercise.publish_time) }}</span>
        </div>
        <div class="info-item">
          <span class="label">截止时间:</span>
          <span class="value">{{ formatDate(exercise.deadline) }}</span>
        </div>
        <div class="info-item">
          <span class="label">在线评测:</span>
          <span class="value">{{ exercise.is_online_judge ? '是' : '否' }}</span>
        </div>
        <div class="info-item">
          <span class="label">允许语言:</span>
          <span class="value">{{ formatLanguages(exercise.allowed_languages) }}</span>
        </div>
        <div class="info-item" v-if="exercise.note">
          <span class="label">练习备注:</span>
          <span class="value note">{{ exercise.note }}</span>
        </div>
      </div>
      
      <div class="problems-section">
        <h3>题目列表</h3>
        <div v-if="exercise.problems && exercise.problems.length > 0">
          <table class="problems-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>题目名称</th>
                <th>题目标题</th>
                <th>时间限制</th>
                <th>内存限制</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="problem in exercise.problems" :key="problem.id">
                <td>{{ problem.id }}</td>
                <td>{{ problem.name }}</td>
                <td>{{ problem.chinese_name }}</td>
                <td>{{ problem.time_limit }}ms</td>
                <td>{{ problem.memory_limit }}MB</td>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getExerciseDetail } from '../../api/exercises';

const route = useRoute();
const router = useRouter();
const exerciseId = route.params.id;

const exercise = ref({});
const loading = ref(true);
const error = ref(null);

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
</style> 