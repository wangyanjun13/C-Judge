<template>
  <div class="statistics-container">
    <div class="header">
      <h3>{{ exerciseName }} - 答题统计</h3>
      <div class="filter-section" v-if="classes.length > 1">
        <label for="class-select">班级：</label>
        <select id="class-select" v-model="selectedClassId" @change="fetchStatistics">
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
    <div v-else-if="!statistics.length && !specialUsers.length" class="empty-data">
      <p>暂无答题数据</p>
    </div>
    <div v-else class="statistics-content">
      <!-- 左侧统计表格 -->
      <div class="statistics-table-wrapper">
        <table class="statistics-table">
          <thead>
            <tr>
              <th class="fixed-column">序号</th>
              <th class="fixed-column">用户名</th>
              <th class="fixed-column">班级/角色</th>
              <th class="fixed-column">总分</th>
              <th v-for="problem in problems" :key="problem.id" class="problem-column">
                {{ problem.name }}
                <div class="problem-info">{{ problem.chinese_name }}</div>
                <div class="problem-score">{{ problem.total_score }}分</div>
              </th>
            </tr>
          </thead>
          <tbody>
            <!-- 管理员和教师答题情况 -->
            <tr v-for="user in specialUsers" :key="user.user_id" class="special-user-row">
              <td class="fixed-column">-</td>
              <td class="fixed-column">{{ user.username }}{{ user.real_name ? ` (${user.real_name})` : '' }}</td>
              <td class="fixed-column">{{ user.role === 'admin' ? '管理员' : '授课教师' }}</td>
              <td class="fixed-column total-score">{{ user.total_score || 0 }}</td>
              <td 
                v-for="problem in problems" 
                :key="`${user.user_id}-${problem.id}`"
                :class="getScoreClass(user.problem_scores[problem.id])"
                @click="viewSubmission(user.user_id, problem.id, user.problem_scores[problem.id], user.role, user.username)"
                class="score-cell"
              >
                <template v-if="user.problem_scores && user.problem_scores[problem.id]">
                  <template v-if="user.problem_scores[problem.id].score !== null">
                    <span class="clickable-score">{{ user.problem_scores[problem.id].score }}</span>
                  </template>
                  <template v-else>
                    <span class="not-submitted">未提交</span>
                  </template>
                </template>
                <template v-else>
                  <span class="not-submitted">未提交</span>
                </template>
              </td>
            </tr>
            
            <!-- 分隔行 -->
            <tr v-if="specialUsers.length > 0 && statistics.length > 0" class="divider-row">
              <td colspan="100%" class="divider-cell">
                <div class="divider-text">班级学生</div>
              </td>
            </tr>
            
            <!-- 学生答题情况 -->
            <tr v-for="student in statistics" :key="student.student_id">
              <td class="fixed-column">{{ student.rank }}</td>
              <td class="fixed-column">{{ student.username }}{{ student.real_name ? ` (${student.real_name})` : '' }}</td>
              <td class="fixed-column">{{ formatClassNames(student.class_names) }}</td>
              <td class="fixed-column total-score">{{ student.total_score || 0 }}</td>
              <td 
                v-for="problem in problems" 
                :key="`${student.student_id}-${problem.id}`"
                :class="getScoreClass(student.problem_scores[problem.id])"
                @click="viewSubmission(student.student_id, problem.id, student.problem_scores[problem.id], 'student', student.username)"
                class="score-cell"
              >
                <template v-if="student.problem_scores && student.problem_scores[problem.id]">
                  <template v-if="student.problem_scores[problem.id].score !== null">
                    <span class="clickable-score">{{ student.problem_scores[problem.id].score }}</span>
                  </template>
                  <template v-else>
                    <span class="not-submitted">未提交</span>
                  </template>
                </template>
                <template v-else>
                  <span class="not-submitted">未提交</span>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getExerciseStatistics } from '../api/exercises';
import { useAuthStore } from '../store/auth';

