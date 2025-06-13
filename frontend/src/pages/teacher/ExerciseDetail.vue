<template>
  <div class="exercise-detail-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack" class="btn btn-primary">返回练习列表</button>
    </div>
    <template v-else>
      <div class="header">
        <h2>{{ exercise.name }}</h2>
        <div class="actions">
          <button @click="showEditModal" class="btn btn-edit">编辑练习</button>
          <button @click="goBack" class="btn btn-back">返回</button>
        </div>
      </div>
      
      <div class="exercise-info">
        <div class="info-item">
          <span class="label">所属课程:</span>
          <span class="value">{{ exercise.course_name }}</span>
        </div>
        <div class="info-item">
          <span class="label">发布时间:</span>
          <span class="value">{{ formatDate(exercise.publish_time) }}</span>
        </div>
        <div class="info-item">
          <span class="label">截止时间:</span>
          <span class="value">{{ formatDate(exercise.end_time) }}</span>
        </div>
        <div class="info-item">
          <span class="label">在线评测:</span>
          <span class="value">{{ exercise.is_online_judge ? '是' : '否' }}</span>
        </div>
        <div class="info-item">
          <span class="label">允许语言:</span>
          <span class="value">{{ formatLanguages(exercise.allowed_languages) }}</span>
        </div>
        <div class="info-item" v-if="exercise.note">
          <span class="label">练习备注:</span>
          <span class="value note">{{ exercise.note }}</span>
        </div>
      </div>
      
      <div class="problems-section">
        <div class="section-header">
          <h3>题目列表</h3>
          <button @click="showAddProblemModal" class="btn btn-primary">添加题目</button>
        </div>
        
        <div v-if="exercise.problems && exercise.problems.length > 0">
          <table class="problems-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>题目名称</th>
                <th>题目标题</th>
                <th>时间限制</th>
                <th>内存限制</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="problem in exercise.problems" :key="problem.id">
                <td>{{ problem.id }}</td>
                <td>{{ problem.name }}</td>
                <td>{{ problem.chinese_name }}</td>
                <td>{{ problem.time_limit }}ms</td>
                <td>{{ problem.memory_limit }}MB</td>
                <td>
                  <button @click="viewProblem(problem.id)" class="btn btn-primary">查看</button>
                  <button @click="removeProblem(problem.id)" class="btn btn-danger">移除</button>
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
    
    <!-- 编辑练习对话框 -->
    <div v-if="editModalVisible" class="modal-overlay" @click="editModalVisible = false">
      <div class="modal" @click.stop>
        <h3>编辑练习</h3>
        <form @submit.prevent="submitEditForm">
          <div class="form-group">
            <label for="exercise-name">练习名称</label>
            <input id="exercise-name" v-model="editForm.name" required />
          </div>
          <div class="form-group">
            <label for="exercise-deadline">截止时间</label>
            <div class="datetime-input-wrapper">
              <input id="exercise-deadline" type="datetime-local" v-model="editForm.deadline" required @change="validateDeadline" />
              <div class="datetime-helper">
                <small>请选择有效的截止时间</small>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label for="exercise-judge">在线评测</label>
            <select id="exercise-judge" v-model="editForm.is_online_judge">
              <option :value="true">是</option>
              <option :value="false">否</option>
            </select>
          </div>
          <div class="form-group">
            <label for="exercise-languages">允许语言</label>
            <input id="exercise-languages" v-model="editForm.allowed_languages" placeholder="如: c,cpp,java" />
          </div>
          <div class="form-group">
            <label for="exercise-note">练习备注</label>
            <textarea id="exercise-note" v-model="editForm.note" rows="4"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="editModalVisible = false" class="btn btn-cancel">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 添加题目对话框 -->
    <div v-if="addProblemModalVisible" class="modal-overlay" @click="addProblemModalVisible = false">
      <div class="modal" @click.stop>
        <h3>添加题目</h3>
        <p>此功能正在开发中...</p>
        <div class="form-actions">
          <button @click="addProblemModalVisible = false" class="btn btn-primary">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getExerciseDetail, updateExercise } from '../../api/exercises';

const route = useRoute();
const router = useRouter();
const exerciseId = route.params.id;

const exercise = ref({});
const loading = ref(true);
const error = ref(null);
const editModalVisible = ref(false);
const addProblemModalVisible = ref(false);

// 编辑表单
const editForm = ref({
  name: '',
  deadline: '',
  is_online_judge: true,
  allowed_languages: '',
  note: ''
});

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 格式化日期为输入框格式
const formatDateForInput = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}T${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
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

// 获取练习详情
const fetchExerciseDetail = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await getExerciseDetail(exerciseId);
    exercise.value = result;
  } catch (err) {
    console.error('获取练习详情失败', err);
    error.value = '获取练习详情失败，请稍后重试';
    ElMessage.error('获取练习详情失败');
  } finally {
    loading.value = false;
  }
};

// 查看题目
const viewProblem = (problemId) => {
  router.push(`/teacher/problem/${problemId}?exercise_id=${exerciseId}`);
};

// 返回练习列表
const goBack = () => {
  router.push('/teacher/exercises');
};

// 显示编辑对话框
const showEditModal = () => {
  editForm.value = {
    name: exercise.value.name,
    deadline: exercise.value.end_time ? formatDateForInput(exercise.value.end_time) : '',
    is_online_judge: exercise.value.is_online_judge,
    allowed_languages: exercise.value.allowed_languages,
    note: exercise.value.note || ''
  };
  editModalVisible.value = true;
};

// 提交编辑表单
const submitEditForm = async () => {
  try {
    // 确保截止时间有效
    validateDeadline();
    
    console.log('提交编辑表单:', editForm.value);
    await updateExercise(exerciseId, editForm.value);
    ElMessage.success('练习更新成功');
    editModalVisible.value = false;
    fetchExerciseDetail(); // 重新获取练习详情
  } catch (error) {
    console.error('更新失败', error);
    ElMessage.error('更新练习失败');
  }
};

// 显示添加题目对话框
const showAddProblemModal = () => {
  addProblemModalVisible.value = true;
};

// 移除题目
const removeProblem = (problemId) => {
  ElMessage.info('题目移除功能正在开发中...');
};

// 在script setup部分添加validateDeadline函数
const validateDeadline = () => {
  const deadline = new Date(editForm.value.deadline);
  const now = new Date();
  
  if (deadline <= now) {
    ElMessage.warning('截止时间必须晚于当前时间');
    // 设置截止时间为当前时间后7天
    const newDeadline = new Date();
    newDeadline.setDate(newDeadline.getDate() + 7);
    editForm.value.deadline = formatDateForInput(newDeadline);
  }
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
}

.actions {
  display: flex;
  gap: 10px;
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
  width: 500px;
  max-width: 90%;
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

.datetime-input-wrapper {
  position: relative;
}

.datetime-helper {
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
}
</style> 