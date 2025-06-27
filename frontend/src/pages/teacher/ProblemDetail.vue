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

      <div class="main-layout">
        <!-- 左侧区域: 题干和代码编辑 -->
        <div class="left-panel">
          <!-- 题目描述 -->
          <div class="problem-description">
            <div class="problem-html" v-html="problem.html_content"></div>
          </div>

          <!-- 代码编辑区和提交按钮 -->
          <div class="code-submission">
            <!-- 语言选择器 -->
            <div class="language-selector">
              <span class="language-label">编程语言：C</span>
            </div>
            
            <!-- 代码编辑框 -->
            <div class="code-editor">
              <div class="editor-header">
                <span class="language-label">编程语言：C</span>
                <span v-if="isSubmitted" class="history-submission">历史提交</span>
              </div>
              <textarea 
                v-model="code" 
                placeholder="请在此处编写代码..."
                rows="20"
                :disabled="isSubmitted && !isRedoing || isExerciseEnded"
              ></textarea>
            </div>

            <!-- 提交按钮或重做按钮 -->
            <div class="submission-actions">
              <div v-if="isExerciseEnded" class="deadline-notice">
                <span>练习已截止，无法提交</span>
              </div>
              <template v-else>
                <div class="button-group">
                  <button v-if="!isSubmitted || isRedoing" @click="submitCode" class="btn btn-submit" :disabled="submitting">
                    {{ submitting ? '提交中...' : '提交代码' }}
                  </button>
                  <button v-else @click="redoSubmission" class="btn btn-redo">
                    重做此题
                  </button>
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- 右侧区域: 统计信息和提交结果 -->
        <div class="right-panel">
          <!-- 题目统计信息 -->
          <div class="problem-stats">
            <h3>题目统计</h3>
            <div class="stats-overview">
              <div class="pie-chart">
                <!-- 使用内联SVG创建扇形图 -->
                <svg viewBox="0 0 100 100">
                  <circle 
                    cx="50" 
                    cy="50" 
                    r="45" 
                    fill="transparent"
                    stroke="#e6e6e6"
                    stroke-width="10"
                  />
                  <circle 
                    cx="50" 
                    cy="50" 
                    r="45"
                    fill="transparent"
                    :stroke="(submissionResult?.total_score || 0) >= 60 ? '#67c23a' : '#e6a23c'"
                    stroke-width="10"
                    :stroke-dasharray="`${(submissionResult?.total_score || 0) * 2.83} ${283 - (submissionResult?.total_score || 0) * 2.83}`"
                    stroke-dashoffset="-70"
                    transform="rotate(-90 50 50)"
                  />
                  <text x="50" y="45" text-anchor="middle" class="rate-text">得分</text>
                  <text x="50" y="65" text-anchor="middle" class="rate-value">{{ submissionResult?.total_score || 0 }}</text>
                </svg>
              </div>
              <div class="stats-details">
                <div class="stats-item">
                  <div class="stats-label">代码检查</div>
                  <div class="stats-value">{{ submissionResult?.code_check_score || 0 }}/20</div>
                </div>
                <div class="stats-item">
                  <div class="stats-label">运行测试</div>
                  <div class="stats-value">{{ submissionResult?.runtime_score || 0 }}/80</div>
                </div>
              </div>
            </div>

            <div class="error-stats">
              <h4>常见错误分布</h4>
              <div class="error-chart">
                <div class="error-item">
                  <div class="error-label">编译错误</div>
                  <div class="error-bar" style="width: 60%;">60%</div>
                </div>
                <div class="error-item">
                  <div class="error-label">运行超时</div>
                  <div class="error-bar" style="width: 20%;">20%</div>
                </div>
                <div class="error-item">
                  <div class="error-label">答案错误</div>
                  <div class="error-bar" style="width: 15%;">15%</div>
                </div>
                <div class="error-item">
                  <div class="error-label">内存超限</div>
                  <div class="error-bar" style="width: 5%;">5%</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 提交结果显示 -->
          <div v-if="submissionResult" class="submission-result">
            <h3>{{ isSubmitted ? '已经提交' : '提交结果' }}</h3>
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
                    <div class="test-cases-header">
                      <h5>测试用例详情:</h5>
                      <div class="test-summary">
                        <div class="test-status-item">
                          <span class="test-status-dot passed"></span>
                          <span>通过</span>
                        </div>
                        <div class="test-status-item">
                          <span class="test-status-dot failed"></span>
                          <span>未通过</span>
                        </div>
                      </div>
                    </div>
                    <div class="test-cases-content">
                      <div v-for="(testCase, index) in submissionResult.result.runtime.details" :key="index" 
                           class="test-case" :class="{'test-passed': testCase.result === 0}">
                        <div class="test-case-header">
                          <span class="test-case-name">
                            <span class="test-status-dot" :class="testCase.result === 0 ? 'passed' : 'failed'"></span>
                            测试点 {{ testCase.test_case || (index + 1) }}
                          </span>
                          <span class="test-case-status">{{ testCase.result === 0 ? '通过' : '未通过' }}</span>
                        </div>
                        <div class="test-case-details">
                          <template v-if="testCase.input">
                            <div class="test-case-input">
                              <strong>输入数据:</strong>
                              <pre>{{ testCase.input }}</pre>
                            </div>
                          </template>
                          <template v-if="testCase.expected">
                            <div class="test-case-expected">
                              <strong>期望输出:</strong>
                              <pre>{{ testCase.expected }}</pre>
                            </div>
                          </template>
                          <template v-if="testCase.actual">
                            <div class="test-case-actual">
                              <strong>实际输出:</strong>
                              <pre>{{ testCase.actual }}</pre>
                            </div>
                          </template>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-submission">
            <p>提交代码后，结果将显示在此处</p>
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
import { logUserOperation, OperationType } from '../../utils/logger';

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
  'c': '#include <stdio.h>'
};

