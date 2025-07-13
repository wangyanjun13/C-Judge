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
            <button @click="showAddProblemModal" class="btn btn-primary">添加题目</button>
            <button @click="showStatisticsModal" class="btn btn-statistics">试题答题统计</button>
            <button @click="showActiveStudentsModal" class="btn btn-success">在线答题用户</button>
            <button @click="clearExercise" class="btn btn-danger">清空</button>
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
                  <button @click="viewProblem(problem.id)" class="btn btn-primary">
                    查看
                    <span v-if="isExerciseEnded" class="deadline-badge">已截止</span>
                  </button>
                  <button @click="showEditProblemModal(problem)" class="btn btn-edit">修改</button>
                  <button @click="removeProblem(problem.id)" class="btn btn-danger">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-problems">
          <p>该练习暂无题目，请添加题目</p>
        </div>
      </div>
    </template>
    
    <!-- 添加题目对话框 -->
    <div v-if="addProblemModalVisible" class="modal-overlay" @click="addProblemModalVisible = false">
      <div class="modal" @click.stop>
        <h3>添加题目</h3>
        <ProblemSelector 
          :exerciseId="exerciseId" 
          @confirm="handleAddProblems" 
          @cancel="addProblemModalVisible = false"
        />
      </div>
    </div>

    <!-- 编辑题目对话框 -->
    <div v-if="editProblemModalVisible" class="modal-overlay" @click="editProblemModalVisible = false">
      <div class="modal" @click.stop>
        <h3>修改题目</h3>
        <form @submit.prevent="submitEditProblemForm">
          <div class="form-section">
            <h4>基本内容</h4>
            <div class="form-group">
              <label for="problem-name">试题名称</label>
              <input id="problem-name" v-model="editProblemForm.name" required />
            </div>
            <div class="form-row">
              <div class="form-group half">
                <label for="problem-time-limit">时间限制 (ms)</label>
                <input id="problem-time-limit" type="number" v-model="editProblemForm.time_limit" required />
              </div>
              <div class="form-group half">
                <label for="problem-memory-limit">空间限制 (MB)</label>
                <input id="problem-memory-limit" type="number" v-model="editProblemForm.memory_limit" required />
              </div>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="editProblemForm.apply_limits_to_all" />
                应用时限和空限到所有试题
              </label>
            </div>
          </div>

          <div class="form-section">
            <h4>得分计算方法</h4>
            <div class="form-group">
              <label for="score-calculation-method">计算方法</label>
              <select id="score-calculation-method" v-model="editProblemForm.score_calculation_method" disabled>
                <option value="综合">取总和</option>
              </select>
            </div>
            <div class="form-row">
              <div class="form-group half">
                <label for="code-review-score">代码检查总分</label>
                <input id="code-review-score" type="number" v-model="editProblemForm.code_check_score" required />
              </div>
              <div class="form-group half">
                <label for="runtime-score">运行总分</label>
                <input id="runtime-score" type="number" v-model="editProblemForm.runtime_score" required />
              </div>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="editProblemForm.apply_score_method_to_all" />
                应用得分计算方法到所有试题
              </label>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="editProblemModalVisible = false" class="btn btn-cancel">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 试题答题统计对话框 -->
    <div v-if="statisticsModalVisible" class="modal-overlay" @click="statisticsModalVisible = false">
      <div class="modal large-modal" @click.stop>
        <h3>试题答题统计</h3>
        <ExerciseStatistics :exerciseId="exerciseId" :includeSpecialUsers="true" />
        <div class="form-actions">
          <button @click="statisticsModalVisible = false" class="btn btn-primary">关闭</button>
        </div>
      </div>
    </div>

    <!-- 在线答题用户对话框 -->
    <div v-if="activeStudentsModalVisible" class="modal-overlay" @click="activeStudentsModalVisible = false">
      <div class="modal large-modal" @click.stop>
        <h3>在线答题用户</h3>
        <ActiveStudentsMonitor :exerciseId="exerciseId" :exerciseName="exercise.name" />
        <div class="form-actions">
          <button @click="activeStudentsModalVisible = false" class="btn btn-primary">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getExerciseDetail, updateExercise, removeProblemFromExercise, updateProblem, addProblemsToExercise, clearExerciseProblems } from '../../api/exercises';
import { getSubmissions } from '../../api/submissions';
import ProblemSelector from '../../components/ProblemSelector.vue';
import ExerciseStatistics from '../../components/ExerciseStatistics.vue';
import ActiveStudentsMonitor from '../../components/ActiveStudentsMonitor.vue';
import { useAuthStore } from '../../store/auth';
import { logUserOperation, OperationType } from '../../utils/logger';
import { getProblemTags, getTagTypes } from '../../api/tags';

const route = useRoute();
const router = useRouter();
const exerciseId = route.params.id;
const authStore = useAuthStore();

