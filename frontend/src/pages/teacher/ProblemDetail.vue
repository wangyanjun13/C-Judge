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
              :disabled="isSubmitted && !isRedoing"
            ></textarea>
          </div>

          <!-- 提交按钮或重做按钮 -->
          <div class="submission-actions">
            <button v-if="!isSubmitted || isRedoing" @click="submitCode" class="btn btn-submit" :disabled="submitting">
              {{ submitting ? '提交中...' : '提交代码' }}
            </button>
            <button v-else-if="!isExerciseEnded" @click="redoSubmission" class="btn btn-redo">
              重做
            </button>
          </div>
        </div>
      </div>

      <!-- 提交结果显示 -->
      <div v-if="submissionResult" class="submission-result">
        <h3>提交结果</h3>
        <div class="result-card" :class="getStatusClass(submissionResult.status)">
          <div class="result-header">
            <span class="status">{{ submissionResult.status }}</span>
            <span class="score">总分: {{ submissionResult.total_score || 0 }}</span>
          </div>
          <div class="result-details">
            <div class="score-breakdown">
              <div class="score-item">
                <span class="score-label">代码检查:</span>
                <span class="score-value">{{ submissionResult.code_check_score || 0 }}/20</span>
              </div>
              <div class="score-item">
                <span class="score-label">运行测试:</span>
                <span class="score-value">{{ submissionResult.runtime_score || 0 }}/80</span>
              </div>
            </div>
            <div v-if="submissionResult.result && submissionResult.result.code_check" class="code-check-result">
              <h4>代码检查结果</h4>
              <p>{{ submissionResult.result.code_check.message }}</p>
            </div>
            <div v-if="submissionResult.result && submissionResult.result.runtime" class="runtime-result">
              <h4>运行测试结果</h4>
              <p>{{ submissionResult.result.runtime.message }}</p>

              <!-- 显示测试用例详情 -->
              <div v-if="submissionResult.result.runtime.details && submissionResult.result.runtime.details.length > 0" class="test-cases">
                <h5>测试用例详情:</h5>
                <div v-for="(testCase, index) in submissionResult.result.runtime.details" :key="index" 
                     class="test-case" :class="{'test-passed': testCase.result === 0}">
                  <div class="test-case-header">
                    <span class="test-case-name">测试点 {{ testCase.test_case || (index + 1) }}</span>
                    <span class="test-case-status">{{ testCase.result === 0 ? '通过' : '未通过' }}</span>
                  </div>
                  <div v-if="testCase.expected && testCase.actual" class="test-case-details">
                    <div class="test-case-expected">
                      <strong>期望输出:</strong>
                      <pre>{{ testCase.expected }}</pre>
                    </div>
                    <div class="test-case-actual">
                      <strong>实际输出:</strong>
                      <pre>{{ testCase.actual }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
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
import { submitCode as submitCodeAPI, getSubmissionDetail, getSubmissions } from '../../api/submissions';
import { useAuthStore } from '../../store/auth';

const route = useRoute();
const router = useRouter();
const problemId = route.params.id;
const exerciseId = route.query.exercise_id;
const authStore = useAuthStore();

const problem = ref({});
const exercise = ref({});
const loading = ref(true);
const error = ref(null);
const code = ref('');
const selectedLanguage = ref('c');
const submitting = ref(false);
const submissionResult = ref(null);
const isSubmitted = ref(false);
const isRedoing = ref(false);

// 判断练习是否已结束
const isExerciseEnded = computed(() => {
  if (!exercise.value || !exercise.value.end_time) return false;
  return new Date(exercise.value.end_time) <= new Date();
});

// 代码模板
const codeTemplates = {
  'c': '#include <stdio.h>\n\nint main() {\n    // 在此处编写代码\n    \n    return 0;\n}'
};

// 获取题目详情和历史提交
const fetchProblemDetail = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // 获取题目详情
    const problemResult = await getProblemDetail(problemId);
    problem.value = problemResult;
    
    // 获取练习详情（主要用于检查结束时间）
    if (exerciseId) {
      const response = await fetch(`/api/exercises/${exerciseId}`);
      if (response.ok) {
        exercise.value = await response.json();
      }
    }
    
    // 获取历史提交记录
    await fetchSubmissionHistory();
  } catch (err) {
    console.error('获取题目详情失败', err);
    error.value = '获取题目详情失败，请稍后重试';
    ElMessage.error('获取题目详情失败');
  } finally {
    loading.value = false;
  }
};

