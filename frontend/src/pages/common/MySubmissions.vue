<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div class="header-content">
        <div class="title-section">
          <h2 class="dashboard-title">
            <span class="title-icon">📊</span>
            答题仪表盘
          </h2>
          <p class="dashboard-subtitle">跟踪学习进度和答题表现</p>
        </div>
        <div class="header-decoration">
          <div class="decoration-circle"></div>
          <div class="decoration-circle small"></div>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载您的答题数据...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>数据加载失败</h3>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="() => { isFetching.value = false; fetchSubmissions(); }">重新加载</button>
    </div>
    
    <div v-else-if="submissions.length === 0" class="empty-container">
      <div class="empty-illustration">
      <div class="empty-icon">📝</div>
        <div class="empty-bg-circles">
          <div class="bg-circle"></div>
          <div class="bg-circle"></div>
        </div>
      </div>
      <h3>开始您的编程之旅</h3>
      <p>您还没有提交过任何题目</p>
      <p class="empty-hint">完成题目后，您的答题记录将显示在这里</p>
    </div>
    
    <div v-else class="dashboard-content">
      <!-- 学生版：个人数据概览 -->
      <div v-if="authStore.user.role === 'student'" class="stats-section">
        <h3 class="section-title">个人数据概览</h3>
      <div class="stats-cards">
          <div class="stat-card primary">
            <div class="stat-icon">📚</div>
            <div class="stat-info">
              <div class="stat-value">{{ authStore.user.role === 'student' ? submissions.length : (showAllSubmissions ? allSubmissionsCount : mySubmissions.length) }}</div>
              <div class="stat-label">{{ authStore.user.role === 'student' ? '已答题目' : (showAllSubmissions ? '总提交数' : '已答题目') }}</div>
            </div>
            <div class="stat-trend">{{ authStore.user.role === 'student' ? '+' + submissions.length : (showAllSubmissions ? '全部记录' : '+' + mySubmissions.length) }}</div>
          </div>
          <div class="stat-card success">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
          <div class="stat-value">{{ averageScore }}</div>
          <div class="stat-label">平均分</div>
        </div>
            <div class="stat-trend" :class="averageScore >= 80 ? 'positive' : 'neutral'">
              {{ averageScore >= 80 ? '优秀' : '良好' }}
            </div>
          </div>
          <div class="stat-card warning">
            <div class="stat-icon">🏆</div>
            <div class="stat-info">
          <div class="stat-value">{{ highestScore }}</div>
          <div class="stat-label">最高分</div>
        </div>
            <div class="stat-trend positive">最佳</div>
          </div>
          <div class="stat-card info">
            <div class="stat-icon">📋</div>
            <div class="stat-info">
              <div class="stat-value">{{ completedExercises }}</div>
              <div class="stat-label">参与练习</div>
            </div>
            <div class="stat-trend">{{ completedExercises }}个</div>
          </div>
        </div>
      </div>
      
      <!-- 管理员/教师版：监控概览 -->
      <div v-else class="stats-section">
        <div class="section-header-with-toggle">
          <h3 class="section-title">
            {{ authStore.user.role === 'admin' ? '全校监控概览' : '班级监控概览' }}
          </h3>
          <div class="view-toggle">
            <button 
              class="toggle-btn" 
              :class="{ active: showAllSubmissions }"
              @click="showAllSubmissions = true"
            >
              监控模式
            </button>
            <button 
              class="toggle-btn" 
              :class="{ active: !showAllSubmissions }"
              @click="showAllSubmissions = false"
            >
              个人模式
            </button>
          </div>
        </div>
        <div class="stats-cards">
          <div class="stat-card primary">
            <div class="stat-icon">👥</div>
            <div class="stat-info">
              <div class="stat-value">{{ allStudentsCount }}</div>
              <div class="stat-label">管理学生</div>
            </div>
            <div class="stat-trend">{{ authStore.user.role === 'admin' ? '全校' : '所辖班级' }}</div>
          </div>
          <div class="stat-card success">
            <div class="stat-icon">📝</div>
            <div class="stat-info">
              <div class="stat-value">{{ allSubmissionsCount }}</div>
              <div class="stat-label">总提交数</div>
            </div>
            <div class="stat-trend positive">{{ activeStudentsCount }}人活跃</div>
          </div>
          <div class="stat-card warning">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <div class="stat-value">{{ Math.round(overallPassRate) }}%</div>
              <div class="stat-label">整体通过率</div>
            </div>
            <div class="stat-trend" :class="overallPassRate >= 80 ? 'positive' : 'neutral'">
              {{ overallPassRate >= 80 ? '优秀' : '良好' }}
            </div>
          </div>
          <div class="stat-card info">
            <div class="stat-icon">📋</div>
            <div class="stat-info">
              <div class="stat-value">{{ showAllSubmissions ? allSubmissionsCount : submissions.length }}</div>
              <div class="stat-label">{{ showAllSubmissions ? '所有提交' : '我的提交' }}</div>
            </div>
            <div class="stat-trend">{{ showAllSubmissions ? '监控数据' : '个人记录' }}</div>
          </div>
        </div>
      </div>
      
      <!-- 提交记录表格 -->
      <div class="records-section">
        <div class="section-header">
          <div class="header-left">
            <h3 class="section-title">
              <span v-if="authStore.user.role === 'student'">我的答题记录</span>
              <span v-else-if="showAllSubmissions && authStore.user.role === 'admin'">全校提交监控</span>
              <span v-else-if="showAllSubmissions">班级提交监控</span>
              <span v-else>我的答题记录</span>
            </h3>
            <span class="record-count">
              <span v-if="authStore.user.role === 'student'">共 {{ filteredSubmissions.length }} 条记录</span>
              <span v-else-if="showAllSubmissions">共 {{ filteredSubmissions.length }} 条提交记录</span>
              <span v-else>共 {{ filteredSubmissions.length }} 条个人记录</span>
            </span>
          </div>
          <div class="header-actions">
            <div class="filter-group">
              <label class="filter-label">筛选练习：</label>
          <select v-model="filterExercise" class="filter-select">
            <option value="">全部练习</option>
            <option v-for="ex in uniqueExercises" :key="ex.id" :value="ex.id">
              {{ ex.name }}
            </option>
          </select>
            </div>
        </div>
      </div>
      
      <div class="table-container">
          <div class="table-wrapper">
        <table class="submissions-table">
          <thead>
            <tr>
                  <th v-if="authStore.user.role !== 'student' && showAllSubmissions" class="col-student">学生信息</th>
                  <th class="col-problem">题目信息</th>
                  <th class="col-score">得分</th>
                  <th class="col-exercise">所属练习</th>
                  <th class="col-course">课程</th>
                  <th v-if="authStore.user.role === 'student'" class="col-class">班级</th>
                  <th class="col-time">提交时间</th>
                  <th class="col-ranking">
                    <span v-if="authStore.user.role === 'admin'">
                      班级排名情况<br><small>(管理员不参与排名，仅可查看)</small>
                    </span>
                    <span v-else-if="authStore.user.role === 'teacher'">
                      班级排名情况<br><small>(教师不参与排名，仅可查看)</small>
                    </span>
                    <span v-else>班级排名</span>
                  </th>
            </tr>
          </thead>
          <tbody>
                <tr v-for="item in filteredSubmissions" :key="item.id" 
                    class="table-row" :class="getScoreClass(item.total_score)">
                  <td v-if="authStore.user.role !== 'student' && showAllSubmissions" class="col-student">
                    <div class="student-info">
                      <div class="student-username">
                        {{ item.username || `用户${item.user_id}` }}
                      </div>
                      <div class="student-realname" v-if="item.real_name">
                        {{ item.real_name }}
                      </div>
                    </div>
                  </td>
                  <td class="col-problem">
                    <div class="problem-info">
                      <div class="problem-name">{{ item.problem_name }}</div>
                      <div class="problem-chinese" v-if="item.problem_chinese_name">
                        {{ item.problem_chinese_name }}
                      </div>
                    </div>
                  </td>
                  <td class="col-score">
                    <div class="score-badge" :class="getScoreBadgeClass(item.total_score)">
                      {{ item.total_score ?? 0 }}
                    </div>
                  </td>
                  <td class="col-exercise">
                    <span class="exercise-name">{{ item.exercise_name || '独立提交' }}</span>
                  </td>
                  <td class="col-course">
                    <span class="course-name">{{ item.course_name || '-' }}</span>
                  </td>
                  <td v-if="authStore.user.role === 'student'" class="col-class">
                    <span class="class-name">{{ item.class_names || '-' }}</span>
                  </td>
                  <td class="col-time">
                    <span class="time-text">{{ formatDate(item.submitted_at) }}</span>
                  </td>
                  <td class="col-ranking">
                    <div v-if="item.exercise_id" class="ranking-display" @click="showRanking(item)">
                      <span class="ranking-text" v-if="rankingCache[getRankingKey(item)]">
                        {{ rankingCache[getRankingKey(item)] }}
                      </span>
                      <span class="ranking-loading" v-else-if="loadingRankings[getRankingKey(item)]">
                        <span class="loading-dots">...</span>
                      </span>
                                             <span class="ranking-placeholder" v-else @click.stop="loadRanking(item)">
                         点击查看
                       </span>
                    </div>
                    <span v-else class="no-ranking">无排名</span>
              </td>
            </tr>
          </tbody>
        </table>
          </div>
        </div>
      </div>
    </div>
    
    <el-dialog v-model="rankingDialog.visible" title="班级排名详情" width="80%" destroy-on-close>
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
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '../../store/auth';
import { getMySubmissions, getProblemRanking, getAllSubmissions, getStudents } from '../../api/submissions';
import ProblemRanking from '../../components/ProblemRanking.vue';
import { ElMessage } from 'element-plus';



