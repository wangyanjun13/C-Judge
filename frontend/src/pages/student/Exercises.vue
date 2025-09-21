<template>
  <div class="exercises-container">
    <div class="header">
      <div class="course-selector">
        <label for="course-select">课程：</label>
        <select id="course-select" v-model="selectedCourse">
          <option value="">全部课程</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </div>
    </div>
    
    <div class="exercises-list">
      <table>
        <thead>
          <tr>
            <th>练习名称</th>
            <th>所属课程</th>
            <th>发布时间</th>
            <th>截止时间</th>
            <th>是否在线测评</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="loading-message">加载中...</td>
          </tr>
          <tr v-else-if="exercises.length === 0">
            <td colspan="7" class="empty-message">暂无练习</td>
          </tr>
          <template v-else>
            <tr v-for="exercise in filteredExercises" :key="exercise.id">
              <td>
                <a class="exercise-link" @click="viewExercise(exercise.id)">{{ exercise.name }}</a>
              </td>
              <td>{{ formatCourseName(exercise) }}</td>
              <td>{{ formatDate(exercise.start_time) }}</td>
              <td>{{ formatDate(exercise.end_time) }}</td>
              <td>{{ exercise.is_online_judge ? '是' : '否' }}</td>
              <td>
                <button class="btn btn-primary" @click="viewExercise(exercise.id)">查看</button>
              </td>
              <td>
                <button class="btn btn-text" @click="showNoteModal(exercise)">备注</button>
                <span v-if="exerciseNotes[exercise.id]" class="note-text">{{ exerciseNotes[exercise.id] }}</span>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    
    <!-- 练习备注弹窗 -->
    <div v-if="noteModalVisible" class="modal-overlay" @click="noteModalVisible = false">
      <div class="modal" @click.stop>
        <h3>练习备注</h3>
        <div class="form-group">
          <label for="exercise-note">备注内容</label>
          <textarea 
            id="exercise-note" 
            v-model="exerciseNotes[selectedExercise?.id]" 
            rows="4"
            placeholder="请输入备注内容..."
          ></textarea>
        </div>
        <div class="form-actions">
          <button @click="noteModalVisible = false">关闭</button>
          <button @click="saveNote" class="btn-primary">保存</button>
        </div>
      </div>
    </div>

    <!-- 悬浮下载按钮 -->
    <FloatingDownload />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getStudentExercises } from '../../api/exercises';
import { logUserOperation, OperationType } from '../../utils/logger';
import FloatingDownload from '../../components/FloatingDownload.vue';

const router = useRouter();
const exercises = ref([]);
const courses = ref([]);
const loading = ref(true);
const selectedCourse = ref('');
const noteModalVisible = ref(false);
const selectedExercise = ref(null);
const exerciseNotes = ref({});  // 存储练习的备注，格式为 {exerciseId: noteText}

// 过滤练习
const filteredExercises = computed(() => {
  if (!selectedCourse.value) {
    return exercises.value;
  }
  return exercises.value.filter(exercise => exercise.course_id === selectedCourse.value);
});

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 查看练习
const viewExercise = (id) => {
  // 记录查看练习的操作
  const exercise = exercises.value.find(e => e.id === id);
  if (exercise) {
    logUserOperation(OperationType.VIEW_EXERCISE, `练习: ${exercise.name}`);
  }
  router.push(`/student/exercise/${id}`);
};

// 显示备注对话框
const showNoteModal = (exercise) => {
  selectedExercise.value = exercise;
  // 如果本地存储中有该练习的备注，则加载
  const savedNotes = localStorage.getItem('studentExerciseNotes');
  if (savedNotes) {
    exerciseNotes.value = JSON.parse(savedNotes);
  }
  noteModalVisible.value = true;
};

// 保存备注
const saveNote = () => {
  if (selectedExercise.value) {
    // 保存到本地存储
    localStorage.setItem('studentExerciseNotes', JSON.stringify(exerciseNotes.value));
    // 记录添加备注的操作
    logUserOperation(OperationType.UPDATE_NOTE, `练习备注: ${selectedExercise.value.name}`);
    ElMessage.success('备注保存成功');
    noteModalVisible.value = false;
  }
};

