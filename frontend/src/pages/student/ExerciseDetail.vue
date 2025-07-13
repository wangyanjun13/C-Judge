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
            （已开始，{{ formatTimeRemaining() }}后截止，截止时间为{{ formatDate(exercise.end_time) }}）
          </span>
          <span class="time-info" v-else-if="!isExerciseStarted">
            （{{ formatTimeRemaining() }}后开始）
          </span>
          <span class="time-info" v-else-if="isExerciseEnded">
            （已截止）
          </span>
        </h2>
        <div class="actions">
          <button @click="goBack" class="btn btn-back">返回</button>
        </div>
      </div>
      
      <div class="problems-section" :class="{'exercise-ended': isExerciseEnded}">
        <div v-if="isExerciseEnded" class="deadline-banner">
          <span>练习已截止，无法提交新代码</span>
        </div>
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
                <th>标签</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(problem, index) in exercise.problems" :key="problem.id">
                <td>{{ index + 1 }}</td>
                <td>{{ problem.name }}</td>
                <td>{{ formatChineseName(problem.chinese_name) }}</td>
                <td>
                  <span class="score-cell">{{ calculateTotalScore(problem) }}</span>
                  <span v-if="isSubmitted(problem)" class="submitted-tag">已提交</span>
                  <span v-else class="not-submitted-tag">未提交</span>
                </td>
                <td>{{ problem.time_limit }}ms</td>
                <td>{{ problem.memory_limit }}MB</td>
                <td class="tags-cell">
                  <div v-if="problem.tags && problem.tags.length > 0" class="problem-tags">
                    <template v-for="(tags, tagType) in groupTagsByType(problem.tags)" :key="tagType">
                      <div class="tag-group">
                        <span class="tag-type">{{ tagType }}:</span>
                        <span 
                          v-for="tag in tags" 
                          :key="tag.id" 
                          class="tag-badge"
                          :style="{ backgroundColor: getTagColor(tag.tag_type_id) }"
                        >
                          {{ tag.name }}
                        </span>
                      </div>
                    </template>
                  </div>
                  <span v-else class="no-tags">暂无标签</span>
                </td>
                <td>
                  <button @click="viewProblem(problem.id)" class="btn btn-primary" 
                    :disabled="!isExerciseStarted" 
                    :title="!isExerciseStarted ? '练习尚未开始，无法查看题目' : ''">
                    查看
                    <span v-if="isExerciseEnded" class="deadline-badge">已截止</span>
                    <span v-else-if="!isExerciseStarted" class="not-started-badge">未开始</span>
                  </button>
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
        <ExerciseStatistics :exerciseId="exerciseId" :includeSpecialUsers="false" />
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
import { getSubmissions } from '../../api/submissions';
import { useAuthStore } from '../../store/auth';
import { logUserOperation, OperationType } from '../../utils/logger';
import { getProblemTags, getTagTypes } from '../../api/tags';
import ExerciseStatistics from '../../components/ExerciseStatistics.vue';

const route = useRoute();
const router = useRouter();
const exerciseId = route.params.id;
const authStore = useAuthStore();

const exercise = ref({});
const loading = ref(true);
const error = ref(null);
const statisticsModalVisible = ref(false);
const submissionMap = ref({}); // 保存题目ID到提交记录的映射
const tagTypeMap = ref({}); // 存储标签类型ID到名称的映射

// 在script setup部分添加计算练习时间的函数
const isExerciseStarted = computed(() => {
  if (!exercise.value || !exercise.value.start_time) return false;
  return new Date(exercise.value.start_time) <= new Date();
});

const isExerciseEnded = computed(() => {
  if (!exercise.value || !exercise.value.end_time) return false;
  return new Date(exercise.value.end_time) <= new Date();
});

const formatTimeRemaining = () => {
  if (!exercise.value) return '0小时';
  
  const now = new Date();
  let targetDate;
  
  if (!isExerciseStarted.value) {
    // 未开始，计算距离开始的时间
    if (!exercise.value.start_time) return '0小时';
    targetDate = new Date(exercise.value.start_time);
    if (isNaN(targetDate.getTime())) return '0小时';
  } else if (!isExerciseEnded.value) {
    // 已开始但未结束，计算距离结束的时间
    if (!exercise.value.end_time) return '0小时';
    targetDate = new Date(exercise.value.end_time);
    if (isNaN(targetDate.getTime())) return '0小时';
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
  return '取总和';
};

// 根据标签类型生成颜色
const getTagColor = (tagTypeId) => {
  // 预定义一组好看的颜色
  const colors = [
    '#409eff', // 蓝色
    '#67c23a', // 绿色
    '#e6a23c', // 橙色
    '#f56c6c', // 红色
    '#909399', // 灰色
    '#9c27b0', // 紫色
    '#2196f3', // 浅蓝
    '#ff9800', // 橙黄
    '#795548', // 棕色
    '#607d8b'  // 蓝灰
  ];
  
  // 使用标签类型ID作为索引来选择颜色
  const index = ((tagTypeId || 0) % colors.length);
  return colors[index];
};

// 计算题目总分
const calculateTotalScore = (problem) => {
  // 检查这个题目是否有提交记录
  const submission = submissionMap.value[problem.id];
  if (submission) {
    // 即使是0分也显示出来
    return `${submission.total_score ?? 0}`;
  }
  return '0';  // 没有提交记录显示0分
};

// 检查题目是否已提交
const isSubmitted = (problem) => {
  return !!submissionMap.value[problem.id];
};

// 获取练习详情
const fetchExerciseDetail = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await getExerciseDetail(exerciseId);
    exercise.value = result;
    
    // 记录查看练习操作
    await logUserOperation(OperationType.VIEW_EXERCISE, `练习: ${result.name}`);
    
    // 获取所有题目的提交记录
    if (authStore.user && authStore.user.id) {
      await fetchSubmissions();
    }
    
    // 加载每个题目的标签
    if (result.problems && result.problems.length > 0) {
      await loadProblemTags();
    }
  } catch (err) {
    console.error('获取练习详情失败', err);
    error.value = '获取练习详情失败，请稍后重试';
    ElMessage.error('获取练习详情失败');
  } finally {
    loading.value = false;
  }
};

