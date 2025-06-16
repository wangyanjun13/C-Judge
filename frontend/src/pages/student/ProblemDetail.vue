<template>
  <div class="problem-detail-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack" class="btn btn-primary">返回</button>
    </div>
    <div v-else class="problem-content">
      <!-- 右上角返回按钮 -->
      <div class="top-actions">
        <button @click="goBack" class="btn btn-back">返回</button>
      </div>

      <div class="problem-layout">
        <!-- 左侧：题目描述 -->
        <div class="problem-description">
          <!-- 题目内容 -->
          <div class="problem-html" v-html="problem.html_content"></div>
        </div>

        <!-- 右侧：代码编辑区和提交按钮 -->
        <div class="code-submission">
          <!-- 语言选择器 -->
          <div class="language-selector">
            <span class="language-label">编程语言：C</span>
          </div>
          
          <!-- 代码编辑框 -->
          <div class="code-editor">
            <textarea 
              v-model="code" 
              placeholder="请在此处编写代码..."
              rows="25"
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
import { ref, onMounted } from 'vue';
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

// 代码模板
const codeTemplates = {
  'c': '#include <stdio.h>\n\nint main() {\n    // 在此处编写代码\n    \n    return 0;\n}'
};

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
  code.value = codeTemplates[selectedLanguage.value] || '';
});
</script>

<style scoped>
.problem-detail-container {
  padding: 10px;
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

.top-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 5px;
}

.problem-layout {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 20px;
  height: calc(100vh - 155px);
}

@media (max-width: 768px) {
  .problem-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
}

.problem-description {
  padding-right: 20px;
  border-right: 1px solid #eee;
  overflow-y: auto;
  max-height: 100%;
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
  height: 100%;
}

.language-selector {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.language-label {
  font-weight: 500;
  color: #606266;
}

.code-editor {
  flex-grow: 1;
  margin-bottom: 15px;
}

.code-editor textarea {
  width: 100%;
  height: 100%;
  min-height: 500px;
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