const exercise = ref({});
const loading = ref(true);
const error = ref(null);
const addProblemModalVisible = ref(false);
const editProblemModalVisible = ref(false);
const statisticsModalVisible = ref(false);
const activeStudentsModalVisible = ref(false);
const submissionMap = ref({}); // 保存题目ID到提交记录的映射
const tagTypeMap = ref({}); // 存储标签类型ID到名称的映射

// 编辑题目表单
const editProblemForm = ref({
  id: '',
  name: '',
  chinese_name: '',
  time_limit: '',
  memory_limit: '',
  apply_limits_to_all: false,
  score_calculation_method: '综合',
  code_check_score: 20,
  runtime_score: 80,
  apply_score_method_to_all: false
});

// 添加题目表单
const addProblemForm = ref({
  name: '',
  chinese_name: '',
  time_limit: '',
  memory_limit: '',
  apply_limits_to_all: false,
  score_calculation_method: '综合',
  code_check_score: 20,
  runtime_score: 80,
  apply_score_method_to_all: false
});

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 获取练习详情
const fetchExerciseDetail = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await getExerciseDetail(exerciseId);
    exercise.value = result;
    
    // 记录查看练习详情操作
    logUserOperation(OperationType.VIEW_EXERCISE, `练习: ${result.name}`);
    
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
  logUserOperation(OperationType.VIEW_PROBLEM, `题目ID: ${problemId}`);
  router.push(`/admin/problem/${problemId}?exercise_id=${exerciseId}`);
};

// 返回练习列表
const goBack = () => {
  router.push('/admin/exercises');
};

// 显示添加题目对话框
const showAddProblemModal = () => {
  addProblemModalVisible.value = true;
};

// 移除题目
const removeProblem = async (problemId) => {
  try {
    await ElMessageBox.confirm('确定要从练习中移除该题目吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    await removeProblemFromExercise(exerciseId, problemId);
    
    // 记录移除题目操作
    const problemName = exercise.value.problems.find(p => p.id === problemId)?.name || problemId;
    logUserOperation(OperationType.REMOVE_PROBLEM, `从练习 ${exercise.value.name} 中移除题目: ${problemName}`);
    
    ElMessage.success('题目已成功移除');
    fetchExerciseDetail(); // 重新获取练习详情
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除题目失败', error);
      ElMessage.error('移除题目失败');
    }
  }
};

// 显示编辑题目对话框
const showEditProblemModal = (problem) => {
  editProblemForm.value = {
    id: problem.id,
    name: problem.name,
    chinese_name: problem.chinese_name,
    time_limit: problem.time_limit,
    memory_limit: problem.memory_limit,
    apply_limits_to_all: false,
    score_calculation_method: '综合',
    code_check_score: problem.code_check_score || 20,
    runtime_score: problem.runtime_score || 80,
    apply_score_method_to_all: false
  };
  editProblemModalVisible.value = true;
};

// 提交编辑题目表单
const submitEditProblemForm = async () => {
  try {
    console.log('提交编辑题目表单:', editProblemForm.value);
    
    // 如果应用到所有题目
    if (editProblemForm.value.apply_limits_to_all || editProblemForm.value.apply_score_method_to_all) {
      const updatedProblems = exercise.value.problems.map(problem => {
        const updatedProblem = { ...problem };
        
        if (editProblemForm.value.apply_limits_to_all) {
          updatedProblem.time_limit = editProblemForm.value.time_limit;
          updatedProblem.memory_limit = editProblemForm.value.memory_limit;
        }
        
        if (editProblemForm.value.apply_score_method_to_all) {
          updatedProblem.score_calculation_method = editProblemForm.value.score_calculation_method;
          updatedProblem.code_check_score = editProblemForm.value.code_check_score;
          updatedProblem.runtime_score = editProblemForm.value.runtime_score;
        }
        
        return updatedProblem;
      });
      
      // 批量更新所有题目
      await updateExercise(exerciseId, { problems: updatedProblems });
      logUserOperation(OperationType.UPDATE_PROBLEMS, `批量更新练习 ${exercise.value.name} 中的所有题目`);
    } else {
      // 只更新单个题目
      const updateData = {
        id: editProblemForm.value.id,
        time_limit: editProblemForm.value.time_limit,
        memory_limit: editProblemForm.value.memory_limit,
        code_check_score: editProblemForm.value.code_check_score,
        runtime_score: editProblemForm.value.runtime_score,
        score_method: 'sum'
      };
      await updateProblem(exerciseId, editProblemForm.value.id, updateData);
      logUserOperation(OperationType.UPDATE_PROBLEM, `更新练习 ${exercise.value.name} 中的题目: ${editProblemForm.value.name}`);
    }
    
    ElMessage.success('题目更新成功');
    editProblemModalVisible.value = false;
    fetchExerciseDetail(); // 重新获取练习详情
  } catch (error) {
    console.error('更新失败', error);
    ElMessage.error('更新题目失败');
  }
};

