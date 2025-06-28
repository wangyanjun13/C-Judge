<template>
  <div class="submission-detail-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack" class="btn btn-primary">返回</button>
    </div>
    <div v-else class="submission-content">
      <!-- 页面头部 -->
      <div class="header">
        <h2>{{ problem.name }} <span v-if="problem.chinese_name" class="chinese-name">{{ problem.chinese_name }}</span></h2>
        <div class="user-info">
          <span class="username">{{ userInfo.username }} {{ userInfo.real_name ? `(${userInfo.real_name})` : '' }}</span>
          <span class="role-badge" :class="getRoleBadgeClass(userInfo.role)">{{ getRoleText(userInfo.role) }}</span>
        </div>
        <div class="actions">
          <button @click="goBack" class="btn btn-back">返回</button>
        </div>
      </div>
      
      <div class="main-layout">
        <!-- 左侧区域: 题干和代码 -->
        <div class="left-panel">
          <!-- 题目描述 -->
          <div class="problem-description">
            <h3>题目描述</h3>
            <div class="problem-html" v-html="problem.html_content"></div>
          </div>

          <!-- 代码展示区 -->
          <div class="code-section">
            <div class="section-header">
              <h3>提交代码</h3>
              <div class="submission-meta">
                <span class="meta-item">提交时间：{{ formatDateTime(submission.submitted_at) }}</span>
                <span class="meta-item">语言：{{ submission.language }}</span>
                <span class="meta-item">状态：<span :class="getStatusClass(submission.status)">{{ submission.status }}</span></span>
              </div>
            </div>
            <div class="code-display">
              <pre><code>{{ submission.code }}</code></pre>
            </div>
          </div>
        </div>

        <!-- 右侧区域: 评测结果 -->
        <div class="right-panel">
          <!-- 评分统计 -->
          <div class="score-summary">
            <h3>评分统计</h3>
            <div class="score-chart">
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
                    :stroke="(submission.total_score || 0) >= 60 ? '#67c23a' : '#e6a23c'"
                    stroke-width="10"
                    :stroke-dasharray="`${(submission.total_score || 0) * 2.83} ${283 - (submission.total_score || 0) * 2.83}`"
                    stroke-dashoffset="-70"
                    transform="rotate(-90 50 50)"
                  />
                  <text x="50" y="45" text-anchor="middle" class="rate-text">得分</text>
                  <text x="50" y="65" text-anchor="middle" class="rate-value">{{ submission.total_score || 0 }}</text>
                </svg>
              </div>
              <div class="score-details">
                <div class="score-item">
                  <div class="score-label">代码检查</div>
                  <div class="score-value">{{ submission.code_check_score || 0 }}/20</div>
                </div>
                <div class="score-item">
                  <div class="score-label">运行测试</div>
                  <div class="score-value">{{ submission.runtime_score || 0 }}/80</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 提交结果详情 -->
          <div class="result-details">
            <h3>评测结果</h3>
            <div class="result-card" :class="getStatusClass(submission.status)">
              <div class="result-header">
                <span class="status">{{ submission.status }}</span>
                <span class="score">总分: {{ submission.total_score || 0 }}</span>
              </div>
              <div class="result-content">
                <div class="score-breakdown">
                  <div class="score-item">
                    <span class="score-label">代码检查:</span>
                    <span class="score-value">{{ submission.code_check_score || 0 }}/20</span>
                  </div>
                  <div class="score-item">
                    <span class="score-label">运行测试:</span>
                    <span class="score-value">{{ submission.runtime_score || 0 }}/80</span>
                  </div>
                </div>
                <div v-if="submission.result && submission.result.code_check" class="code-check-result">
                  <h4>代码检查结果</h4>
                  <p>{{ submission.result.code_check.message }}</p>
                </div>
                <div v-if="submission.result && submission.result.runtime" class="runtime-result">
                  <h4>运行测试结果</h4>
                  <p>{{ submission.result.runtime.message }}</p>
                  
                  <!-- 显示测试用例详情 -->
                  <div v-if="submission.result.runtime.details && submission.result.runtime.details.length > 0" class="test-cases">
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
                      <div v-for="(testCase, index) in submission.result.runtime.details" :key="index" 
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
import { getSubmissionDetail } from '../../api/submissions';
import { useAuthStore } from '../../store/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const submissionId = route.params.id;
const problemId = route.query.problem_id;
const userId = route.query.user_id;
const exerciseId = route.query.exercise_id;
const username = route.query.username || '';
const realName = route.query.real_name || '';

