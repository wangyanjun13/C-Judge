<template>
  <div class="active-students-monitor">
    <div class="header">
      <h3>{{ exerciseName }} - 当前练习-实时答题监控</h3>
      <div class="filter-section" v-if="classes.length > 1">
        <label for="class-select">班级：</label>
        <select id="class-select" v-model="selectedClassId" @change="fetchActiveStudents">
          <option value="">全部班级</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }}
          </option>
        </select>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="!activeStudents.length" class="empty-data">
      <p>暂无学生在线答题</p>
    </div>
    <div v-else class="active-students-table-container">
      <div class="summary">
        <div class="summary-item">
          <span class="label">在线学生：</span>
          <span class="value">{{ onlineStudentsCount }}</span>
        </div>
        <div class="summary-item">
          <span class="label">活跃学生：</span>
          <span class="value">{{ activeStudents.length }}</span>
        </div>
      </div>
      
      <table class="active-students-table">
        <thead>
          <tr>
            <th>学生</th>
            <th>班级</th>
            <th>在线状态</th>
            <th>活动时间</th>
            <th>完成题目数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in activeStudents" :key="student.student_id">
            <td>{{ student.real_name }} ({{ student.username }})</td>
            <td>{{ formatClassList(student.class_names) }}</td>
            <td>
              <span 
                class="badge" 
                :class="student.is_online ? 'badge-success' : 'badge-secondary'"
              >
                {{ student.is_online ? '在线' : '离线' }}
              </span>
            </td>
            <td>
              <div class="activity-time">
                <div>{{ student.latest_activity }}</div>
                <div class="time-ago">{{ student.last_active_time_ago }}</div>
              </div>
            </td>
            <td>{{ student.completed_problems_count }} / {{ student.total_problems_count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { getExerciseActiveStudents } from '../api/exercises';
import { ElMessage } from 'element-plus';

const props = defineProps({
  exerciseId: {
    type: [Number, String],
    required: true
  },
  exerciseName: {
    type: String,
    default: '练习'
  },
  refreshInterval: {
    type: Number,
    default: 5000 // 默认5秒刷新一次，更频繁地更新活动状态
  }
});

const loading = ref(true);
const error = ref(null);
const activeStudents = ref([]);
const classes = ref([]);
const selectedClassId = ref('');
const refreshTimer = ref(null);

// 计算在线学生数量
const onlineStudentsCount = computed(() => {
  return activeStudents.value.filter(student => student.is_online).length;
});

// 获取活跃学生数据
const fetchActiveStudents = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const data = await getExerciseActiveStudents(props.exerciseId, selectedClassId.value || null);
    activeStudents.value = data;
    
    // 提取班级信息
    const uniqueClasses = new Map();
    data.forEach(student => {
      student.class_names.forEach(className => {
        // 假设className格式为"班级名称 (ID)"
        const match = className.match(/(.+) \((\d+)\)/);
        if (match) {
          uniqueClasses.set(parseInt(match[2]), match[1]);
        }
      });
    });
    
    classes.value = Array.from(uniqueClasses.entries()).map(([id, name]) => ({ id, name }));
  } catch (err) {
    console.error('获取活跃学生数据失败:', err);
    error.value = err.response?.data?.detail || '获取活跃学生数据失败，请稍后重试';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
};

// 格式化班级列表
const formatClassList = (classList) => {
  if (!classList || classList.length === 0) return '-';
  return classList.join(', ');
};

// 格式化日期时间
const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return '-';
  try {
    const date = new Date(dateTimeString);
    if (isNaN(date.getTime())) return dateTimeString;
    
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    }).format(date);
  } catch (error) {
    console.error('日期格式化错误:', error);
    return dateTimeString;
  }
};

// 计算进度百分比
const calculateProgressPercentage = (student) => {
  if (!student.total_problems_count) return 0;
  return (student.completed_problems_count / student.total_problems_count) * 100;
};

// 获取进度条样式类
const getProgressClass = (student) => {
  const percentage = calculateProgressPercentage(student);
  if (percentage >= 100) return 'complete';
  if (percentage >= 50) return 'half';
  return 'start';
};

// 设置定时刷新
const setupRefreshInterval = () => {
  refreshTimer.value = setInterval(() => {
    fetchActiveStudents();
  }, props.refreshInterval);
};

onMounted(() => {
  fetchActiveStudents();
  setupRefreshInterval();
});

onUnmounted(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value);
  }
});
</script>

<style scoped>
.active-students-monitor {
  width: 100%;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.header h3 {
  margin: 0;
  color: #303133;
}

.filter-section {
  display: flex;
  align-items: center;
}

.filter-section label {
  margin-right: 8px;
  white-space: nowrap;
}

.filter-section select {
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fff;
  min-width: 120px;
}

.loading, .error, .empty-data {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.error {
  color: #f56c6c;
}

.summary {
  display: flex;
  margin-bottom: 15px;
  gap: 20px;
}

.summary-item {
  background-color: #f5f7fa;
  padding: 10px 15px;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.summary-item .label {
  color: #606266;
  margin-right: 8px;
}

.summary-item .value {
  color: #409eff;
  font-weight: bold;
  font-size: 18px;
}

.active-students-table-container {
  overflow-x: auto;
}

.active-students-table {
  width: 100%;
  border-collapse: collapse;
}

.active-students-table th, .active-students-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.active-students-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.online {
  background-color: #67c23a;
  color: white;
}

.status-badge.offline {
  background-color: #909399;
  color: white;
}

.progress-cell {
  width: 180px;
}

.progress-bar-container {
  background-color: #f5f7fa;
  height: 20px;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background-color: #409eff;
  transition: width 0.3s ease;
}

.progress-bar.start {
  background-color: #e6a23c;
}

.progress-bar.half {
  background-color: #409eff;
}

.progress-bar.complete {
  background-color: #67c23a;
}

.progress-text {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #303133;
  font-size: 12px;
}

.time-ago {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.activity-time {
  display: flex;
  flex-direction: column;
}

.badge {
  padding: 5px 8px;
  border-radius: 4px;
}

.badge-success {
  background-color: #28a745;
  color: white;
}

.badge-secondary {
  background-color: #6c757d;
  color: white;
}
</style> 