// 获取题目详情和历史提交
const fetchProblemDetail = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // 获取题目详情
    const problemResult = await getProblemDetail(problemId);
    problem.value = problemResult;
    
    // 记录查看题目的操作
    if (problemResult && problemResult.name) {
      logUserOperation(OperationType.VIEW_PROBLEM, `题目: ${problemResult.name}`);
    }
    
    // 获取练习详情（主要用于检查结束时间）
    if (exerciseId) {
      try {
        const response = await fetch(`/api/exercises/${exerciseId}`);
        if (response.ok) {
          exercise.value = await response.json();
        } else {
          // 即使无法获取练习信息，也允许教师操作
          exercise.value = { end_time: null };
        }
      } catch (error) {
        // 出错时也允许教师操作
        exercise.value = { end_time: null };
      }
    }
    
    // 获取历史提交记录
    await fetchSubmissionHistory();
  } catch (err) {
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
      
      // 获取完整的提交详情(包括代码)
      try {
        const submissionDetail = await getSubmissionDetail(latestSubmission.id);
        submissionResult.value = submissionDetail;
        
        // 确保有代码才更新
        if (submissionDetail && submissionDetail.code) {
          code.value = submissionDetail.code;
          console.log("教师版本：加载历史提交代码成功, ID:", submissionDetail.id);
          isSubmitted.value = true;
        } else {
          console.warn("教师版本：提交记录中无代码内容");
          code.value = codeTemplates[selectedLanguage.value] || '';
        }
      } catch (detailError) {
        console.error("教师版本：获取提交详情失败:", detailError);
        code.value = codeTemplates[selectedLanguage.value] || '';
        submissionResult.value = latestSubmission;
      }
    } else {
      // 没有提交记录，使用默认代码模板
      code.value = codeTemplates[selectedLanguage.value] || '';
      isSubmitted.value = false;
      console.log("教师版本：无历史提交记录，使用模板代码");
    }
  } catch (error) {
    console.error('教师版本：获取提交历史失败:', error);
    code.value = codeTemplates[selectedLanguage.value] || '';
  }
};

// 轮询获取提交结果
const pollSubmissionResult = async (submissionId) => {
  let retries = 0;
  const maxRetries = 10;
  const interval = 1000; // 1秒

  const poll = async () => {
    try {
      const detail = await getSubmissionDetail(submissionId);
      console.log('获取到提交详情:', detail);
      if (detail?.result?.runtime?.details) {
        console.log('测试用例详情:', detail.result.runtime.details);
      }
      if (detail?.result?.code_check || detail?.result?.runtime || retries >= maxRetries) {
        submissionResult.value = detail;
        return;
      }
      retries++;
      setTimeout(poll, interval);
    } catch (error) {
      console.error('轮询提交结果失败:', error);
    }
  };

  await poll();
};