// 获取历史提交记录
const fetchSubmissionHistory = async () => {
  if (!authStore.user || !authStore.user.id) return;
  
  try {
    const submissions = await getSubmissions({
      userId: authStore.user.id,
      problemId: problemId,
      exerciseId: exerciseId
    });
    
    if (submissions && submissions.length > 0) {
      // 获取最新的一次提交
      const latestSubmission = submissions[0];
      submissionResult.value = latestSubmission;
      code.value = latestSubmission.code;
      isSubmitted.value = true;
    } else {
      // 没有提交记录，使用默认代码模板
      code.value = codeTemplates[selectedLanguage.value] || '';
      isSubmitted.value = false;
    }
  } catch (error) {
    console.error('获取提交历史失败:', error);
    code.value = codeTemplates[selectedLanguage.value] || '';
  }
};

// 提交代码
const submitCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请先编写代码');
    return;
  }

  submitting.value = true;
  
  try {
    const result = await submitCodeAPI(
      authStore.user.id,
      problemId,
      exerciseId,
      code.value,
      selectedLanguage.value
    );
    
    if (result && result.id) {
      // 提交成功，获取详细结果
      submissionResult.value = result;
      isSubmitted.value = true;
      isRedoing.value = false;
      ElMessage.success('代码提交成功');
    } else {
      ElMessage.error('提交失败，请稍后重试');
    }
  } catch (error) {
    console.error('提交代码失败', error);
    ElMessage.error(`提交失败: ${error.response?.data?.detail || error.message}`);
  } finally {
    submitting.value = false;
  }
};

// 重做提交
const redoSubmission = () => {
  isRedoing.value = true;
  ElMessage.info('您可以修改代码后重新提交');
};

// 获取状态对应的样式类
const getStatusClass = (status) => {
  if (!status) return '';
  
  switch (status.toLowerCase()) {
    case 'accepted':
      return 'status-accepted';
    case 'wrong answer':
      return 'status-wrong';
    case 'compilation error':
      return 'status-error';
    case 'time limit exceeded':
      return 'status-limit';
    case 'memory limit exceeded':
      return 'status-limit';
    case 'runtime error':
      return 'status-error';
    case 'system error':
      return 'status-error';
    default:
      return 'status-pending';
  }
};

// 返回上一页
const goBack = () => {
  router.go(-1);
};

onMounted(() => {
  fetchProblemDetail();
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

.code-editor textarea:disabled {
  background-color: #f5f7fa;
  cursor: not-allowed;
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.btn-redo {
  background-color: #e6a23c;
  color: white;
  font-size: 16px;
  padding: 10px 20px;
}

.btn-redo:hover {
  background-color: #ebb563;
}

/* 提交结果样式 */
.submission-result {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.submission-result h3 {
  margin: 0 0 15px;
  color: #303133;
}

.result-card {
  background-color: #f8f8f9;
  border-radius: 8px;
  overflow: hidden;
}

.result-header {
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  font-weight: bold;
}

.result-details {
  padding: 15px;
  background-color: white;
  border: 1px solid #ebeef5;
  border-top: none;
}

.score-breakdown {
  display: flex;
  margin-bottom: 15px;
  border-bottom: 1px dashed #ebeef5;
  padding-bottom: 15px;
}

.score-item {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.score-label {
  font-size: 14px;
  color: #606266;
}

.score-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.code-check-result, .runtime-result {
  margin-top: 15px;
}

.code-check-result h4, .runtime-result h4 {
  margin: 0 0 8px;
  color: #606266;
  font-size: 14px;
}

/* 状态样式 */
.status-accepted .result-header {
  background-color: #67c23a;
}

.status-wrong .result-header {
  background-color: #e6a23c;
}

.status-error .result-header {
  background-color: #f56c6c;
}

.status-limit .result-header {
  background-color: #909399;
}

.status-pending .result-header {
  background-color: #909399;
}

/* 测试用例样式 */
.test-cases {
  margin-top: 15px;
  border-top: 1px dashed #ebeef5;
  padding-top: 15px;
}

.test-cases h5 {
  margin: 0 0 10px;
  color: #606266;
  font-size: 14px;
}

.test-case {
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.test-case-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 10px;
  background-color: #f5f7fa;
}

.test-case-name {
  font-weight: 500;
  color: #606266;
}

.test-case-status {
  font-weight: 500;
}

.test-passed .test-case-header {
  background-color: #f0f9eb;
}

.test-passed .test-case-status {
  color: #67c23a;
}

.test-case-details {
  padding: 10px;
  background-color: white;
}

.test-case-expected, .test-case-actual {
  margin-bottom: 8px;
}

.test-case-details pre {
  margin: 5px 0 0;
  padding: 8px;
  background-color: #f8f8f9;
  border-radius: 4px;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}
</style> 