const authStore = useAuthStore();
const loading = ref(false);
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

// 排名缓存和加载状态
const rankingCache = ref({});
const loadingRankings = ref({});

// 管理员/教师监控数据
const allStudents = ref([]);
const allSubmissions = ref([]);
const allStudentsCount = ref(0);
const allSubmissionsCount = ref(0);
const activeStudentsCount = ref(0);
const overallPassRate = ref(0);
const showAllSubmissions = ref(true); // 管理员/教师是否显示所有提交记录
const mySubmissions = ref([]); // 个人提交记录缓存

// 格式化时间
const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 获取排名缓存键
const getRankingKey = (item) => {
  return `${item.problem_id}-${item.exercise_id}`;
};

// 加载特定项目的排名信息
const loadRanking = async (item) => {
  const key = getRankingKey(item);
  if (rankingCache.value[key] || loadingRankings.value[key]) return;
  
  loadingRankings.value[key] = true;
  
  try {
    const rankingData = await getProblemRanking(item.problem_id, item.exercise_id, item.class_id);
    
    const currentUserRank = rankingData.current_user_rank;
    const totalStudents = rankingData.total_students;
    const submissionCount = rankingData.submission_count;
    const userRole = authStore.user.role;
    
    if (userRole === 'student' && currentUserRank && totalStudents > 0) {
      // 学生显示个人排名
      rankingCache.value[key] = `${currentUserRank}/${totalStudents}`;
    } else if (totalStudents > 0 && submissionCount > 0) {
      // 管理员和教师显示提交情况
      rankingCache.value[key] = `${submissionCount}/${totalStudents}`;
    } else if (totalStudents > 0) {
      rankingCache.value[key] = `0/${totalStudents}`;
    } else {
      rankingCache.value[key] = '暂无数据';
    }
  } catch (error) {
    console.error('获取排名失败:', error);
    rankingCache.value[key] = '获取失败';
  } finally {
    loadingRankings.value[key] = false;
  }
};