// 提交代码
const submitCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请先编写代码');
    return;
  }
  
  // 检查练习是否已截止
  if (isExerciseEnded.value) {
    ElMessage.warning('练习已截止，无法提交');
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
      submissionResult.value = result;
      code.value = result.code || code.value;
      isSubmitted.value = true;
      isRedoing.value = false;
      ElMessage.success('代码提交成功');
      
      // 开始轮询获取完整结果
      await pollSubmissionResult(result.id);
      
      // 记录提交代码操作
      logUserOperation(OperationType.SUBMIT_CODE, `题目: ${problem.value.name || problemId}`);
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
  // 检查练习是否已截止
  if (isExerciseEnded.value) {
    ElMessage.warning('练习已截止，无法重做');
    return;
  }
  
  // 记录重做提交的操作
  logUserOperation(OperationType.REDO_SUBMISSION, `题目: ${problem.value.name || problemId}`);
  
  // 将isRedoing置为true，但保留当前代码
  isRedoing.value = true;
  ElMessage.info('您可以在历史代码的基础上进行修改后重新提交');
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
  height: auto;
  margin-bottom: 60px;
  overflow: visible;
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

.main-layout {
  display: flex;
  gap: 20px;
  min-height: calc(100vh - 150px);
  height: auto;
}

.left-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: visible;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.problem-description {
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
  max-height: none;
  border: none;
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
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: auto;
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
  position: relative;
  min-height: 600px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background-color: #f5f7fa;
}

.history-submission {
  font-size: 14px;
  color: #409eff;
  background-color: #ecf5ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.code-editor textarea {
  width: 100%;
  height: 100%;
  min-height: 600px;
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
  align-items: center;
  padding: 15px 0;
  position: relative;
  z-index: 5;
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
  display: flex;
  flex-direction: column;
  height: 600px;
}

.test-cases-header {
  flex-shrink: 0;
  margin-bottom: 15px;
}

.test-cases-header h5 {
  margin: 0 0 10px;
  color: #606266;
  font-size: 14px;
}

.test-summary {
  display: flex;
  gap: 20px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #ebeef5;
}

.test-cases-content {
  flex-grow: 1;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  background-color: #fff;
}

/* 美化滚动条 */
.test-cases-content::-webkit-scrollbar {
  width: 8px;
}

.test-cases-content::-webkit-scrollbar-thumb {
  background-color: #909399;
  border-radius: 4px;
}

.test-cases-content::-webkit-scrollbar-track {
  background-color: #f5f7fa;
  border-radius: 4px;
}

/* 调整测试用例样式 */
.test-case {
  margin-bottom: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.test-case:last-child {
  margin-bottom: 0;
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
  display: flex;
  align-items: center;
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

.test-case-input,
.test-case-expected,
.test-case-actual {
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
  font-family: monospace;
}

/* 添加截止信息样式 */
.deadline-notice {
  background-color: #909399;
  color: white;
  padding: 10px 15px;
  border-radius: 4px;
  text-align: center;
  font-weight: 500;
}

.problem-stats {
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.problem-stats h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.stats-overview {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.pie-chart {
  width: 150px;
  height: 150px;
}

.pie-chart svg {
  width: 100%;
  height: 100%;
}

.rate-text {
  font-size: 14px;
  fill: #606266;
}

.rate-value {
  font-size: 20px;
  font-weight: bold;
  fill: #303133;
}

.stats-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stats-item {
  flex: 1;
  min-width: 80px;
  padding: 10px;
  background-color: #f8f8f9;
  border-radius: 6px;
  text-align: center;
}

.stats-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.stats-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.error-stats h4 {
  margin: 0 0 10px;
  color: #606266;
  font-size: 14px;
}

.error-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.error-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-label {
  width: 70px;
  font-size: 12px;
  color: #606266;
}

.error-bar {
  height: 20px;
  background-color: #409eff;
  color: white;
  font-size: 12px;
  line-height: 20px;
  padding: 0 8px;
  border-radius: 10px;
  text-align: right;
}

.no-submission {
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  text-align: center;
  color: #909399;
}

/* 调整按钮组样式 */
.button-group {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.btn-submit, .btn-redo {
  min-width: 120px;
  height: 40px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.btn-submit {
  background-color: #67c23a;
  color: white;
  border: none;
}

.btn-submit:hover {
  background-color: #85ce61;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.2);
}

.btn-redo {
  background-color: #e6a23c;
  color: white;
  border: none;
}

.btn-redo:hover {
  background-color: #ebb563;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.2);
}

/* 右侧面板布局调整 */
.right-panel {
  position: sticky;
  top: 20px;
  height: fit-content;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.problem-stats {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.submission-result {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

/* 响应式调整 */
@media (max-width: 992px) {
  .main-layout {
    flex-direction: column;
  }
  
  .right-panel {
    position: static;
    width: 100%;
  }
  
  .pie-chart {
    width: 120px;
    height: 120px;
  }
}

.test-status-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.test-status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 5px;
}

.test-status-dot.passed {
  background-color: #67c23a;
}

.test-status-dot.failed {
  background-color: #f56c6c;
}
</style> 