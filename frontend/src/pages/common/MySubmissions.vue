<template>
  <div class="dashboard-container">
    <h2 class="dashboard-title">个人答题仪表盘</h2>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载您的答题数据...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-icon">!</div>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchSubmissions">重试</button>
    </div>
    
    <div v-else-if="submissions.length === 0" class="empty-container">
      <div class="empty-icon">📝</div>
      <p>您还没有提交过任何题目</p>
      <p class="empty-hint">完成题目后，您的答题记录将显示在这里</p>
    </div>
    
    <div v-else class="dashboard-content">
      <!-- 数据概览卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-value">{{ submissions.length }}</div>
          <div class="stat-label">已答题目</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ averageScore }}</div>
          <div class="stat-label">平均分</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ highestScore }}</div>
          <div class="stat-label">最高分</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ completedExercises }}</div>
          <div class="stat-label">参与练习</div>
        </div>
      </div>
      
      <!-- 提交记录表格 -->
      <div class="table-header">
        <h3>我的答题记录</h3>
        <div class="table-actions">
          <select v-model="filterExercise" class="filter-select">
            <option value="">全部练习</option>
            <option v-for="ex in uniqueExercises" :key="ex.id" :value="ex.id">
              {{ ex.name }}
            </option>
          </select>
        </div>
      </div>
      
      <div class="table-container">
        <table class="submissions-table">
          <thead>
            <tr>
              <th>题目名称</th>
              <th>得分</th>
              <th>所属练习</th>
              <th>所属课程</th>
              <th>班级</th>
              <th>提交时间</th>
              <th>班级排名</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredSubmissions" :key="item.id" :class="getScoreClass(item.total_score)">
              <td class="problem-name-cell">
                {{ item.problem_name }}
                <div class="chinese-name" v-if="item.problem_chinese_name">{{ item.problem_chinese_name }}</div>
              </td>
              <td class="score-cell">{{ item.total_score ?? 0 }}</td>
              <td>{{ item.exercise_name || '-' }}</td>
              <td>{{ item.course_name || '-' }}</td>
              <td>{{ item.class_names || '-' }}</td>
              <td>{{ formatDate(item.submitted_at) }}</td>
              <td>
                <button class="ranking-btn" @click="showRanking(item)" :disabled="!item.exercise_id">
                  {{ item.exercise_id ? '查看排名' : '无排名' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <el-dialog v-model="rankingDialog.visible" title="班级排名" width="80%" destroy-on-close>
      <ProblemRanking
        v-if="rankingDialog.visible && rankingDialog.problemId"
        :problem-id="rankingDialog.problemId"
        :exercise-id="rankingDialog.exerciseId"
        :class-id="rankingDialog.classId"
        :problem-name="rankingDialog.problemName"
        @close="rankingDialog.visible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../../store/auth';
import { getMySubmissions } from '../../api/submissions';
import ProblemRanking from '../../components/ProblemRanking.vue';
import { ElMessage } from 'element-plus';

const authStore = useAuthStore();
const loading = ref(true);
const error = ref(null);
const submissions = ref([]);
const filterExercise = ref('');
const rankingDialog = ref({
  visible: false,
  problemId: null,
  exerciseId: null,
  classId: null,
  problemName: ''
});

// 格式化时间
const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 获取所有答题记录
const fetchSubmissions = async () => {
  loading.value = true;
  error.value = null;
  try {
    // 使用新API直接获取包含完整信息的答题记录
    const data = await getMySubmissions();
    submissions.value = data;
  } catch (e) {
    error.value = '获取答题记录失败';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
};

// 显示班级排名弹窗
const showRanking = (item) => {
  rankingDialog.value = {
    visible: true,
    problemId: item.problem_id,
    exerciseId: item.exercise_id,
    classId: item.class_id,
    problemName: item.problem_name
  };
};

// 根据分数获取行样式类名
const getScoreClass = (score) => {
  if (score === null || score === undefined) return 'no-score';
  if (score >= 90) return 'excellent-score';
  if (score >= 80) return 'good-score';
  if (score >= 60) return 'pass-score';
  return 'fail-score';
};

// 统计数据计算
const averageScore = computed(() => {
  if (!submissions.value.length) return 0;
  const total = submissions.value.reduce((sum, item) => sum + (item.total_score || 0), 0);
  return Math.round(total / submissions.value.length);
});

const highestScore = computed(() => {
  if (!submissions.value.length) return 0;
  return Math.max(...submissions.value.map(item => item.total_score || 0));
});

// 唯一练习列表
const uniqueExercises = computed(() => {
  const exercises = [];
  const seen = new Set();
  
  submissions.value.forEach(item => {
    if (item.exercise_id && item.exercise_name && !seen.has(item.exercise_id)) {
      seen.add(item.exercise_id);
      exercises.push({
        id: item.exercise_id,
        name: item.exercise_name
      });
    }
  });
  
  return exercises;
});

// 参与的练习数量
const completedExercises = computed(() => uniqueExercises.value.length);

// 根据练习筛选提交记录
const filteredSubmissions = computed(() => {
  if (!filterExercise.value) return submissions.value;
  return submissions.value.filter(item => item.exercise_id === filterExercise.value);
});

onMounted(() => {
  fetchSubmissions();
});
</script>

<style scoped>
.dashboard-container {
  padding: 25px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  min-height: 80vh;
}

.dashboard-title {
  margin-top: 0;
  margin-bottom: 25px;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #909399;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #409eff;
  border-radius: 50%;
  margin-bottom: 15px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态 */
.error-container {
  text-align: center;
  padding: 40px 0;
  color: #f56c6c;
}

.error-icon {
  font-size: 30px;
  width: 50px;
  height: 50px;
  line-height: 50px;
  margin: 0 auto 15px;
  border-radius: 50%;
  background-color: #fef0f0;
  color: #f56c6c;
  font-weight: bold;
}

.retry-btn {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

/* 空状态 */
.empty-container {
  text-align: center;
  padding: 60px 0;
  color: #909399;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.empty-hint {
  color: #c0c4cc;
  font-size: 14px;
}

/* 仪表盘内容 */
.dashboard-content {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #f8fafc;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0,0,0,0.08);
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

/* 表格头部 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 15px;
}

.table-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fff;
  color: #606266;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
}

.submissions-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.submissions-table th,
.submissions-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.submissions-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
  position: sticky;
  top: 0;
  z-index: 1;
}

.submissions-table tr {
  transition: background-color 0.2s;
}

.submissions-table tr:hover {
  background-color: #f9fafc;
}

/* 分数样式 */
.score-cell {
  font-weight: 600;
}

.excellent-score .score-cell {
  color: #67c23a;
}

.good-score .score-cell {
  color: #409eff;
}

.pass-score .score-cell {
  color: #e6a23c;
}

.fail-score .score-cell {
  color: #f56c6c;
}

.no-score .score-cell {
  color: #909399;
}

/* 题目名称 */
.problem-name-cell {
  max-width: 250px;
}

.chinese-name {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 按钮样式 */
.ranking-btn {
  padding: 6px 12px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.ranking-btn:hover:not(:disabled) {
  background: #66b1ff;
  transform: translateY(-1px);
}

.ranking-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dashboard-title {
    font-size: 20px;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .submissions-table th,
  .submissions-table td {
    padding: 10px;
  }
}
</style> 