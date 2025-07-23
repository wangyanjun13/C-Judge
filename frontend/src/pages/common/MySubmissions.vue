<template>
  <div class="my-submissions-container">
    <h2>我的答题记录</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="submissions.length === 0" class="empty">暂无答题记录</div>
    <div v-else>
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
          <tr v-for="item in submissions" :key="item.id">
            <td>{{ item.problem_name }}{{ item.problem_chinese_name ? `(${item.problem_chinese_name})` : '' }}</td>
            <td>{{ item.total_score ?? 0 }}</td>
            <td>{{ item.exercise_name || '-' }}</td>
            <td>{{ item.course_name || '-' }}</td>
            <td>{{ item.class_names || '-' }}</td>
            <td>{{ formatDate(item.submitted_at) }}</td>
            <td>
              <button class="ranking-btn" @click="showRanking(item)">查看</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <el-dialog v-model="rankingDialog.visible" title="班级排名" width="80%" destroy-on-close :close-on-click-modal="true">
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
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../../store/auth';
import { getMySubmissions } from '../../api/submissions';
import ProblemRanking from '../../components/ProblemRanking.vue';
import { ElMessage } from 'element-plus';

const authStore = useAuthStore();
const loading = ref(true);
const error = ref(null);
const submissions = ref([]);
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

onMounted(() => {
  fetchSubmissions();
});
</script>

<style scoped>
.my-submissions-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  min-height: 60vh;
}
.loading, .error, .empty {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}
.error { color: #f56c6c; }
.submissions-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
.submissions-table th, .submissions-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #ebeef5;
  text-align: center;
}
.submissions-table th {
  background: #f5f7fa;
  color: #606266;
  font-weight: 500;
}
.ranking-btn {
  padding: 4px 10px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}
.ranking-btn:hover {
  background: #66b1ff;
}
</style> 