const loading = ref(true);
const error = ref(null);
const problem = ref({});
const submission = ref({});
const userInfo = ref({
  username: username,
  real_name: realName,
  role: 'student'  // 默认为学生角色
});

// 获取提交详情和相关信息
const fetchSubmissionDetail = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // 获取提交详情
    const submissionData = await getSubmissionDetail(submissionId);
    submission.value = submissionData;
    
    // 获取题目详情
    const problemData = await getProblemDetail(problemId || submissionData.problem_id);
    problem.value = problemData;
    
    // 如果URL中没有提供用户名和真实姓名，尝试从API获取
    if (!username) {
      try {
        const response = await fetch(`/api/users/${userId || submissionData.user_id}`);
        if (response.ok) {
          const userData = await response.json();
          userInfo.value = userData;
        }
      } catch (err) {
        console.error('获取用户信息失败:', err);
      }
    }
  } catch (err) {
    console.error('获取提交详情失败:', err);
    error.value = '获取提交详情失败，请稍后重试';
    ElMessage.error('获取提交详情失败');
  } finally {
    loading.value = false;
  }
};

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '未知时间';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
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

// 获取角色标签样式
const getRoleBadgeClass = (role) => {
  if (!role) return 'role-student';
  
  switch (role.toLowerCase()) {
    case 'admin':
      return 'role-admin';
    case 'teacher':
      return 'role-teacher';
    case 'student':
      return 'role-student';
    default:
      return 'role-student';
  }
};

// 获取角色文本
const getRoleText = (role) => {
  if (!role) return '学生';
  
  switch (role.toLowerCase()) {
    case 'admin':
      return '管理员';
    case 'teacher':
      return '教师';
    case 'student':
      return '学生';
    default:
      return '学生';
  }
};

// 返回上一页
const goBack = () => {
  router.go(-1);
};

onMounted(() => {
  fetchSubmissionDetail();
});
</script>

<style scoped>
.submission-detail-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  min-height: calc(100vh - 120px);
  height: auto;
  margin-bottom: 60px;
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
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  flex: 1;
}

.chinese-name {
  font-size: 16px;
  color: #606266;
  margin-left: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  margin-right: 20px;
}

.username {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-right: 10px;
}

.role-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: white;
}

.role-admin {
  background-color: #409eff;
}

.role-teacher {
  background-color: #67c23a;
}

.role-student {
  background-color: #909399;
}

.actions {
  display: flex;
  gap: 10px;
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

.main-layout {
  display: flex;
  gap: 20px;
  min-height: calc(100vh - 200px);
  height: auto;
}

.left-panel {
  flex: 3;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.problem-description {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.problem-description h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 18px;
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

.code-section {
  padding: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.section-header {
  padding: 15px 20px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.section-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 18px;
}

.submission-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
  color: #606266;
}

.meta-item {
  display: flex;
  align-items: center;
}

.code-display {
  padding: 20px;
  max-height: 600px;
  overflow-y: auto;
}

.code-display pre {
  margin: 0;
  padding: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.5;
}

.score-summary {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.score-summary h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 18px;
}

.score-chart {
  display: flex;
  align-items: center;
  gap: 20px;
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

.score-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.score-item {
  padding: 10px;
  background-color: #f8f8f9;
  border-radius: 6px;
  text-align: center;
}

.score-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.score-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.result-details {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.result-details h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 18px;
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

.result-content {
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

.code-check-result, .runtime-result {
  margin-top: 15px;
}

.code-check-result h4, .runtime-result h4 {
  margin: 0 0 8px;
  color: #606266;
  font-size: 16px;
}

/* 状态样式 */
.status-accepted {
  color: #67c23a;
}

.status-wrong {
  color: #e6a23c;
}

.status-error {
  color: #f56c6c;
}

.status-limit {
  color: #909399;
}

.status-pending {
  color: #909399;
}

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

.test-cases-header {
  margin-bottom: 15px;
}

.test-cases-header h5 {
  margin: 0 0 10px;
  color: #606266;
  font-size: 16px;
}

.test-summary {
  display: flex;
  gap: 20px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #ebeef5;
}

.test-cases-content {
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  background-color: #fff;
}

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

/* 响应式调整 */
@media (max-width: 992px) {
  .main-layout {
    flex-direction: column;
  }
  
  .pie-chart {
    width: 120px;
    height: 120px;
  }
}
</style> 