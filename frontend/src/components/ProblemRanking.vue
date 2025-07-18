<template>
  <div class="problem-ranking-container">
    <div v-if="loading" class="loading">
      <span>加载中...</span>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    <div v-else class="ranking-content">
      <div class="ranking-header">
        <h2 class="problem-title">{{ problemName }} - 班级排名</h2>
        <div class="ranking-stats">
          <div class="stat-item">
            <span class="stat-label">提交人数</span>
            <span class="stat-value">{{ rankingData.submission_count }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">班级人数</span>
            <span class="stat-value">{{ rankingData.total_students }}</span>
          </div>
          <div v-if="rankingData.current_user_rank" class="stat-item highlight">
            <span class="stat-label">我的排名</span>
            <span class="stat-value">{{ rankingData.current_user_rank }}</span>
          </div>
        </div>
      </div>

      <!-- 特殊提交卡片区域：教师提交和当前用户自己提交（非学生） -->
      <div class="special-cards">
        <!-- 教师提交信息 -->
        <div v-if="rankingData.teacher_submission" class="card teacher-card">
          <div class="card-header">
            <span class="card-icon">👨‍🏫</span>
            <span class="card-title">教师提交</span>
          </div>
          <div class="card-body">
            <div class="submission-score">{{ rankingData.teacher_submission.score }}分</div>
            <div class="submission-details">
              <div class="submission-name">{{ rankingData.teacher_submission.real_name || rankingData.teacher_submission.username }}</div>
              <div class="submission-meta">
                <div class="submission-status">{{ rankingData.teacher_submission.status }}</div>
                <div class="submission-time">{{ formatTime(rankingData.teacher_submission.submitted_at) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 管理员/教师自己的提交 -->
        <div v-if="rankingData.current_user_submission && !rankingData.current_user_rank" 
             class="card user-card">
          <div class="card-header">
            <span class="card-icon">👤</span>
            <span class="card-title">您的提交 ({{ userRole === 'teacher' ? '教师' : '管理员' }})</span>
          </div>
          <div class="card-body">
            <div class="submission-score">{{ rankingData.current_user_submission.score }}分</div>
            <div class="submission-details">
              <div class="submission-name">{{ rankingData.current_user_submission.real_name || rankingData.current_user_submission.username }}</div>
              <div class="submission-meta">
                <div class="submission-status">{{ rankingData.current_user_submission.status }}</div>
                <div class="submission-time">{{ formatTime(rankingData.current_user_submission.submitted_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 排名列表 -->
      <div class="ranking-list-container">
        <div v-if="rankingData.rankings.length === 0" class="no-data">
          暂无学生数据
        </div>
        <div v-else>
          <div class="ranking-table">
            <div class="table-header">
              <div class="col-rank">排名</div>
              <div class="col-name">姓名</div>
              <div class="col-score">得分</div>
              <div class="col-status">状态</div>
              <div class="col-time">提交时间</div>
            </div>
            
            <div class="table-body">
              <!-- 已提交的学生 -->
              <div v-for="(item, index) in submittedStudents" :key="`submitted-${item.user_id}`"
                   class="table-row" :class="{'current-user': item.user_id === currentUserId}">
                <div class="col-rank">
                  <span class="rank-badge" :class="getRankClass(index)">{{ index + 1 }}</span>
                </div>
                <div class="col-name">{{ item.real_name || item.username }}</div>
                <div class="col-score">{{ item.score }}分</div>
                <div class="col-status">{{ item.status }}</div>
                <div class="col-time">{{ formatTime(item.submitted_at) }}</div>
              </div>

              <!-- 未提交分隔线 -->
              <div v-if="unsubmittedStudents.length > 0" class="divider">
                <span>以下同学未提交</span>
              </div>
              
              <!-- 未提交的学生 -->
              <div v-for="item in unsubmittedStudents" :key="`unsubmitted-${item.user_id}`"
                   class="table-row unsubmitted" :class="{'current-user': item.user_id === currentUserId}">
                <div class="col-rank">-</div>
                <div class="col-name">{{ item.real_name || item.username }}</div>
                <div class="col-score">0分</div>
                <div class="col-status">未提交</div>
                <div class="col-time">-</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 关闭按钮 -->
      <div class="action-bar">
        <button class="action-button" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../store/auth';
import { getProblemRanking } from '../api/submissions';
import { ElMessage } from 'element-plus';

const props = defineProps({
  problemId: {
    type: Number,
    required: true
  },
  exerciseId: {
    type: Number,
    required: true
  },
  classId: {
    type: Number,
    default: null
  },
  problemName: {
    type: String,
    default: '题目'
  }
});

const emit = defineEmits(['close']);
const authStore = useAuthStore();
const currentUserId = computed(() => authStore.user?.id);
const userRole = computed(() => authStore.user?.role);

const loading = ref(true);
const error = ref(null);
const rankingData = ref({
  rankings: [],
  current_user_rank: null,
  total_students: 0,
  submission_count: 0,
  current_user_submission: null,
  teacher_submission: null
});

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-';
  const date = new Date(timeStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 获取排名数据
const fetchRankingData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const data = await getProblemRanking(props.problemId, props.exerciseId, props.classId);
    rankingData.value = data;
  } catch (err) {
    console.error('获取排名失败:', err);
    error.value = '获取排名数据失败，请稍后重试';
    ElMessage.error('获取排名数据失败');
  } finally {
    loading.value = false;
  }
};

// 获取排名样式
const getRankClass = (index) => {
  if (index === 0) return 'rank-first';
  if (index === 1) return 'rank-second';
  if (index === 2) return 'rank-third';
  return '';
};

onMounted(() => {
  fetchRankingData();
});

// 分离已提交和未提交的学生
const submittedStudents = computed(() => {
  return rankingData.value.rankings.filter(student => student.status !== "未提交");
});

const unsubmittedStudents = computed(() => {
  return rankingData.value.rankings.filter(student => student.status === "未提交");
});
</script>

<style scoped>
.problem-ranking-container {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.ranking-content {
  padding: 28px;
}

.loading, .error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #909399;
  font-size: 16px;
}

.error {
  color: #f56c6c;
}

/* 头部样式 */
.ranking-header {
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f2f5;
}

.problem-title {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  line-height: 1.4;
}

.ranking-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 6px;
}

.stat-value {
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.stat-item.highlight .stat-value {
  color: #409eff;
}

/* 特殊卡片区域 */
.special-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
}

.card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.teacher-card {
  border: 1px solid rgba(64, 158, 255, 0.15);
}

.user-card {
  border: 1px solid rgba(103, 194, 58, 0.15);
}

.card-header {
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.teacher-card .card-header {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.user-card .card-header {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.card-icon {
  font-size: 18px;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
}

.card-body {
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 18px;
}

.submission-score {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  background-color: #f5f7fa;
  width: 68px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}

.submission-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-grow: 1;
}

.submission-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.submission-meta {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 14px;
}

/* 排名列表样式 */
.ranking-list-container {
  margin-bottom: 28px;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 40px 0;
  font-size: 16px;
}

.ranking-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  background-color: #f5f7fa;
  font-weight: 500;
  color: #606266;
}

.table-body {
  border: 1px solid #f0f2f5;
  border-top: none;
}

.table-row {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #f0f2f5;
  transition: background-color 0.2s;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background-color: #f9fafc;
}

.table-row.current-user {
  background-color: rgba(64, 158, 255, 0.08);
}

.col-rank {
  width: 80px;
  text-align: center;
}

.col-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px;
}

.col-score {
  width: 100px;
  text-align: center;
  font-weight: 500;
}

.col-status {
  width: 140px;
  text-align: center;
}

.col-time {
  width: 180px;
  text-align: right;
  color: #909399;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: 600;
  color: #606266;
  background-color: #f5f7fa;
}

.rank-first {
  background-color: #f56c6c;
  color: white;
}

.rank-second {
  background-color: #e6a23c;
  color: white;
}

.rank-third {
  background-color: #409eff;
  color: white;
}

/* 未提交分割线 */
.divider {
  padding: 12px 20px;
  background-color: #fdf6ec;
  color: #e6a23c;
  font-size: 14px;
  text-align: center;
  border-bottom: 1px solid #f0f2f5;
}

.table-row.unsubmitted {
  background-color: #fafafa;
  color: #909399;
}

.table-row.unsubmitted:hover {
  background-color: #f5f5f5;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.action-button {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  background-color: #409eff;
  color: white;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
}

.action-button:hover {
  background-color: #66b1ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ranking-content {
    padding: 20px;
  }
  
  .problem-title {
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .table-header, 
  .table-row {
    padding: 12px 16px;
  }
  
  .col-rank {
    width: 60px;
  }
  
  .col-score {
    width: 80px;
  }
  
  .col-status {
    width: 100px;
  }
  
  .col-time {
    width: 120px;
    font-size: 12px;
  }
}
</style> 