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
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 24px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
  flex-wrap: wrap;
  gap: 16px;
}

.header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.filter-section {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.8);
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.filter-section label {
  margin-right: 12px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
}

.filter-section select {
  padding: 8px 16px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: var(--radius-sm);
  min-width: 150px;
  background-color: white;
  color: var(--text-primary);
  font-size: 14px;
  transition: var(--transition-fast);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-section select:hover {
  border-color: var(--primary-color);
}

.filter-section select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.loading, .error, .empty-data {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.error {
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.05);
  border: 1px solid rgba(245, 108, 108, 0.2);
}

.summary {
  display: flex;
  margin-bottom: 20px;
  gap: 20px;
  flex-wrap: wrap;
}

.summary-item {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  padding: 16px 20px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: var(--shadow-sm);
  min-width: 180px;
}

.summary-item .label {
  color: var(--text-primary);
  margin-right: 12px;
  font-weight: 500;
}

.summary-item .value {
  color: var(--primary-color);
  font-weight: bold;
  font-size: 24px;
}

.active-students-table-container {
  overflow-x: auto;
}

.active-students-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  background: white;
}

.active-students-table th, .active-students-table td {
  padding: 14px 18px;
  text-align: left;
}

.active-students-table th {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  color: var(--text-primary);
  font-weight: 600;
  font-size: 14px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.active-students-table td {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  color: var(--text-primary);
  font-size: 14px;
}

.active-students-table tr:last-child td {
  border-bottom: none;
}

.active-students-table tr:hover td {
  background-color: rgba(102, 126, 234, 0.05);
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
}

.badge-success {
  background: linear-gradient(135deg, #67c23a, #529b2e);
  color: white;
  box-shadow: 0 2px 4px rgba(103, 194, 58, 0.2);
}

.badge-secondary {
  background: linear-gradient(135deg, #909399, #606266);
  color: white;
}

.activity-time {
  display: flex;
  flex-direction: column;
}

.time-ago {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
  background-color: rgba(102, 126, 234, 0.05);
  padding: 2px 6px;
  border-radius: 10px;
  display: inline-block;
}
</style> 