// 加载所有问题的标签
const loadProblemTags = async () => {
  // 加载标签类型
  try {
    const tagTypes = await getTagTypes();
    // 初始化tagTypeMap
    tagTypes.forEach(tagType => {
      tagTypeMap.value[tagType.id] = tagType.name;
    });
  } catch (err) {
    console.error('加载标签类型失败:', err);
  }
  
  for (const problem of exercise.value.problems) {
    if (problem.data_path) {
      try {
        const tags = await getProblemTags(problem.data_path);
        if (tags.length > 0) {
          // 直接将标签添加到问题对象上
          problem.tags = tags;
        }
      } catch (err) {
        console.error(`获取问题 ${problem.data_path} 的标签失败:`, err);
      }
    }
  }
};

// 根据标签类型分组标签
const groupTagsByType = (tags) => {
  const grouped = {};
  
  if (!tags) return grouped;
  
  tags.forEach(tag => {
    const typeName = tagTypeMap.value[tag.tag_type_id] || '未分类';
    if (!grouped[typeName]) {
      grouped[typeName] = [];
    }
    grouped[typeName].push(tag);
  });
  
  return grouped;
};

// 获取提交记录
const fetchSubmissions = async () => {
  try {
    // 获取该用户在这个练习中的所有提交记录
    const submissions = await getSubmissions({
      userId: authStore.user.id,
      exerciseId: exerciseId
    });
    
    // 为每道题找到最新的提交记录
    const tempMap = {};
    submissions.forEach(submission => {
      // 如果这道题还没有提交记录，或者这条记录比之前的更新
      if (!tempMap[submission.problem_id] || 
          new Date(submission.submitted_at) > new Date(tempMap[submission.problem_id].submitted_at)) {
        tempMap[submission.problem_id] = submission;
      }
    });
    
    submissionMap.value = tempMap;
  } catch (error) {
    console.error('获取提交记录失败:', error);
  }
};

// 查看题目
const viewProblem = (problemId) => {
  // 记录查看题目操作
  logUserOperation(OperationType.VIEW_PROBLEM, `题目ID: ${problemId}`);
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
  margin-bottom: 60px; /* 增加底部边距，防止与页脚重叠 */
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
  font-size: 15px;
  color: #606266;
  margin-left: 10px;
  font-weight: bold;
  background-color: #f0f9eb;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e1f3d8;
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

.score-cell {
  font-weight: bold;
  color: #303133;
}

.submitted-tag {
  display: inline-block;
  margin-left: 5px;
  padding: 2px 5px;
  background-color: #67c23a;
  color: white;
  font-size: 12px;
  border-radius: 4px;
}

.not-submitted-tag {
  display: inline-block;
  margin-left: 5px;
  padding: 2px 5px;
  background-color: #909399;
  color: white;
  font-size: 12px;
  border-radius: 4px;
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

.deadline-badge {
  display: inline-block;
  margin-left: 5px;
  padding: 2px 5px;
  background-color: #909399;
  color: white;
  font-size: 12px;
  border-radius: 4px;
}

.not-started-badge {
  display: inline-block;
  margin-left: 5px;
  padding: 2px 5px;
  background-color: #e6a23c;
  color: white;
  font-size: 12px;
  border-radius: 4px;
}

.tags-cell {
  max-width: 300px;
}

.problem-tags {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
}

.tag-type {
  font-weight: 500;
  font-size: 0.9em;
  color: #606266;
}

.tag-badge {
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-size: 0.85em;
  white-space: nowrap;
}

.no-tags {
  color: #909399;
  font-size: 0.9em;
  font-style: italic;
}

/* 如果练习已截止，使表格显示灰色 */
.exercise-ended .problems-table {
  opacity: 0.8;
}

.deadline-banner {
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
  color: #f56c6c;
  padding: 10px;
  margin-bottom: 20px;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
}
</style> 