// 监控数据加载状态
const isMonitoringDataLoaded = ref(false);

// 获取监控数据（管理员/教师）
const fetchMonitoringData = async () => {
  if (authStore.user.role === 'student' || isMonitoringDataLoaded.value) return;
  
  try {
    let students, allSubs;
    
    if (authStore.user.role === 'admin') {
      // 管理员获取全校数据
      [students, allSubs] = await Promise.all([
        getStudents(),
        getAllSubmissions()
      ]);
    } else {
      // 教师只获取自己管辖范围的数据
      [students, allSubs] = await Promise.all([
        getStudents(), // 依赖后端根据JWT token自动识别教师权限并过滤班级学生
        getAllSubmissions({ scope: 'teacher' }) // 传递scope参数告诉后端只返回教师管辖范围的数据
      ]);
    }
    
    // 设置学生数据
    allStudents.value = students;
    allStudentsCount.value = students.length;
    
    // 设置提交记录数据
    // 对于教师，筛选只属于其管辖学生的提交记录
    if (authStore.user.role === 'teacher') {
      const teacherStudentIds = new Set(students.map(student => student.id));
      allSubs = allSubs.filter(sub => teacherStudentIds.has(sub.user_id));
    }
    
    allSubmissions.value = allSubs;
    allSubmissionsCount.value = allSubs.length;
    
    // 计算活跃学生数（有提交记录的学生）
    const activeStudentIds = new Set(allSubs.map(sub => sub.user_id));
    activeStudentsCount.value = activeStudentIds.size;
    
    // 计算整体通过率（60分以上算通过）
    const passedSubmissions = allSubs.filter(sub => (sub.total_score || 0) >= 60);
    overallPassRate.value = allSubs.length > 0 ? (passedSubmissions.length / allSubs.length) * 100 : 0;
    
    isMonitoringDataLoaded.value = true;
    
  } catch (error) {
    console.error('获取监控数据失败:', error);
    ElMessage.error('获取监控数据失败');
  }
};