// 提交添加题目表单
const submitAddProblemForm = async () => {
  try {
    console.log('提交添加题目表单:', addProblemForm.value);
    
    // 实现添加题目的逻辑
    ElMessage.success('添加题目成功');
    addProblemModalVisible.value = false;
    fetchExerciseDetail(); // 重新获取练习详情
  } catch (error) {
    console.error('添加题目失败', error);
    ElMessage.error('添加题目失败');
  }
};

// 处理添加题目
const handleAddProblems = async (data) => {
  try {
    // 添加题目到练习
    const result = await addProblemsToExercise(data.exerciseId, data.problems);
    
    // 记录添加题目操作
    logUserOperation(OperationType.ADD_PROBLEMS, `向练习 ${exercise.value.name} 添加题目: ${data.problems.length}道`);
    
    // 根据返回结果显示不同的消息
    if (result.added_count > 0 && result.existing_count > 0) {
      ElMessage.success(`成功添加 ${result.added_count} 道题目，${result.existing_count} 道题目已存在`);
    } else if (result.added_count > 0) {
      ElMessage.success(`成功添加 ${result.added_count} 道题目`);
    } else if (result.existing_count > 0) {
      ElMessage.info(`${result.existing_count} 道题目已在练习中`);
    } else {
      ElMessage.warning('未添加任何题目');
    }
    
    addProblemModalVisible.value = false;
    fetchExerciseDetail(); // 重新获取练习详情
  } catch (error) {
    console.error('添加题目失败', error);
    ElMessage.error('添加题目失败');
  }
};

// 显示试题答题统计对话框
const showStatisticsModal = () => {
  statisticsModalVisible.value = true;
  // 记录查看统计的操作
  logUserOperation(OperationType.VIEW_STATISTICS, `查看练习 ${exercise.value.name} 的答题统计`);
};

// 显示在线答题用户对话框
const showActiveStudentsModal = () => {
  activeStudentsModalVisible.value = true;
  // 记录查看在线用户的操作
  logUserOperation(OperationType.VIEW_ACTIVE_STUDENTS, `查看练习 ${exercise.value.name} 的在线答题用户`);
};

// 清空练习
const clearExercise = async () => {
  try {
    await ElMessageBox.confirm('确定要清空练习中的所有题目吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    await clearExerciseProblems(exerciseId);
    logUserOperation(OperationType.CLEAR_EXERCISE, `清空练习 ${exercise.value.name} 中的所有题目`);
    ElMessage.success('已清空练习中的所有题目');
    fetchExerciseDetail(); // 重新获取练习详情
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空题目失败', error);
      ElMessage.error('清空题目失败');
    }
  }
};

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

.actions {
  display: flex;
  gap: 10px;
}

.problems-section {
  margin-top: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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
  white-space: nowrap;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-primary:hover {
  background-color: #66b1ff;
}

.btn-secondary {
  background-color: #909399;
  color: white;
}

.btn-secondary:hover {
  background-color: #a6a9ad;
}

.btn-edit {
  background-color: #67c23a;
  color: white;
}

.btn-edit:hover {
  background-color: #85ce61;
}

.btn-danger {
  background-color: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background-color: #f78989;
}

.btn-back {
  background-color: #f4f4f5;
  color: #606266;
}

.btn-back:hover {
  background-color: #e9e9eb;
}

.btn-cancel {
  background-color: #909399;
  color: white;
}

.btn-cancel:hover {
  background-color: #a6a9ad;
}

.btn-info {
  background-color: #909399;
  color: white;
}

.btn-info:hover {
  background-color: #a6a9ad;
}

.btn-statistics {
  background-color: #409eff;
  color: white;
  font-weight: bold;
  padding: 8px 16px;
  border: 2px solid #3a8ee6;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-statistics:hover {
  background-color: #66b1ff;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-success {
  background-color: #67c23a;
  color: white;
}

.btn-success:hover {
  background-color: #85ce61;
}

.btn-warning {
  background-color: #e6a23c;
  color: white;
}

.btn-warning:hover {
  background-color: #ebb563;
}

/* 模态对话框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 1200px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #606266;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.form-section {
  margin-bottom: 20px;
}

.form-section h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #606266;
  font-size: 16px;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-group.half {
  width: calc(50% - 5px);
}

.checkbox-label {
  display: flex;
  align-items: center;
}

.checkbox-label input {
  margin-right: 5px;
  width: auto;
}

.large-modal {
  width: 90%;
  max-width: 1400px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.large-modal h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #303133;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

/* 如果练习已截止，使表格显示半透明 */
.exercise-ended .problems-table {
  opacity: 0.9;
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

.deadline-badge {
  display: inline-block;
  margin-left: 5px;
  padding: 2px 5px;
  background-color: #909399;
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
</style> 