const props = defineProps({
  exerciseId: {
    type: [Number, String],
    required: true
  },
  includeSpecialUsers: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['close']);
const router = useRouter();
const authStore = useAuthStore();

const loading = ref(true);
const error = ref(null);
const exerciseName = ref('');
const problems = ref([]);
const classes = ref([]);
const statistics = ref([]);
const specialUsers = ref([]); // 管理员和当前教师
const selectedClassId = ref('');

// 获取统计数据
const fetchStatistics = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const data = await getExerciseStatistics(props.exerciseId, selectedClassId.value || null, props.includeSpecialUsers);
    
    // 更新组件数据
    exerciseName.value = data.exercise_name;
    problems.value = data.problems;
    classes.value = data.classes;
    
    // 分离特殊用户（管理员和教师）和学生
    if (data.statistics && data.statistics.length > 0) {
      // 过滤出管理员和教师
      specialUsers.value = data.statistics.filter(user => 
        user.role === 'admin' || user.role === 'teacher'
      );
      
      // 过滤出学生
      statistics.value = data.statistics.filter(user => 
        !user.role || user.role === 'student'
      );
      
      // 如果没有特殊用户数据，但当前用户是管理员或教师，则添加当前用户
      if (specialUsers.value.length === 0 && (authStore.userRole === 'admin' || authStore.userRole === 'teacher')) {
        // 检查当前用户是否已经在特殊用户列表中
        const currentUserExists = specialUsers.value.some(u => u.user_id === authStore.user.id);
        
        if (!currentUserExists) {
          // 创建一个空的问题得分对象
          const emptyProblemScores = {};
          problems.value.forEach(problem => {
            emptyProblemScores[problem.id] = {
              score: null,
              submission_id: null,
              status: "未提交"
            };
          });
          
          // 添加当前用户到特殊用户列表
          specialUsers.value.push({
            user_id: authStore.user.id,
            username: authStore.user.username,
            real_name: authStore.user.real_name || '',
            role: authStore.userRole,
            total_score: 0,
            problem_scores: emptyProblemScores
          });
          
          console.log('添加当前用户到特殊用户列表:', specialUsers.value);
        }
      }
      
      // 如果是管理员登录，确保相关教师也在特殊用户列表中
      if (authStore.userRole === 'admin' && data.course_teacher && !specialUsers.value.some(u => u.user_id === data.course_teacher.id)) {
        // 创建一个空的问题得分对象
        const emptyProblemScores = {};
        problems.value.forEach(problem => {
          emptyProblemScores[problem.id] = {
            score: null,
            submission_id: null,
            status: "未提交"
          };
        });
        
        // 添加课程教师到特殊用户列表
        specialUsers.value.push({
          user_id: data.course_teacher.id,
          username: data.course_teacher.username,
          real_name: data.course_teacher.real_name || '',
          role: 'teacher',
          total_score: 0,
          problem_scores: emptyProblemScores
        });
        
        console.log('添加课程教师到特殊用户列表:', specialUsers.value);
      }
      
      console.log('特殊用户:', specialUsers.value);
      console.log('学生:', statistics.value);
    } else {
      specialUsers.value = [];
      statistics.value = [];
      
      // 如果没有任何统计数据，但当前用户是管理员或教师，则添加当前用户
      if (authStore.userRole === 'admin' || authStore.userRole === 'teacher') {
        // 创建一个空的问题得分对象
        const emptyProblemScores = {};
        problems.value.forEach(problem => {
          emptyProblemScores[problem.id] = {
            score: null,
            submission_id: null,
            status: "未提交"
          };
        });
        
        // 添加当前用户到特殊用户列表
        specialUsers.value.push({
          user_id: authStore.user.id,
          username: authStore.user.username,
          real_name: authStore.user.real_name || '',
          role: authStore.userRole,
          total_score: 0,
          problem_scores: emptyProblemScores
        });
        
        console.log('添加当前用户到特殊用户列表（无数据情况）:', specialUsers.value);
      }
    }
  } catch (err) {
    console.error('获取统计数据失败:', err);
    error.value = err.response?.data?.detail || '获取统计数据失败，请稍后重试';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
};

// 格式化班级名称
const formatClassNames = (classNames) => {
  if (!classNames || classNames.length === 0) return '无班级';
  return classNames.join(', ');
};

// 获取分数单元格的样式类
const getScoreClass = (scoreData) => {
  if (!scoreData || scoreData.score === null) {
    return 'not-submitted-cell';
  }
  
  const score = scoreData.score;
  if (score >= 90) {
    return 'excellent-score';
  } else if (score >= 80) {
    return 'good-score';
  } else if (score >= 60) {
    return 'pass-score';
  } else {
    return 'fail-score';
  }
};