// 防止重复加载的标志
const isFetching = ref(false);

// 获取所有答题记录
const fetchSubmissions = async () => {
  if (isFetching.value) return; // 防止重复加载
  
  isFetching.value = true;
  loading.value = true;
  error.value = null;
  
  try {
    // 获取个人记录
    const personalData = await getMySubmissions();
    mySubmissions.value = personalData;
    
    // 如果是管理员或教师，获取监控数据
    if (authStore.user.role !== 'student') {
      await fetchMonitoringData();
      // 根据切换状态决定显示什么数据
      submissions.value = showAllSubmissions.value ? allSubmissions.value : personalData;
      
      // 预加载排名信息
      const itemsWithExercise = submissions.value.filter(item => item.exercise_id);
      
      // 分批加载排名信息，避免一次性发起太多请求
      const batchSize = 3;
      for (let i = 0; i < itemsWithExercise.length; i += batchSize) {
        const batch = itemsWithExercise.slice(i, i + batchSize);
        
        // 每批延迟一段时间，避免同时发起太多请求
        setTimeout(() => {
          batch.forEach(item => loadRanking(item));
        }, i * 200); // 每批间隔200ms
      }
    } else {
      submissions.value = personalData;
    }
  } catch (e) {
    error.value = '获取答题记录失败';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
    isFetching.value = false;
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

// 根据分数获取徽章样式
const getScoreBadgeClass = (score) => {
  if (score === null || score === undefined) return 'badge-no-score';
  if (score >= 90) return 'badge-excellent';
  if (score >= 80) return 'badge-good';
  if (score >= 60) return 'badge-pass';
  return 'badge-fail';
};

// 统计数据计算
const averageScore = computed(() => {
  const dataToCalculate = authStore.user.role === 'student' ? submissions.value : mySubmissions.value;
  if (!dataToCalculate.length) return 0;
  const total = dataToCalculate.reduce((sum, item) => sum + (item.total_score || 0), 0);
  return Math.round(total / dataToCalculate.length);
});

const highestScore = computed(() => {
  const dataToCalculate = authStore.user.role === 'student' ? submissions.value : mySubmissions.value;
  if (!dataToCalculate.length) return 0;
  return Math.max(...dataToCalculate.map(item => item.total_score || 0));
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
const completedExercises = computed(() => {
  const dataToCalculate = authStore.user.role === 'student' ? submissions.value : mySubmissions.value;
  const exercises = new Set();
  dataToCalculate.forEach(item => {
    if (item.exercise_id) exercises.add(item.exercise_id);
  });
  return exercises.size;
});

// 根据练习筛选提交记录
const filteredSubmissions = computed(() => {
  if (!filterExercise.value) return submissions.value;
  return submissions.value.filter(item => item.exercise_id === filterExercise.value);
});

// 监听视图切换
watch(showAllSubmissions, (newValue) => {
  
  if (authStore.user.role !== 'student') {
    // 确保数据已经加载完成再切换
    if (allSubmissions.value.length > 0 || mySubmissions.value.length > 0) {
      
      submissions.value = newValue ? allSubmissions.value : mySubmissions.value;
      
    }
  }
});

onMounted(() => {
  fetchSubmissions();
});
</script>

<style scoped>
.dashboard-container {
  padding: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  position: relative;
}

.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 30px;
  position: relative;
  overflow: hidden;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 2;
}

.title-section {
  flex: 1;
}

.dashboard-title {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
}

.dashboard-subtitle {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
  font-weight: 300;
}

.header-decoration {
  position: relative;
}

.decoration-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  position: absolute;
  top: -60px;
  right: 0;
}

.decoration-circle.small {
  width: 60px;
  height: 60px;
  top: -30px;
  right: 80px;
  background: rgba(255, 255, 255, 0.05);
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: white;
  background: rgba(255, 255, 255, 0.1);
  margin: 20px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  margin-bottom: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态 */
.error-container {
  text-align: center;
  padding: 60px 20px;
  color: white;
  background: rgba(255, 255, 255, 0.1);
  margin: 20px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-container h3 {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
}

.retry-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 20px;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* 空状态 */
.empty-container {
  text-align: center;
  padding: 80px 20px;
  color: white;
  background: rgba(255, 255, 255, 0.1);
  margin: 20px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  position: relative;
}

.empty-illustration {
  position: relative;
  display: inline-block;
  margin-bottom: 24px;
}

.empty-icon {
  font-size: 64px;
  position: relative;
  z-index: 2;
}

.empty-bg-circles {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}

.bg-circle:first-child {
  width: 100px;
  height: 100px;
  top: -50px;
  left: -50px;
}

.bg-circle:last-child {
  width: 140px;
  height: 140px;
  top: -70px;
  left: -70px;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.05; }
  50% { transform: scale(1.1); opacity: 0.1; }
}

.empty-container h3 {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
}

.empty-hint {
  opacity: 0.8;
  font-size: 14px;
}

/* 仪表盘内容 */
.dashboard-content {
  background: #f8fafc;
  min-height: 100vh;
  padding: 30px;
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.stats-section,
.records-section {
  margin-bottom: 32px;
}

.section-title {
  margin: 0 0 20px 0;
  color: #1a202c;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.section-title::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 2px;
  margin-right: 12px;
}

.section-header-with-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.view-toggle {
  display: flex;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 4px;
  gap: 2px;
}

.toggle-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #718096;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toggle-btn:hover:not(.active) {
  color: #4a5568;
  background: rgba(255, 255, 255, 0.7);
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--card-color);
}

.stat-card.primary {
  --card-color: #667eea;
}

.stat-card.success {
  --card-color: #48bb78;
}

.stat-card.warning {
  --card-color: #ed8936;
}

.stat-card.info {
  --card-color: #4299e1;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--card-color);
  border-radius: 12px;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 4px;
}

.stat-label {
  color: #718096;
  font-size: 14px;
  font-weight: 500;
}

.stat-trend {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
  background: #f7fafc;
  color: #718096;
}

.stat-trend.positive {
  background: #f0fff4;
  color: #38a169;
}

.stat-trend.neutral {
  background: #fef5e7;
  color: #d69e2e;
}

/* 记录部分 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.record-count {
  background: #e2e8f0;
  color: #4a5568;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 16px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #4a5568;
  font-size: 14px;
  min-width: 160px;
  transition: all 0.2s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 表格样式 */
.table-container {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.table-wrapper {
  overflow-x: auto;
}

.submissions-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.submissions-table th {
  background: #f8fafc;
  color: #4a5568;
  font-weight: 600;
  font-size: 14px;
  padding: 16px 20px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.submissions-table td {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.table-row {
  transition: all 0.2s ease;
}

.table-row:hover {
  background: #f8fafc;
}

.table-row:last-child td {
  border-bottom: none;
}

/* 表格列 */
.col-student {
  min-width: 120px;
}

.student-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.student-username {
  font-weight: 600;
  color: #1a202c;
  font-size: 14px;
}

.student-realname {
  font-size: 12px;
  color: #718096;
}

.col-problem {
  min-width: 200px;
}

.problem-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.problem-name {
  font-weight: 600;
  color: #1a202c;
  font-size: 14px;
}

.problem-chinese {
  font-size: 12px;
  color: #718096;
}

.col-score {
  width: 80px;
  text-align: center;
}

.score-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 28px;
  border-radius: 14px;
  font-weight: 600;
  font-size: 13px;
  color: white;
}

.badge-excellent {
  background: linear-gradient(135deg, #48bb78, #38a169);
}

.badge-good {
  background: linear-gradient(135deg, #4299e1, #3182ce);
}

.badge-pass {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
}

.badge-fail {
  background: linear-gradient(135deg, #f56565, #e53e3e);
}

.badge-no-score {
  background: #a0aec0;
}

.col-exercise,
.col-course,
.col-class {
  min-width: 120px;
}

.exercise-name,
.course-name,
.class-name {
  font-size: 14px;
  color: #4a5568;
}

.col-time {
  min-width: 140px;
}

.time-text {
  font-size: 13px;
  color: #718096;
}

.col-ranking {
  width: 120px;
  text-align: center;
}

.col-ranking small {
  color: #718096;
  font-weight: 400;
  font-size: 11px;
  line-height: 1.2;
  display: block;
  margin-top: 2px;
}

.ranking-display {
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  font-size: 13px;
  font-weight: 500;
}

.ranking-display:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
  transform: translateY(-1px);
}

.ranking-text {
  color: #667eea;
  font-weight: 600;
}

.ranking-display:hover .ranking-text {
  color: white;
}

.ranking-loading {
  color: #a0aec0;
}

.loading-dots {
  animation: loadingDots 1.5s infinite;
}

@keyframes loadingDots {
  0%, 20% { opacity: 0; }
  50% { opacity: 1; }
  80%, 100% { opacity: 0; }
}

.ranking-placeholder {
  color: #718096;
  font-size: 12px;
}

.no-ranking {
  color: #a0aec0;
  font-size: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .dashboard-header {
    padding: 24px 20px;
  }
  
  .dashboard-title {
    font-size: 24px;
  }
  
  .dashboard-content {
    padding: 20px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .submissions-table th,
  .submissions-table td {
    padding: 12px 16px;
  }
  
  .col-student {
    min-width: 100px;
  }
  
  .col-problem {
    min-width: 160px;
  }
  
  .col-exercise,
  .col-course,
  .col-class {
    min-width: 100px;
  }
  
  .col-ranking {
    min-width: 110px;
  }
}
</style> 