<template>
  <div class="logs-container">
    <h2>操作记录</h2>
    
    <div class="filter-section">
      <div class="date-filters">
        <div class="filter-item">
          <label for="start-date">开始日期：</label>
          <input 
            type="date" 
            id="start-date" 
            v-model="filters.startDate"
            @change="fetchLogs"
          />
        </div>
        <div class="filter-item">
          <label for="end-date">结束日期：</label>
          <input 
            type="date" 
            id="end-date" 
            v-model="filters.endDate"
            @change="fetchLogs"
          />
        </div>
        <button class="btn btn-primary" @click="clearFilters">清除筛选</button>
        <button class="btn btn-danger" @click="confirmClearAllLogs">清空所有记录</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    <div v-else-if="logs.length === 0" class="empty-state">
      暂无操作记录
    </div>
    <div v-else class="logs-table-container">
      <table class="logs-table">
        <thead>
          <tr>
            <th>操作时间</th>
            <th>操作类型</th>
            <th>操作对象</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ formatDateTime(log.created_at) }}</td>
            <td class="operation-type">{{ log.operation }}</td>
            <td>{{ log.target || '-' }}</td>
          </tr>
        </tbody>
      </table>
      
      <div class="pagination">
        <button 
          class="btn btn-page" 
          :disabled="currentPage === 1" 
          @click="prevPage"
        >
          上一页
        </button>
        <span class="page-info">第 {{ currentPage }} 页</span>
        <button 
          class="btn btn-page" 
          :disabled="logs.length < pageSize" 
          @click="nextPage"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { getUserOperationLogs, clearAllOperationLogs } from '../../api/operation_logs';
import { ElMessage, ElMessageBox } from 'element-plus';

const logs = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = 20;
const filters = ref({
  startDate: '',
  endDate: ''
});
const refreshInterval = ref(null);

// 获取操作日志
const fetchLogs = async () => {
  loading.value = true;
  
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
      sort: 'desc' // 按时间降序排列，最新的在最上面
    };
    
    if (filters.value.startDate) {
      params.start_date = filters.value.startDate;
    }
    
    if (filters.value.endDate) {
      params.end_date = filters.value.endDate;
    }
    
    logs.value = await getUserOperationLogs(params);
  } catch (error) {
    console.error('获取操作日志失败:', error);
    ElMessage.error('获取操作日志失败');
  } finally {
    loading.value = false;
  }
};

// 格式化日期时间
const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return '-';
  try {
    // 解析ISO格式的时间字符串，这会自动处理时区
    const date = new Date(dateTimeString);
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      return dateTimeString; // 如果无效，返回原始字符串
    }
    
    // 使用本地时区格式化日期
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone // 使用浏览器的本地时区
    }).format(date);
  } catch (error) {
    console.error('日期格式化错误:', error);
    return dateTimeString;
  }
};

// 上一页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchLogs();
  }
};

// 下一页
const nextPage = () => {
  currentPage.value++;
  fetchLogs();
};

// 清除筛选条件
const clearFilters = () => {
  filters.value = {
    startDate: '',
    endDate: ''
  };
  currentPage.value = 1;
  fetchLogs();
};

// 确认清空所有日志
const confirmClearAllLogs = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有操作记录吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    await clearAllOperationLogs();
    ElMessage.success('已清空所有操作记录');
    fetchLogs(); // 重新获取日志列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空操作记录失败:', error);
      ElMessage.error('清空操作记录失败');
    }
  }
};

// 设置定时刷新
const setupRefreshInterval = () => {
  // 每30秒刷新一次数据
  refreshInterval.value = setInterval(() => {
    fetchLogs();
  }, 30000);
};

onMounted(() => {
  fetchLogs();
  setupRefreshInterval();
});

onUnmounted(() => {
  // 清除定时器
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value);
  }
});
</script>

<style scoped>
.logs-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.filter-section {
  margin-bottom: 20px;
}

.date-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-item {
  display: flex;
  align-items: center;
}

.filter-item label {
  margin-right: 8px;
  white-space: nowrap;
}

.filter-item input {
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.loading, .empty-state {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.logs-table-container {
  overflow-x: auto;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th, .logs-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.logs-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.operation-type {
  color: #67c23a;
  font-weight: 500;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #66b1ff;
}

.btn-danger {
  background-color: #f56c6c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #f78989;
}

.btn-page {
  background-color: #f4f4f5;
  color: #606266;
}

.btn-page:hover:not(:disabled) {
  background-color: #e9e9eb;
}

.page-info {
  color: #606266;
}
</style> 