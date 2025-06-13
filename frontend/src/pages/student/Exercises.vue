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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getStudentExercises } from '../../api/exercises';

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
}

.course-selector {
  display: flex;
  align-items: center;
}

.course-selector label {
  margin-right: 10px;
  font-weight: 500;
}

.course-selector select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 200px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

th {
  background-color: #fafafa;
  font-weight: 500;
}

.loading-message, .empty-message {
  text-align: center;
  padding: 20px;
  color: #999;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-text {
  background: none;
  color: #1890ff;
  padding: 0;
}

.btn-text:hover {
  color: #40a9ff;
  text-decoration: underline;
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
  width: 400px;
  max-width: 90%;
}

.modal h3 {
  margin-top: 0;
  color: #1890ff;
}

.modal button {
  margin-top: 20px;
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal button:hover {
  background-color: #40a9ff;
}

.exercise-link {
  color: #1890ff;
  cursor: pointer;
  text-decoration: none;
}

.exercise-link:hover {
  text-decoration: underline;
}

.note-text {
  display: inline-block;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-left: 5px;
  color: #999;
  font-size: 12px;
  font-style: italic;
}
</style> 