// 查看提交详情
const viewSubmission = (userId, problemId, scoreData, role, username) => {
  if (!scoreData || !scoreData.submission_id) {
    ElMessage.info('该用户未提交此题');
    return;
  }
  
  try {
    // 查找用户的真实姓名
    let realName = '';
    
    // 从specialUsers或statistics中查找用户信息
    if (role === 'admin' || role === 'teacher') {
      const user = specialUsers.value.find(u => u.user_id === userId);
      if (user) {
        realName = user.real_name || '';
      }
    } else {
      const student = statistics.value.find(s => s.student_id === userId);
      if (student) {
        realName = student.real_name || '';
      }
    }
    
    // 构建查看提交详情的路由路径
    const routePath = `/submission-detail/${scoreData.submission_id}?problem_id=${problemId}&user_id=${userId}&exercise_id=${props.exerciseId}&username=${encodeURIComponent(username)}&real_name=${encodeURIComponent(realName)}`;
    
    // 使用路由导航而不是打开新窗口
    router.push(routePath).catch(err => {
      console.error('导航失败:', err);
      ElMessage.error('页面导航失败，请稍后重试');
    });
  } catch (err) {
    console.error('查看提交详情失败:', err);
    ElMessage.error('操作失败，请稍后重试');
  }
};

onMounted(() => {
  fetchStatistics();
});
</script>

<style scoped>
.statistics-container {
  background-color: #fff;
  border-radius: 8px;
  padding: 0;
  height: 60vh;
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.filter-section {
  display: flex;
  align-items: center;
}

.filter-section label {
  margin-right: 10px;
  font-weight: 500;
}

.filter-section select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-width: 150px;
}

.loading, .error, .empty-data {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error {
  color: #f56c6c;
}

.statistics-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.statistics-table-wrapper {
  flex: 1;
  overflow: auto;
  position: relative;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.statistics-table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
}

.statistics-table th, .statistics-table td {
  padding: 12px 15px;
  text-align: center;
  border: 1px solid #ebeef5;
}

.statistics-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
  position: sticky;
  top: 0;
  z-index: 10;
}

.fixed-column {
  position: sticky;
  left: 0;
  background-color: #f5f7fa;
  z-index: 5;
}

.statistics-table td.fixed-column {
  background-color: #fff;
}

/* 增加用户名列的宽度 */
.statistics-table th:nth-child(2),
.statistics-table td:nth-child(2) {
  min-width: 180px;
  max-width: 250px;
  white-space: normal;
  word-break: break-word;
}

.problem-column {
  min-width: 120px;
}

.problem-info {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.problem-score {
  font-size: 12px;
  color: #409eff;
  margin-top: 3px;
}

.total-score {
  font-weight: bold;
  color: #303133;
}

.not-submitted {
  color: #909399;
  font-style: italic;
}

.not-submitted-cell {
  background-color: #f8f8f8;
}

.excellent-score {
  background-color: #f0f9eb;
  color: #67c23a;
  font-weight: bold;
}

.good-score {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: bold;
}

.pass-score {
  background-color: #fdf6ec;
  color: #e6a23c;
  font-weight: bold;
}

.fail-score {
  background-color: #fef0f0;
  color: #f56c6c;
  font-weight: bold;
}

/* 特殊用户行样式 */
.special-user-row {
  background-color: #f2f6fc;
}

.special-user-row td.fixed-column {
  background-color: #f2f6fc;
}

/* 如果有特殊用户，添加一个分隔行 */
.special-user-row:last-child {
  border-bottom: 2px solid #409eff;
}

/* 可点击分数样式 */
.score-cell {
  cursor: pointer;
  transition: all 0.3s;
}

.score-cell:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.clickable-score {
  position: relative;
}

.clickable-score::after {
  content: "";
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: currentColor;
}

/* 美化滚动条 */
.statistics-table-wrapper::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.statistics-table-wrapper::-webkit-scrollbar-thumb {
  background-color: #909399;
  border-radius: 4px;
}

.statistics-table-wrapper::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

/* 分隔行样式 */
.divider-row {
  background-color: #e8f4ff;
}

.divider-cell {
  padding: 8px 15px;
  text-align: center;
  border: 1px solid #c6e2ff;
  background-color: #e8f4ff;
}

.divider-text {
  font-weight: bold;
  color: #409eff;
  font-size: 14px;
}
</style> 