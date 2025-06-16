<template>
  <div class="problem-detail-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack" class="btn btn-primary">返回</button>
    </div>
    <div v-else class="problem-content">
      <!-- 头部信息 -->
      <div class="header">
        <h2>{{ problem.chinese_name || problem.name }}</h2>
        <div class="actions">
          <button @click="goBack" class="btn btn-back">返回</button>
        </div>
      </div>

      <div class="problem-layout">
        <!-- 左侧：题目描述 -->
        <div class="problem-description">
          <div class="problem-info">
            <div class="info-item">
              <span class="label">时间限制：</span>
              <span class="value">{{ problem.time_limit }}ms</span>
            </div>
            <div class="info-item">
              <span class="label">内存限制：</span>
              <span class="value">{{ problem.memory_limit }}MB</span>
            </div>
          </div>
          
          <!-- 题目内容 -->
          <div class="problem-html" v-html="problem.html_content"></div>
        </div>

        <!-- 右侧：代码编辑区和提交按钮 -->
        <div class="code-submission">
          <div class="language-selector">
            <label for="language">编程语言：</label>
            <select id="language" v-model="selectedLanguage">
              <option v-for="lang in availableLanguages" :key="lang.value" :value="lang.value">
                {{ lang.label }}
              </option>
            </select>
          </div>

          <!-- 代码编辑框 -->
          <div class="code-editor">
            <textarea 
              v-model="code" 
              placeholder="请在此处编写代码..."
              rows="20"
            ></textarea>
          </div>

          <!-- 提交按钮 -->
          <div class="submission-actions">
            <button @click="submitCode" class="btn btn-submit">提交代码</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getProblemDetail } from '../../api/exercises';

const route = useRoute();
const router = useRouter();
const problemId = route.params.id;
const exerciseId = route.query.exercise_id;

const problem = ref({});
const loading = ref(true);
const error = ref(null);
const code = ref('');
const selectedLanguage = ref('c');

// 可用的编程语言
const availableLanguages = [
  { label: 'C', value: 'c' },
  { label: 'C++', value: 'cpp' },
  { label: 'Java', value: 'java' },
  { label: 'Python', value: 'python' }
];

// 获取题目详情
const fetchProblemDetail = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await getProblemDetail(problemId);
    problem.value = result;
  } catch (err) {
    console.error('获取题目详情失败', err);
    error.value = '获取题目详情失败，请稍后重试';
    ElMessage.error('获取题目详情失败');
  } finally {
    loading.value = false;
  }
};

// 提交代码
const submitCode = () => {
  if (!code.value.trim()) {
    ElMessage.warning('请先编写代码');
    return;
  }
  
  ElMessage.info('代码提交功能正在开发中...');
  
  // 这里将来添加代码提交的API调用
};

// 返回上一页
const goBack = () => {
  router.go(-1);
};

onMounted(() => {
  fetchProblemDetail();
  
  // 可以添加一些代码模板
  const codeTemplates = {
    'c': '#include <stdio.h>\n\nint main() {\n    // 在此处编写代码\n    \n    return 0;\n}',
    'cpp': '#include <iostream>\nusing namespace std;\n\nint main() {\n    // 在此处编写代码\n    \n    return 0;\n}',
    'java': 'public class Main {\n    public static void main(String[] args) {\n        // 在此处编写代码\n        \n    }\n}',
    'python': '# 在此处编写代码\n\n'
  };
  
  // 根据选择的语言设置代码模板
  code.value = codeTemplates[selectedLanguage.value] || '';
});
</script>

<style scoped>
.problem-detail-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  min-height: calc(100vh - 120px);
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

.problem-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .problem-layout {
    grid-template-columns: 1fr;
  }
}

.problem-description {
  padding-right: 20px;
  border-right: 1px solid #eee;
}

.problem-info {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f8f8f9;
  border-radius: 4px;
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

.problem-html {
  line-height: 1.6;
  color: #303133;
  overflow-wrap: break-word;
}

.problem-html :deep(p) {
  margin: 1em 0;
}

.problem-html :deep(pre) {
  background-color: #f8f8f9;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.code-submission {
  display: flex;
  flex-direction: column;
}

.language-selector {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.language-selector label {
  margin-right: 10px;
  font-weight: 500;
  color: #606266;
}

.language-selector select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.code-editor {
  flex-grow: 1;
  margin-bottom: 15px;
}

.code-editor textarea {
  width: 100%;
  height: 100%;
  min-height: 400px;
  padding: 12px;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.5;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
}

.submission-actions {
  display: flex;
  justify-content: flex-end;
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

.btn-submit {
  background-color: #67c23a;
  color: white;
  font-size: 16px;
  padding: 10px 20px;
}

.btn-submit:hover {
  background-color: #85ce61;
}
</style> 