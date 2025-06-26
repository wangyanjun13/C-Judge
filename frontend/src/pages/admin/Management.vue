<template>
  <div class="management-container">
    <div class="page-header">
      <h2>系统管理</h2>
    </div>

    <div class="tabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.value" 
        :class="['tab-item', { active: activeTab === tab.value }]"
        @click="switchTab(tab.value)"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- 班级管理 -->
    <div v-if="activeTab === 'classes'" class="tab-content">
      <div class="content-header">
        <h3>班级管理</h3>
        <button class="btn btn-primary" @click="showClassModal">添加班级</button>
      </div>

      <div v-if="loading.classes" class="loading">加载中...</div>
      <div v-else-if="!classes || classes.length === 0" class="empty-data">
        暂无班级数据，请添加
      </div>
      <div v-else class="data-table">
        <p>找到 {{ classes.length }} 个班级</p>
        <table>
          <thead>
            <tr>
              <th>班级名称</th>
              <th>授课教师</th>
              <th>学生数量</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="classItem in classes" :key="classItem.id">
              <td>{{ classItem.name }}</td>
              <td>
                <span v-for="(teacher, index) in classItem.teachers" :key="teacher.id">
                  {{ teacher.username }} ({{ teacher.real_name }}){{ index < classItem.teachers.length - 1 ? ', ' : '' }}
                </span>
              </td>
              <td>{{ classItem.student_count || 0 }}</td>
              <td>
                <button class="btn btn-sm btn-edit" @click="editClass(classItem)">修改</button>
                <button class="btn btn-sm btn-danger" @click="confirmDeleteClass(classItem)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 教师管理 -->
    <div v-else-if="activeTab === 'teachers'" class="tab-content">
      <div class="content-header">
        <h3>教师管理</h3>
        <button class="btn btn-primary" @click="showTeacherModal">添加教师</button>
      </div>
      
      <div v-if="loading.teachers" class="loading">加载中...</div>
      <div v-else-if="!teachers || teachers.length === 0" class="empty-data">
        暂无教师数据，请添加
      </div>
      <div v-else class="data-table">
        <p>找到 {{ teachers.length }} 个教师</p>
        <table>
          <thead>
            <tr>
              <th>用户名称</th>
              <th>是否在线</th>
              <th>注册时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="teacher in teachers" :key="teacher.id">
              <td>{{ teacher.username }} ({{ teacher.real_name }})</td>
              <td>
                <span :class="['status-badge', teacher.is_online ? 'online' : 'offline']">
                  {{ teacher.is_online ? '在线' : '离线' }}
                </span>
              </td>
              <td>{{ formatDate(teacher.register_time) }}</td>
              <td>
                <button class="btn btn-sm btn-edit" @click="editTeacher(teacher)">修改</button>
                <button class="btn btn-sm btn-danger" @click="confirmDeleteTeacher(teacher)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 课程管理 -->
    <div v-else-if="activeTab === 'courses'" class="tab-content">
      <div class="content-header">
        <h3>课程竞赛</h3>
        <button class="btn btn-primary" @click="showCourseModal">添加课程</button>
      </div>
      
      <div v-if="loading.courses" class="loading">加载中...</div>
      <div v-else-if="!courses || courses.length === 0" class="empty-data">
        暂无课程数据，请添加
      </div>
      <div v-else class="data-table">
        <p>找到 {{ courses.length }} 个课程</p>
        <table>
          <thead>
            <tr>
              <th>课程名称</th>
              <th>教师</th>
              <th>班级</th>
              <th>课程类别</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id">
              <td>{{ course.name }}</td>
              <td>{{ formatTeacherName(course) }}</td>
              <td>
                <span v-if="course.classes && course.classes.length > 0">
                  <span 
                    v-for="(cls, index) in course.classes" 
                    :key="cls.id" 
                    class="class-link"
                    @click="goToStudentsByClass(cls.id)"
                  >
                    {{ cls.name }}{{ index < course.classes.length - 1 ? ', ' : '' }}
                  </span>
                </span>
                <span v-else>无</span>
              </td>
              <td>{{ course.category || '未分类' }}</td>
              <td>
                <button class="btn btn-sm btn-edit" @click="editCourse(course)">修改</button>
                <button class="btn btn-sm btn-danger" @click="confirmDeleteCourse(course)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 学生管理 -->
    <div v-else-if="activeTab === 'students'" class="tab-content">
      <div class="content-header">
        <h3>学生管理</h3>
        <div class="action-buttons">
          <button class="btn btn-primary" @click="showStudentModal">添加学生</button>
          <button class="btn btn-secondary" @click="showImportModal">批量导入</button>
          <button class="btn btn-secondary" @click="exportStudents">导出</button>
          <button class="btn btn-danger" @click="confirmClearStudents">清空</button>
        </div>
      </div>
      
      <div class="filter-section">
        <div class="filter-item">
          <label for="class-filter">班级：</label>
          <select id="class-filter" v-model="studentFilters.classId" @change="fetchStudents">
            <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
              {{ classItem.name }}
            </option>
          </select>
        </div>
      </div>
      
      <div v-if="loading.students" class="loading">加载中...</div>
      <div v-else-if="!filteredStudents || filteredStudents.length === 0" class="empty-data">
        暂无学生数据，请添加
      </div>
      <div v-else class="data-table">
        <p>找到 {{ filteredStudents.length }} 个学生</p>
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>学生名称</th>
              <th>班级</th>
              <th>是否在线</th>
              <th>注册时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, index) in filteredStudents" :key="student.id">
              <td>{{ index + 1 }}</td>
              <td>{{ student.username }} ({{ student.real_name }})</td>
              <td>{{ formatClassList(student.classes) }}</td>
              <td>
                <span :class="['status-badge', student.is_online ? 'online' : 'offline']">
                  {{ student.is_online ? '在线' : '离线' }}
                </span>
              </td>
              <td>{{ formatDate(student.register_time) }}</td>
              <td>
                <button class="btn btn-sm btn-edit" @click="editStudent(student)">修改</button>
                <button class="btn btn-sm btn-danger" @click="confirmDeleteStudent(student)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 班级添加/编辑对话框 -->
    <div v-if="classModalVisible" class="modal-overlay" @click="classModalVisible = false">
      <div class="modal" @click.stop>
        <h3>{{ isEditing ? '编辑班级' : '添加班级' }}</h3>
        <form @submit.prevent="submitClassForm">
          <div class="form-group">
            <label for="class-name">班级名称</label>
            <input
              type="text"
              id="class-name"
              v-model="classForm.name"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="class-teacher">授课教师</label>
            <div class="checkbox-group">
              <div v-for="teacher in teachers" :key="teacher.id" class="checkbox-item">
                <input
                  type="checkbox"
                  :id="`teacher-${teacher.id}`"
                  :value="teacher.id"
                  v-model="classForm.teacher_ids"
                />
                <label :for="`teacher-${teacher.id}`">{{ teacher.username }} ({{ teacher.real_name }})</label>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="classModalVisible = false">取消</button>
            <button type="submit" class="btn-primary">{{ isEditing ? '保存' : '添加' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 教师添加/编辑对话框 -->
    <div v-if="teacherModalVisible" class="modal-overlay" @click="teacherModalVisible = false">
      <div class="modal" @click.stop>
        <h3>{{ isEditing ? '编辑教师' : '添加教师' }}</h3>
        <form @submit.prevent="submitTeacherForm">
          <div class="form-group">
            <label for="teacher-username">用户名</label>
            <input
              type="text"
              id="teacher-username"
              v-model="teacherForm.username"
              :disabled="isEditing"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="teacher-password">密码</label>
            <input
              type="password"
              id="teacher-password"
              v-model="teacherForm.password"
              :required="!isEditing"
            />
          </div>
          
          <div class="form-group">
            <label for="teacher-confirm-password">确认密码</label>
            <input
              type="password"
              id="teacher-confirm-password"
              v-model="teacherForm.confirmPassword"
              :required="!isEditing"
            />
          </div>
          
          <div class="form-group">
            <label for="teacher-realname">真实姓名</label>
            <input
              type="text"
              id="teacher-realname"
              v-model="teacherForm.real_name"
              required
            />
          </div>
          
          <div class="form-actions">
            <button type="button" @click="teacherModalVisible = false">取消</button>
            <button type="submit" class="btn-primary">{{ isEditing ? '保存' : '添加' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 课程添加/编辑对话框 -->
    <div v-if="courseModalVisible" class="modal-overlay" @click="courseModalVisible = false">
      <div class="modal" @click.stop>
        <h3>{{ isEditing ? '编辑课程' : '添加课程' }}</h3>
        <form @submit.prevent="submitCourseForm">
          <div class="form-group">
            <label for="course-name">课程名称</label>
            <input
              type="text"
              id="course-name"
              v-model="courseForm.name"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="course-teacher">授课教师</label>
            <select
              id="course-teacher"
              v-model="courseForm.teacher_id"
              required
            >
              <option v-if="!isEditing" value="">选择教师</option>
              <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                {{ teacher.username }} ({{ teacher.real_name }})
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>选择班级</label>
            <div class="checkbox-group">
              <div v-for="classItem in classes" :key="classItem.id" class="checkbox-item">
                <input
                  type="checkbox"
                  :id="`class-${classItem.id}`"
                  :value="classItem.id"
                  v-model="courseForm.class_ids"
                />
                <label :for="`class-${classItem.id}`">{{ classItem.name }}</label>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label for="course-category">课程类别</label>
            <select
              id="course-category"
              v-model="courseForm.category"
            >
              <option v-if="!isEditing" value="">选择类别</option>
              <option value="（课程）">（课程）</option>
              <option value="（竞赛）">（竞赛）</option>
              <option value="（在线练习）">（在线练习）</option>
            </select>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="courseModalVisible = false">取消</button>
            <button type="submit" class="btn-primary">{{ isEditing ? '保存' : '添加' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 确认删除对话框 -->
    <div v-if="deleteModalVisible" class="modal-overlay" @click="deleteModalVisible = false">
      <div class="modal" @click.stop>
        <h3>确认删除</h3>
        <p>您确定要删除{{ deleteType === 'class' ? '班级' : deleteType === 'teacher' ? '教师' : deleteType === 'course' ? '课程' : '' }} "{{ deleteItem?.name }}" 吗？此操作不可撤销。</p>
        <div class="form-actions">
          <button @click="deleteModalVisible = false">取消</button>
          <button class="btn-danger" @click="confirmDelete">删除</button>
        </div>
      </div>
    </div>

    <!-- 学生添加/编辑对话框 -->
    <div v-if="studentModalVisible" class="modal-overlay" @click="studentModalVisible = false">
      <div class="modal" @click.stop>
        <h3>{{ isEditing ? '编辑学生' : '添加学生' }}</h3>
        <form @submit.prevent="submitStudentForm">
          <div class="form-group">
            <label for="student-username">用户名（学号）</label>
            <input
              type="text"
              id="student-username"
              v-model="studentForm.username"
              :disabled="isEditing"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="student-password">密码</label>
            <input
              type="password"
              id="student-password"
              v-model="studentForm.password"
              :required="!isEditing"
            />
          </div>
          
          <div class="form-group">
            <label for="student-confirm-password">确认密码</label>
            <input
              type="password"
              id="student-confirm-password"
              v-model="studentForm.confirmPassword"
              :required="!isEditing"
            />
          </div>
          
          <div class="form-group">
            <label for="student-realname">真实姓名</label>
            <input
              type="text"
              id="student-realname"
              v-model="studentForm.real_name"
              required
            />
          </div>
          
          <div class="form-group">
            <label>班级</label>
            <div class="selected-class">
              {{ getClassName(studentForm.class_ids[0]) || '未选择班级' }}
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="studentModalVisible = false">取消</button>
            <button type="submit" class="btn-primary">{{ isEditing ? '保存' : '添加' }}</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 批量导入学生对话框 -->
    <div v-if="importModalVisible" class="modal-overlay" @click="importModalVisible = false">
      <div class="modal" @click.stop>
        <h3>批量导入学生</h3>
        
        <!-- 导入结果显示 -->
        <div v-if="importResult" class="import-result">
          <h4>导入结果</h4>
          <p class="success-count">成功导入: <span>{{ importResult.success_count }}</span> 名学生</p>
          
          <div v-if="importResult.errors && importResult.errors.length > 0" class="error-list">
            <p class="error-title">导入过程中有以下错误:</p>
            <ul>
              <li v-for="(error, index) in importResult.errors" :key="index" class="error-item">{{ error }}</li>
            </ul>
          </div>
        </div>
        
        <!-- 导入表单 -->
        <div v-if="!importResult">
          <div class="import-instructions">
            <p>请选择包含学生信息的TXT或CSV文件，每行一条记录，格式为：</p>
            <pre>学号,密码,真实姓名</pre>
            <p>例如：</p>
            <pre>20210001,password123,张三
20210002,password456,李四
20210003,password789,王五</pre>
          </div>
          
          <div class="form-group">
            <label for="import-class">选择班级</label>
            <select id="import-class" v-model="importForm.class_id" required>
              <option value="">请选择班级</option>
              <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
                {{ classItem.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="import-file">选择文件</label>
            <input type="file" id="import-file" @change="handleFileChange" accept=".txt,.csv" required />
          </div>
        </div>
        
        <div class="form-actions">
          <button type="button" @click="importModalVisible = false">{{ importResult ? '关闭' : '取消' }}</button>
          <button v-if="!importResult" type="button" class="btn-primary" @click="importStudents">导入</button>
          <button v-else type="button" class="btn-secondary" @click="importResult = null">重新导入</button>
        </div>
      </div>
    </div>
    
    <!-- 确认清空对话框 -->
    <div v-if="clearModalVisible" class="modal-overlay" @click="clearModalVisible = false">
      <div class="modal" @click.stop>
        <h3>确认清空</h3>
        <p>您确定要清空所有学生数据吗？此操作不可撤销。</p>
        <div class="form-actions">
          <button @click="clearModalVisible = false">取消</button>
          <button class="btn-danger" @click="clearStudents">清空</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from '@/utils/axios';  // 修正导入路径
import { logUserOperation, OperationType } from '../../utils/logger';

// 获取路由参数
const route = useRoute();
const router = useRouter();

// 标签页配置
const tabs = [
  { label: '班级管理', value: 'classes' },
  { label: '教师管理', value: 'teachers' },
  { label: '课程竞赛', value: 'courses' },
  { label: '学生管理', value: 'students' }
];

// 当前活动标签
const activeTab = ref(route.query.tab || 'classes');

// 加载状态
const loading = ref({
  classes: false,
  teachers: false,
  courses: false,
  students: false
});

// 数据
const classes = ref([]);
const teachers = ref([]);
const courses = ref([]);
const students = ref([]);

// 模态框状态
const classModalVisible = ref(false);
const deleteModalVisible = ref(false);
const isEditing = ref(false);
const deleteType = ref('');
const deleteItem = ref(null);

// 表单数据
const classForm = ref({
  id: null,
  name: '',
  teacher_ids: []
});

// 教师相关表单数据
const teacherModalVisible = ref(false);
const teacherForm = ref({
  id: null,
  username: '',
  password: '',
  confirmPassword: '',
  real_name: '',
  role: 'teacher'
});

// 课程相关表单数据
const courseModalVisible = ref(false);
const courseForm = ref({
  id: null,
  name: '',
  teacher_id: '',
  category: '',
  class_ids: []
});

// 学生相关表单数据
const studentModalVisible = ref(false);
const importModalVisible = ref(false);
const clearModalVisible = ref(false);
const selectedFile = ref(null);

const studentFilters = ref({
  classId: ''
});

const studentForm = ref({
  id: null,
  username: '',
  password: '',
  confirmPassword: '',
  real_name: '',
  role: 'student',
  class_ids: []
});

const importForm = ref({
  class_id: '',
  file: null
});

// 添加导入结果状态
const importResult = ref(null);

// 切换标签
const switchTab = async (tab) => {
  activeTab.value = tab;
  router.push({ 
    path: route.path,
    query: { ...route.query, tab }
  });
  await loadTabData(tab);
  
  // 如果是学生管理标签，且班级已加载，设置默认班级
  if (tab === 'students' && classes.value.length > 0 && !studentFilters.value.classId) {
    studentFilters.value.classId = classes.value[0].id;
    fetchStudents();
  }
};

// 加载标签数据
const loadTabData = async (tab) => {
  switch (tab) {
    case 'classes':
      await fetchClasses();
      break;
    case 'teachers':
      await fetchTeachers();
      break;
    case 'courses':
      await fetchCourses();
      break;
    case 'students':
      await fetchClasses();
      await fetchStudents();
      break;
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 格式化班级列表
const formatClassList = (classList) => {
  if (!classList || !Array.isArray(classList) || classList.length === 0) return '无';
  return classList
    .filter(cls => cls && typeof cls === 'object' && cls.name)
    .map(cls => cls.name)
    .join(', ');
};

// 格式化教师名称
const formatTeacherName = (course) => {
  if (course.teacher && course.teacher.username && course.teacher.real_name) {
    return `${course.teacher.username} (${course.teacher.real_name})`;
  } else if (course.teacher_username && course.teacher_real_name) {
    return `${course.teacher_username} (${course.teacher_real_name})`;
  } else if (course.teacher_name) {
    return course.teacher_name;
  }
  return '未分配';
};

// ========== 班级管理相关 ==========

// 获取班级列表
const fetchClasses = async () => {
  loading.value.classes = true;
  try {
    const res = await axios.get('/api/classes/');
    classes.value = Array.isArray(res.data) ? res.data : [];
  } catch (error) {
    console.error('获取班级列表失败', error);
    ElMessage.error('获取班级列表失败');
    classes.value = [];
    
    // 如果是401错误，可能是未登录或token过期
    if (error.response?.status === 401) {
      router.push('/login');
    }
  } finally {
    loading.value.classes = false;
  }
};

// 显示班级添加对话框
const showClassModal = () => {
  isEditing.value = false;
  classForm.value = { 
    id: null, 
    name: '', 
    teacher_ids: [] 
  };
  classModalVisible.value = true;
  
  // 确保教师列表已加载
  if (teachers.value.length === 0) {
    fetchTeachers();
  }
};

// 显示班级编辑对话框
const editClass = async (classItem) => {
  isEditing.value = true;
  
  // 确保教师列表已加载
  if (teachers.value.length === 0) {
    await fetchTeachers();
  }
  
  classForm.value = { 
    id: classItem.id, 
    name: classItem.name,
    teacher_ids: classItem.teachers ? classItem.teachers.map(t => t.id) : []
  };
  classModalVisible.value = true;
};

// 确认删除班级
const confirmDeleteClass = (classItem) => {
  deleteType.value = 'class';
  deleteItem.value = classItem;
  deleteModalVisible.value = true;
};

// 提交班级表单
const submitClassForm = async () => {
  try {
    // 构建提交数据
    const postData = {
      name: classForm.value.name,
      teacher_ids: classForm.value.teacher_ids || []
    };
    
    if (isEditing.value) {
      // 更新班级
      await axios.put(`/api/classes/${classForm.value.id}`, postData);
      logUserOperation(OperationType.UPDATE_CLASS, `班级: ${classForm.value.name}`);
      ElMessage.success('班级更新成功');
    } else {
      // 创建班级
      await axios.post('/api/classes/', postData);
      logUserOperation(OperationType.CREATE_CLASS, `班级: ${classForm.value.name}`);
      ElMessage.success('班级创建成功');
    }
    classModalVisible.value = false;
    await fetchClasses();
  } catch (error) {
    console.error('提交班级失败', error);
    ElMessage.error(isEditing.value ? '更新班级失败' : '创建班级失败');
  }
};

// ========== 教师管理相关 ==========

// 获取教师列表
const fetchTeachers = async () => {
  loading.value.teachers = true;
  try {
    const res = await axios.get('/api/users/teachers');
    teachers.value = Array.isArray(res.data) ? res.data : [];
  } catch (error) {
    console.error('获取教师列表失败', error);
    ElMessage.error('获取教师列表失败');
    teachers.value = [];
  } finally {
    loading.value.teachers = false;
  }
};

// 显示教师添加对话框
const showTeacherModal = () => {
  isEditing.value = false;
  teacherForm.value = { id: null, username: '', password: '', confirmPassword: '', real_name: '', role: 'teacher' };
  teacherModalVisible.value = true;
};

// 显示教师编辑对话框
const editTeacher = (teacher) => {
  isEditing.value = true;
  teacherForm.value = { 
    id: teacher.id, 
    username: teacher.username, 
    password: '',
    confirmPassword: '',
    real_name: teacher.real_name, 
    role: 'teacher' 
  };
  teacherModalVisible.value = true;
};

// 确认删除教师
const confirmDeleteTeacher = (teacher) => {
  deleteType.value = 'teacher';
  deleteItem.value = teacher;
  deleteModalVisible.value = true;
};

// 提交教师表单
const submitTeacherForm = async () => {
  try {
    // 验证表单
    if (!teacherForm.value.username) {
      ElMessage.warning('请输入用户名');
      return;
    }
    
    if (!isEditing.value) {
      if (!teacherForm.value.password) {
        ElMessage.warning('请输入密码');
        return;
      }
      
      if (teacherForm.value.password !== teacherForm.value.confirmPassword) {
        ElMessage.warning('两次输入的密码不一致');
        return;
      }
    } else if (teacherForm.value.password && teacherForm.value.password !== teacherForm.value.confirmPassword) {
      ElMessage.warning('两次输入的密码不一致');
      return;
    }
    
    if (!teacherForm.value.real_name) {
      ElMessage.warning('请输入真实姓名');
      return;
    }
    
    // 构建提交数据
    const postData = {
      username: teacherForm.value.username,
      real_name: teacherForm.value.real_name,
      role: 'teacher'
    };
    
    // 只有在密码不为空时才添加密码字段
    if (teacherForm.value.password) {
      postData.password = teacherForm.value.password;
    }
    
    if (isEditing.value) {
      // 更新教师
      await axios.put(`/api/users/teacher/${teacherForm.value.id}`, postData);
      logUserOperation(OperationType.UPDATE_TEACHER, `教师: ${teacherForm.value.real_name} (${teacherForm.value.username})`);
      ElMessage.success('教师信息更新成功');
    } else {
      // 创建教师
      await axios.post('/api/users/teacher', postData);
      logUserOperation(OperationType.CREATE_TEACHER, `教师: ${teacherForm.value.real_name} (${teacherForm.value.username})`);
      ElMessage.success('教师创建成功');
    }
    teacherModalVisible.value = false;
    await fetchTeachers();
  } catch (error) {
    console.error('提交教师失败', error);
    // 显示后端返回的错误消息或默认消息
    const errorMsg = error.response?.data?.detail || (isEditing.value ? '更新教师失败' : '创建教师失败');
    ElMessage.error(errorMsg);
  }
};

// ========== 课程管理相关 ==========

// 获取课程列表
const fetchCourses = async () => {
  loading.value.courses = true;
  try {
    const res = await axios.get('/api/courses/');
    courses.value = Array.isArray(res.data) ? res.data : [];
  } catch (error) {
    console.error('获取课程列表失败', error);
    ElMessage.error('获取课程列表失败');
    courses.value = [];
  } finally {
    loading.value.courses = false;
  }
};

const showCourseModal = () => {
  isEditing.value = false;
  courseForm.value = { id: null, name: '', teacher_id: '', category: '', class_ids: [] };
  courseModalVisible.value = true;
  
  if (teachers.value.length === 0) fetchTeachers();
  if (classes.value.length === 0) fetchClasses();
};

const editCourse = async (course) => {
  isEditing.value = true;
  
  // 确保教师列表已加载
  if (teachers.value.length === 0) {
    await fetchTeachers();
  }
  
  // 确保班级列表已加载
  if (classes.value.length === 0) {
    await fetchClasses();
  }
  
  // 从course.teacher对象中获取教师ID
  const teacherId = course.teacher ? course.teacher.id : undefined;
  
  const classIds = course.classes && Array.isArray(course.classes)
    ? course.classes.filter(cls => cls && cls.id).map(cls => cls.id)
    : [];
  
  courseForm.value = {
    id: course.id,
    name: course.name,
    teacher_id: teacherId, // 使用从teacher对象中获取的ID
    category: course.category || '',
    class_ids: classIds
  };
  
  courseModalVisible.value = true;
};

const confirmDeleteCourse = (course) => {
  deleteType.value = 'course';
  deleteItem.value = course;
  deleteModalVisible.value = true;
};

const submitCourseForm = async () => {
  try {
    if (isEditing.value) {
      // 更新课程
      await axios.put(`/api/courses/${courseForm.value.id}`, courseForm.value);
      logUserOperation(OperationType.UPDATE_COURSE, `课程: ${courseForm.value.name}`);
      ElMessage.success('课程更新成功');
    } else {
      // 创建课程
      await axios.post('/api/courses/', courseForm.value);
      logUserOperation(OperationType.CREATE_COURSE, `课程: ${courseForm.value.name}`);
      ElMessage.success('课程创建成功');
    }
    courseModalVisible.value = false;
    await fetchCourses();
  } catch (error) {
    console.error('提交课程失败', error);
    ElMessage.error(isEditing.value ? '更新课程失败' : '创建课程失败');
  }
};

// 更新确认删除函数以支持删除课程
const confirmDelete = async () => {
  try {
    if (deleteType.value === 'class') {
      // 删除班级
      await axios.delete(`/api/classes/${deleteItem.value.id}`);
      logUserOperation(OperationType.DELETE_CLASS, `班级: ${deleteItem.value.name}`);
      ElMessage.success('班级删除成功');
      await fetchClasses();
    } else if (deleteType.value === 'teacher') {
      // 删除教师
      await axios.delete(`/api/users/teacher/${deleteItem.value.id}`);
      logUserOperation(OperationType.DELETE_TEACHER, `教师: ${deleteItem.value.real_name} (${deleteItem.value.username})`);
      ElMessage.success('教师删除成功');
      await fetchTeachers();
    } else if (deleteType.value === 'course') {
      // 删除课程
      await axios.delete(`/api/courses/${deleteItem.value.id}`);
      logUserOperation(OperationType.DELETE_COURSE, `课程: ${deleteItem.value.name}`);
      ElMessage.success('课程删除成功');
      await fetchCourses();
    } else if (deleteType.value === 'student') {
      // 删除学生
      await axios.delete(`/api/users/student/${deleteItem.value.id}`);
      logUserOperation(OperationType.DELETE_STUDENT, `学生: ${deleteItem.value.real_name} (${deleteItem.value.username})`);
      ElMessage.success('学生删除成功');
      await fetchStudents();
    }
    deleteModalVisible.value = false;
  } catch (error) {
    console.error('删除失败', error);
    ElMessage.error('删除失败');
  }
};

// ========== 学生管理相关 ==========

// 筛选后的学生列表
const filteredStudents = computed(() => {
  if (!students.value || !Array.isArray(students.value)) {
    return [];
  }

  if (!studentFilters.value.classId) {
    return students.value;
  }
  
  return students.value.filter(student => {
    if (!student || !student.classes || !Array.isArray(student.classes)) {
      return false;
    }
    return student.classes.some(cls => cls && cls.id === studentFilters.value.classId);
  });
});

// 获取学生列表
const fetchStudents = async () => {
  loading.value.students = true;
  try {
    let url = '/api/users/students';
    if (studentFilters.value.classId) {
      url += `?class_id=${studentFilters.value.classId}`;
    }
    
    const res = await axios.get(url);
    students.value = Array.isArray(res.data) ? res.data : [];
  } catch (error) {
    console.error('获取学生列表失败', error);
    ElMessage.error('获取学生列表失败');
    students.value = [];
  } finally {
    loading.value.students = false;
  }
};

const showStudentModal = () => {
  isEditing.value = false;
  studentForm.value = { 
    id: null, 
    username: '', 
    password: '', 
    confirmPassword: '',
    real_name: '', 
    role: 'student', 
    class_ids: studentFilters.value && studentFilters.value.classId ? [studentFilters.value.classId] : []
  };
  studentModalVisible.value = true;
  
  if (classes.value.length === 0) fetchClasses();
};

const editStudent = (student) => {
  isEditing.value = true;
  
  studentForm.value = {
    id: student.id,
    username: student.username,
    password: '',
    confirmPassword: '',
    real_name: student.real_name,
    role: 'student',
    class_ids: student.classes && student.classes.length > 0 ? [student.classes[0].id] : []
  };
  studentModalVisible.value = true;
};

const confirmDeleteStudent = (student) => {
  deleteType.value = 'student';
  deleteItem.value = student;
  deleteModalVisible.value = true;
};

const submitStudentForm = async () => {
  try {
    if (!studentForm.value.username) {
      ElMessage.warning('请输入用户名');
      return;
    }
    
    if (!isEditing.value) {
      if (!studentForm.value.password) {
        ElMessage.warning('请输入密码');
        return;
      }
      
      if (studentForm.value.password !== studentForm.value.confirmPassword) {
        ElMessage.warning('两次输入的密码不一致');
        return;
      }
    } else if (studentForm.value.password && studentForm.value.password !== studentForm.value.confirmPassword) {
      ElMessage.warning('两次输入的密码不一致');
      return;
    }
    
    if (!studentForm.value.real_name) {
      ElMessage.warning('请输入真实姓名');
      return;
    }
    
    if (!studentForm.value.class_ids || studentForm.value.class_ids.length === 0) {
      ElMessage.warning('请选择班级');
      return;
    }
    
    // 构建提交数据
    const postData = {
      username: studentForm.value.username,
      real_name: studentForm.value.real_name,
      role: 'student',
      class_ids: studentForm.value.class_ids || []
    };
    
    // 只有在创建新学生时才添加密码字段
    if (!isEditing.value) {
      postData.password = studentForm.value.password;
    }
    
    if (isEditing.value) {
      // 更新学生
      await axios.put(`/api/users/student/${studentForm.value.id}`, postData);
      logUserOperation(OperationType.UPDATE_STUDENT, `学生: ${studentForm.value.real_name} (${studentForm.value.username})`);
      ElMessage.success('学生信息更新成功');
    } else {
      // 创建学生
      await axios.post('/api/users/student', postData);
      logUserOperation(OperationType.CREATE_STUDENT, `学生: ${studentForm.value.real_name} (${studentForm.value.username})`);
      ElMessage.success('学生创建成功');
    }
    
    studentModalVisible.value = false;
    await fetchStudents();
  } catch (error) {
    console.error('提交学生失败', error);
    // 显示后端返回的错误消息或默认消息
    const errorMsg = error.response?.data?.detail || (isEditing.value ? '更新学生失败' : '创建学生失败');
    ElMessage.error(errorMsg);
  }
};

const showImportModal = () => {
  // 初始化导入表单
  importForm.value = {
    class_id: studentFilters.value && studentFilters.value.classId ? studentFilters.value.classId : '',
    file: null
  };
  importModalVisible.value = true;
  
  // 如果班级列表为空，则获取班级
  if (classes.value.length === 0) {
    fetchClasses();
  }
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (!file) {
    importForm.value.file = null;
    return;
  }
  
  // 验证文件类型
  const fileName = file.name.toLowerCase();
  if (!fileName.endsWith('.txt') && !fileName.endsWith('.csv')) {
    ElMessage.error('请选择TXT或CSV文件');
    event.target.value = ''; // 清空选择
    importForm.value.file = null;
    return;
  }
  
  // 验证文件大小，限制为5MB
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('文件过大，请选择5MB以下的文件');
    event.target.value = ''; // 清空选择
    importForm.value.file = null;
    return;
  }
  
  console.log('已选择文件:', file.name, `(${(file.size / 1024).toFixed(2)} KB)`);
  importForm.value.file = file;
  ElMessage.success(`已选择文件: ${file.name}`);
};

const importStudents = async () => {
  if (!importForm.value.class_id) {
    ElMessage.warning('请选择班级');
    return;
  }
  
  if (!importForm.value.file) {
    ElMessage.warning('请选择文件');
    return;
  }
  
  try {
    const formData = new FormData();
    formData.append('file', importForm.value.file);
    formData.append('class_id', String(importForm.value.class_id));
    
    const response = await axios.post('/api/users/import', formData);
    
    logUserOperation(OperationType.IMPORT_STUDENTS, `导入学生到班级ID: ${importForm.value.class_id}`);
    ElMessage.success(`学生导入成功，共导入 ${response.data.success_count || 0} 名学生`);
    
    importModalVisible.value = false;
    await fetchStudents();
  } catch (error) {
    console.error('导入学生失败', error);
    ElMessage.error('导入学生失败');
  }
};

const exportStudents = async () => {
  try {
    let url = '/api/users/export';
    if (studentFilters.value.classId) {
      url += `?class_id=${studentFilters.value.classId}`;
    }
    
    const res = await axios.get(url);
    
    // 创建下载链接
    const blob = new Blob([res.data.content], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = res.data.filename;
    link.click();
    
    logUserOperation(OperationType.EXPORT_STUDENTS, studentFilters.value.classId ? `导出班级ID: ${studentFilters.value.classId} 的学生` : '导出所有学生');
    ElMessage.success('学生数据导出成功');
  } catch (error) {
    console.error('导出学生失败', error);
    ElMessage.error('导出学生失败');
  }
};

const confirmClearStudents = () => {
  clearModalVisible.value = true;
};

const clearStudents = async () => {
  try {
    let url = '/api/users/clear';
    if (studentFilters.value.classId) {
      url += `?class_id=${studentFilters.value.classId}`;
    }
    
    await axios.delete(url);
    
    logUserOperation(OperationType.CLEAR_STUDENTS, studentFilters.value.classId ? `清空班级ID: ${studentFilters.value.classId} 的学生` : '清空所有学生');
    ElMessage.success('学生数据已清空');
    clearModalVisible.value = false;
    await fetchStudents();
  } catch (error) {
    console.error('清空学生失败', error);
    ElMessage.error('清空学生失败');
  }
};

// 简化强制刷新方法
const forceRefresh = async () => {
  await loadTabData(activeTab.value);
};

// 初始化
onMounted(async () => {
  // 检查用户是否已登录
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/login');
    return;
  }
  
  // 根据URL参数初始化当前标签
  if (route.query.tab && tabs.some(tab => tab.value === route.query.tab)) {
    activeTab.value = route.query.tab;
  }
  
  // 加载当前标签数据
  await loadTabData(activeTab.value);
  
  // 如果是学生管理标签，且班级已加载，设置默认班级
  if (activeTab.value === 'students' && classes.value.length > 0) {
    studentFilters.value.classId = classes.value[0].id;
    fetchStudents();
  }
  
  // 延迟后强制刷新一次数据
  setTimeout(forceRefresh, 1000);
});

// 监听路由变化，切换标签
watch(() => route.query.tab, (newTab) => {
  if (newTab && tabs.some(tab => tab.value === newTab)) {
    activeTab.value = newTab;
    loadTabData(newTab);
  }
}, { immediate: true });

// 获取班级名称
const getClassName = (classId) => {
  if (!classId) return '';
  const classItem = classes.value.find(cls => cls.id === classId);
  return classItem ? classItem.name : '';
};

// 获取教师名称
const getTeacherName = (teacherId) => {
  if (!teacherId) return '';
  const teacher = teachers.value.find(t => t.id === teacherId);
  return teacher ? `${teacher.username} (${teacher.real_name})` : '';
};

// 获取当前选中课程的教师名称
const getCurrentTeacherName = () => {
  // 如果teachers尚未加载，尝试从courses中获取
  if (isEditing.value && courseForm.value.teacher_id) {
    const course = courses.value.find(c => c.id === courseForm.value.id);
    if (course && course.teacher) {
      return `${course.teacher.username} (${course.teacher.real_name})`;
    }
    if (course && course.teacher_username && course.teacher_real_name) {
      return `${course.teacher_username} (${course.teacher_real_name})`;
    }
  }
  return '';
};

// 计算属性 - 是否显示当前教师信息
const showCurrentTeacher = computed(() => {
  // 编辑模式下，且当前教师ID不在teachers列表中时显示
  if (isEditing.value && courseForm.value.teacher_id) {
    return !teachers.value.some(t => t.id === courseForm.value.teacher_id);
  }
  return false;
});

// 添加班级点击跳转函数
const goToStudentsByClass = (classId) => {
  // 设置学生筛选的班级ID
  studentFilters.value.classId = classId;
  // 切换到学生管理标签
  switchTab('students');
};
</script>

<style scoped>
.management-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 60px; /* 增加底部边距，防止与页脚重叠 */
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 20px;
}

.tab-item {
  padding: 8px 16px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #409eff;
}

.tab-item.active {
  color: #409eff;
  border-bottom-color: #409eff;
}

.tab-content {
  min-height: 400px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-header h3 {
  margin: 0;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.loading, .empty-data {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.data-table {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.form-actions button {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-actions button:first-child {
  background-color: #f0f0f0;
  color: #333;
}

.form-actions .btn-primary {
  background-color: #409eff;
  color: white;
}

.form-actions .btn-danger {
  background-color: #f56c6c;
  color: white;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.online {
  background-color: #67c23a;
  color: white;
}

.offline {
  background-color: #909399;
  color: white;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 5px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  min-width: 150px;
}

.checkbox-item input[type="checkbox"] {
  margin-right: 5px;
  width: auto;
}

.filter-section {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
}

.filter-item {
  display: flex;
  align-items: center;
}

.filter-item label {
  margin-right: 10px;
  font-weight: 500;
}

.filter-item select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-width: 200px;
}

.import-instructions {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.import-instructions pre {
  background-color: #eee;
  padding: 8px;
  border-radius: 4px;
  font-family: monospace;
  margin: 10px 0;
}

.selected-class {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
  color: #606266;
  min-height: 36px;
  line-height: 20px;
}

.selected-teacher {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
  color: #606266;
  min-height: 36px;
  line-height: 20px;
}

.class-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
}

.selected-class-info {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.file-format-info {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.import-result {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f8f9;
  border-radius: 4px;
}

.import-result h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #303133;
}

.success-count {
  font-size: 16px;
  margin-bottom: 10px;
}

.success-count span {
  font-weight: bold;
  color: #67c23a;
}

.error-list {
  margin-top: 15px;
  padding: 10px;
  background-color: #fef0f0;
  border-radius: 4px;
  border-left: 4px solid #f56c6c;
}

.error-title {
  margin-top: 0;
  font-weight: bold;
  color: #f56c6c;
}

.error-list ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.error-list li {
  margin-bottom: 5px;
}
</style> 