// 获取练习列表
const fetchExercises = async () => {
  loading.value = true;
  try {
    const result = await getStudentExercises();
    
    // 确保返回结果是数组
    exercises.value = Array.isArray(result) ? result : [];
    
    // 提取不重复的课程列表
    const courseMap = new Map();
    
    if (exercises.value.length > 0) {
      exercises.value.forEach(exercise => {
        if (!courseMap.has(exercise.course_id)) {
          courseMap.set(exercise.course_id, {
            id: exercise.course_id,
            name: exercise.course_name
          });
        }
      });
    }
    
    courses.value = Array.from(courseMap.values());
  } catch (error) {
    console.error('获取练习列表失败', error);
    ElMessage.error('获取练习列表失败');
    // 确保在出错时初始化为空数组
    exercises.value = [];
    courses.value = [];
  } finally {
    loading.value = false;
  }
};

// 格式化课程名称
const formatCourseName = (exercise) => {
  if (exercise.course_name && exercise.teacher_name) {
    return `${exercise.course_name}（${exercise.teacher_name}）`;
  } else if (exercise.course_name) {
    return exercise.course_name;
  }
  return '未知课程';
};

onMounted(() => {
  fetchExercises();
  
  // 加载备注数据
  const savedNotes = localStorage.getItem('studentExerciseNotes');
  if (savedNotes) {
    exerciseNotes.value = JSON.parse(savedNotes);
  }
});
</script>

<style scoped>
.exercises-container {
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
}

.course-selector {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.8);
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.course-selector label {
  margin-right: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.course-selector select {
  padding: 8px 16px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: var(--radius-sm);
  min-width: 200px;
  background-color: white;
  color: var(--text-primary);
  font-size: 14px;
  transition: var(--transition-fast);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.course-selector select:hover {
  border-color: var(--primary-color);
}

.course-selector select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  background: white;
}

th, td {
  padding: 14px 18px;
  text-align: left;
}

th {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  color: var(--text-primary);
  font-weight: 600;
  font-size: 14px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

td {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  color: var(--text-primary);
  font-size: 14px;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background-color: rgba(102, 126, 234, 0.05);
}

.loading-message, .empty-message {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  margin-right: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition-fast);
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
  box-shadow: 0 2px 5px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
}

.btn-text {
  background: none;
  color: var(--primary-color);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
}

.btn-text:hover {
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
  text-decoration: none;
}

/* 模态对话框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 0;
  border-radius: var(--radius-lg);
  width: 450px;
  max-width: 90%;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  animation: modal-in 0.3s ease;
}

@keyframes modal-in {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal h3 {
  margin: 0;
  padding: 20px;
  background: var(--primary-gradient);
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.form-group {
  padding: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: var(--radius-sm);
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  font-size: 14px;
}

.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding: 0 20px 20px;
  gap: 12px;
}

.form-actions button {
  padding: 8px 20px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition-fast);
}

.form-actions button:first-child {
  background-color: #f0f2f5;
  color: var(--text-primary);
}

.form-actions button:first-child:hover {
  background-color: #e4e6eb;
}

.form-actions .btn-primary {
  background: var(--primary-gradient);
  color: white;
}

.form-actions .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.exercise-link {
  color: var(--primary-color);
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
  transition: var(--transition-fast);
  padding: 4px 8px;
  margin: -4px -8px;
  border-radius: var(--radius-sm);
  display: inline-block;
}

.exercise-link:hover {
  background-color: rgba(102, 126, 234, 0.1);
  text-decoration: none;
}

.note-text {
  display: inline-block;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-left: 5px;
  color: var(--text-secondary);
  font-size: 12px;
  font-style: italic;
  background-color: rgba(102, 126, 234, 0.05);
  padding: 2px 6px;
  border-radius: 10px;
}
</style> 