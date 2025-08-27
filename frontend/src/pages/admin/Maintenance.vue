<template>
  <div class="maintenance-container">
    <div class="tab-header">
      <div class="tab" :class="{ active: activeTab === 'problems' }" @click="activeTab = 'problems'">
        题库维护
      </div>
      <div class="tab" :class="{ active: activeTab === 'upload' }" @click="activeTab = 'upload'">
        上传题库
      </div>
      <div class="tab" :class="{ active: activeTab === 'tags' }" @click="activeTab = 'tags'">
        标签管理
      </div>
      <div class="tab" :class="{ active: activeTab === 'approval' }" @click="activeTab = 'approval'">
        标签审核
      </div>
    </div>

    <!-- 题库维护 -->
    <div v-if="activeTab === 'problems'" class="tab-content">
      <!-- 新的标签筛选布局 -->
      <div class="tags-filter-container">
        <div v-for="tagType in tagTypes" :key="tagType.id" class="tag-type-row">
          <div class="tag-type-label">{{ tagType.name }}：</div>
          <div class="tag-items">
            <div 
              class="tag-item" 
              :class="{ active: selectedTagIds[tagType.id] === '' }"
              @click="selectTag(tagType.id, '')">
              全部
            </div>
            <div 
              v-for="tag in getTagsByType(tagType.id)" 
              :key="tag.id" 
              class="tag-item"
              :class="{ active: selectedTagIds[tagType.id] === tag.id }"
              :style="{ '--tag-color': tag.tag_type_id ? `var(--tag-color-${tag.tag_type_id % 10})` : '#409eff' }"
              @click="selectTag(tagType.id, tag.id)">
              {{ tag.name }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">
        加载中...
      </div>
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      <div v-else-if="problems.length === 0" class="empty-state">
        暂无试题
      </div>
      <div v-else class="problems-table-container">
        <table class="problems-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>操作</th>
              <th>试题名称</th>
              <th>试题中文名称</th>
              <th>标签</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(problem, index) in problems" :key="problem.name">
              <td>{{ index + 1 }}</td>
              <td>
                <button @click="openTagDialog(problem)" class="btn btn-edit">打标签</button>
                <button @click="confirmDelete(problem)" class="btn btn-delete">删除</button>
              </td>
              <td>{{ problem.name }}</td>
              <td>{{ problem.chinese_name }}</td>
              <td class="tags-cell">
                <div v-if="problemTags[problem.data_path] && problemTags[problem.data_path].length > 0" class="problem-tags">
                  <template v-for="(tags, tagType) in groupTagsByType(problemTags[problem.data_path])" :key="tagType">
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
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 上传题库 -->
    <div v-if="activeTab === 'upload'" class="tab-content">
      <div class="upload-container">
        
        <div class="upload-layout">
          <!-- 左侧表单 -->
          <div class="form-container">
            <!-- 基本信息卡片 -->
            <div class="form-card">
              <div class="card-header">
                <h3 class="card-title">📝 基本信息</h3>
              </div>
              <div class="card-body">
                <div class="form-grid">
                  <div class="form-field">
                    <label class="field-label required">题目名称（英文）</label>
                    <input 
                      v-model="problemForm.name" 
                      placeholder="例如: fibonacci（只允许字母、数字、下划线）"
                      class="field-input"
                      :class="{ error: errors.name }"
                      @input="validateField('name')"
                    />
                    <div v-if="errors.name" class="error-message">{{ errors.name }}</div>
                    <div class="field-hint">将用作题目文件夹名称，不能重复</div>
                  </div>
                  
                  <div class="form-field">
                    <label class="field-label required">题目中文名称</label>
                    <input 
                      v-model="problemForm.chineseName" 
                      placeholder="例如: 斐波那契数列"
                      class="field-input"
                      :class="{ error: errors.chineseName }"
                      @input="validateField('chineseName')"
                    />
                    <div v-if="errors.chineseName" class="error-message">{{ errors.chineseName }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 题目描述卡片 -->
            <div class="form-card">
              <div class="card-header">
                <h3 class="card-title">📖 题目描述</h3>
                <div class="header-actions">
                  <button 
                    type="button" 
                    @click="useDescriptionTemplate"
                    class="action-btn template-btn"
                  >
                    <span class="btn-icon">📝</span>
                    使用模板
                  </button>
                  <button 
                    type="button" 
                    @click="showDescriptionPreview = !showDescriptionPreview"
                    class="action-btn preview-btn"
                  >
                    <span class="btn-icon">👁️</span>
                    {{ showDescriptionPreview ? '隐藏预览' : '预览效果' }}
                  </button>
                  <button 
                    type="button" 
                    @click="showFormatHelp = !showFormatHelp"
                    class="action-btn help-btn"
                  >
                    <span class="btn-icon">❓</span>
                    格式帮助
                  </button>
                </div>
              </div>
              <div class="card-body">
                <!-- 格式帮助 -->
                <div v-if="showFormatHelp" class="format-help">
                  <h5>🔍 自动格式识别说明</h5>
                  <p>系统会自动识别以下格式并转换为统一的HTML显示：</p>
                  <div class="help-grid">
                    <div class="help-item"><strong>题目描述：</strong> 以"题目描述："、"问题描述："或"描述："开头</div>
                    <div class="help-item"><strong>输入格式：</strong> 以"输入格式："、"输入："开头</div>
                    <div class="help-item"><strong>输出格式：</strong> 以"输出格式："、"输出："开头</div>
                    <div class="help-item"><strong>输入示例：</strong> 以"输入示例："、"样例输入："开头</div>
                    <div class="help-item"><strong>输出示例：</strong> 以"输出示例："、"样例输出："开头</div>
                    <div class="help-item"><strong>数据范围：</strong> 以"数据范围："、"约束条件："开头</div>
                    <div class="help-item"><strong>注意事项：</strong> 以"注意："、"备注："开头</div>
                  </div>
                  <div class="help-note">
                    💡 <strong>提示：</strong> 如果没有使用上述格式，整个内容将作为题目描述处理。
                  </div>
                </div>
                
                <div class="form-field full-width">
                  <label class="field-label required">题目描述内容</label>
                  <textarea 
                    v-model="problemForm.description" 
                    rows="10"
                    placeholder="请输入题目描述，推荐使用结构化格式：&#10;&#10;题目描述：&#10;这里是题目的具体要求...&#10;&#10;输入：&#10;输入格式说明...&#10;&#10;输出：&#10;输出格式说明...&#10;&#10;输入示例：&#10;16 24&#10;&#10;输出示例：&#10;8 48&#10;&#10;数据范围：&#10;数据范围说明...&#10;&#10;注意：&#10;特别注意事项..."
                    class="field-textarea"
                    :class="{ error: errors.description }"
                    @input="validateField('description')"
                  ></textarea>
                  
                  <!-- 预览面板 -->
                  <div v-if="showDescriptionPreview" class="preview-panel">
                    <div class="preview-header">
                      <h5>🎯 预览效果</h5>
                    </div>
                    <div class="preview-content" v-html="formattedDescription"></div>
                  </div>
                  
                  <div class="field-meta">
                    <div v-if="errors.description" class="error-message">{{ errors.description }}</div>
                    <div class="char-count">{{ problemForm.description.length }}/{{ LIMITS.description }} 字符</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 测试用例卡片 -->
            <div class="form-card">
              <div class="card-header">
                <h3 class="card-title">🧪 测试用例</h3>
              </div>
              <div class="card-body">
                <div class="testcases-grid">
                  <div 
                    v-for="(testcase, index) in problemForm.testcases" 
                    :key="index" 
                    class="testcase-card"
                    :class="{ error: errors[`testcase_${index}`] }"
                  >
                    <div class="testcase-header">
                      <h4 class="testcase-title">
                        <span class="case-number">{{ index + 1 }}</span>
                        测试用例 {{ index + 1 }}
                      </h4>
                      <button 
                        v-if="problemForm.testcases.length > 1"
                        @click="removeTestcase(index)" 
                        class="remove-btn"
                        type="button"
                        title="删除此测试用例"
                      >
                        ✕
                      </button>
                    </div>
                    
                    <div class="testcase-content">
                      <div class="io-section">
                        <label class="io-label">
                          📥 输入数据
                        </label>
                        <textarea 
                          v-model="testcase.input" 
                          placeholder="请输入测试数据..."
                          rows="4"
                          class="io-input"
                          @input="validateTestcase(index)"
                        ></textarea>
                        <div class="char-counter">{{ testcase.input.length }}/{{ LIMITS.testcase_input }}</div>
                      </div>
                      
                      <div class="io-section">
                        <label class="io-label">
                          📤 期望输出
                        </label>
                        <textarea 
                          v-model="testcase.output" 
                          placeholder="请输入期望的输出结果..."
                          rows="4"
                          class="io-input"
                          @input="validateTestcase(index)"
                        ></textarea>
                        <div class="char-counter">{{ testcase.output.length }}/{{ LIMITS.testcase_output }}</div>
                      </div>
                    </div>
                    
                    <div v-if="errors[`testcase_${index}`]" class="error-message">
                      {{ errors[`testcase_${index}`] }}
                    </div>
                  </div>
                  
                  <div class="action-card">
                    <div class="action-buttons">
                      <button 
                        @click="addTestcase()" 
                        class="action-btn add-btn"
                        :disabled="problemForm.testcases.length >= LIMITS.max_testcases"
                        type="button"
                      >
                        <span class="btn-icon">➕</span>
                        添加测试用例 ({{ problemForm.testcases.length }}/{{ LIMITS.max_testcases }})
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 参考代码卡片 -->
            <div class="form-card">
              <div class="card-header">
                <h3 class="card-title">💻 参考代码</h3>
                <div class="header-actions">
                  <button 
                    type="button" 
                    @click="showReferencePreview = !showReferencePreview"
                    class="action-btn preview-btn"
                  >
                    <span class="btn-icon">👁️</span>
                    {{ showReferencePreview ? '隐藏预览' : '预览代码' }}
                  </button>
                </div>
              </div>
              <div class="card-body">
                <div class="form-field full-width">
                  <label class="field-label">参考代码（可选）</label>
                  <textarea 
                    v-model="problemForm.referenceAnswer" 
                    rows="8"
                    placeholder="请输入参考代码，支持C/C++、Java、Python等语言...&#10;&#10;示例：&#10;#include &lt;stdio.h&gt;&#10;int main() {&#10;    int a, b;&#10;    scanf(&quot;%d %d&quot;, &amp;a, &amp;b);&#10;    printf(&quot;%d&quot;, a + b);&#10;    return 0;&#10;}"
                    class="field-textarea code-textarea"
                  ></textarea>
                  
                  <!-- 代码预览区域 -->
                  <div v-if="showReferencePreview && problemForm.referenceAnswer" class="preview-panel">
                    <div class="preview-header">
                      <h5>💻 代码预览</h5>
                    </div>
                    <div class="preview-content">
                      <pre class="code-preview">{{ problemForm.referenceAnswer }}</pre>
                    </div>
                  </div>
                  
                  <div class="field-meta">
                    <div class="char-count">{{ problemForm.referenceAnswer.length }}/{{ LIMITS.reference_answer }} 字符</div>
                    <div class="field-hint">提供参考代码有助于学生理解解题思路，可选填写</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作按钮卡片 -->
            <div class="form-card action-card">
              <div class="card-body">
                <div class="action-buttons">
                  <button @click="resetForm()" class="action-btn secondary-btn" type="button">
                    <span class="btn-icon">🔄</span>
                    清空重置
                  </button>
                  <button @click="previewProblem()" class="action-btn info-btn" type="button" :disabled="!isFormValid">
                    <span class="btn-icon">👁️</span>
                    预览题目
                  </button>
                  <button @click="submitCustomProblem()" class="action-btn primary-btn" type="button" :disabled="!isFormValid || isSubmitting">
                    <span class="btn-icon">{{ isSubmitting ? '⏳' : '🚀' }}</span>
                    {{ isSubmitting ? '创建中...' : '创建题目' }}
                  </button>
                </div>
              </div>
            </div>
            
          </div>
          
          <!-- 右侧标签选择 -->
          <div class="tags-sidebar">
            <div class="tags-sidebar-header">
              <h3>🏷️ 设置标签</h3>
              <p class="sidebar-subtitle">为题目选择合适的标签，方便后续分类管理</p>
            </div>
            
            <div class="tags-selection-content">
              <div v-for="tagType in tagTypes" :key="tagType.id" class="tag-type-section">
                <h5>{{ tagType.name }}</h5>
                <div class="tag-list">
                  <div 
                    v-for="tag in getTagsByType(tagType.id)" 
                    :key="tag.id" 
                    class="tag-item"
                    :class="{ selected: selectedTagsForUpload.includes(tag.id) }"
                    @click="toggleUploadTag(tag.id)"
                  >
                    {{ tag.name }}
                  </div>
                </div>
              </div>
              
              <div v-if="selectedTagsForUpload.length > 0" class="selected-tags-summary">
                <h5>已选择标签 ({{ selectedTagsForUpload.length }})</h5>
                <div class="selected-tags-list">
                  <span 
                    v-for="tagId in selectedTagsForUpload" 
                    :key="tagId"
                    class="tag-badge"
                    :style="{ backgroundColor: getTagColorById(tagId) }">
                    {{ getTagNameById(tagId) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 标签管理 -->
    <div v-if="activeTab === 'tags'" class="tab-content">
      <div class="tags-section">
        <TagManager @update="handleTagsUpdate" />
      </div>
    </div>
    
    <!-- 标签审核 -->
    <div v-if="activeTab === 'approval'" class="tab-content">
      <div class="approval-section">
        <div class="approval-header">
          <h3>标签审核管理</h3>
          <div class="filter-tabs">
            <div 
              class="filter-tab"
              :class="{ active: approvalFilter === 'pending' }"
              @click="approvalFilter = 'pending'; loadApprovalRequests()">
              待审核 ({{ pendingCount }})
            </div>
            <div 
              class="filter-tab"
              :class="{ active: approvalFilter === 'all' }"
              @click="approvalFilter = 'all'; loadApprovalRequests()">
              全部
            </div>
          </div>
        </div>
        
        <div v-if="approvalLoading" class="loading">
          加载中...
        </div>
        
        <div v-else-if="approvalRequests.length === 0" class="empty-state">
          暂无审核请求
        </div>
        
        <div v-else class="approval-list">
          <div 
            v-for="request in approvalRequests" 
            :key="request.id" 
            class="approval-item"
            :class="{ 'pending': request.status === 'pending' }">
            
            <div class="approval-header-info">
              <div class="request-info">
                <div class="problem-info-section">
                  <div class="problem-names">
                    <span class="problem-name-cn">{{ getProblemChineseName(request.problem_data_path) }}</span>
                    <span class="problem-name-en">{{ request.problem_data_path.split('/').pop() }}</span>
                  </div>
                </div>
                <div class="meta-info">
                <span class="status-badge" :class="request.status">
                  {{ getStatusText(request.status) }}
                </span>
                <span class="requestor">
                  申请人: {{ request.requestor?.real_name || request.requestor?.username || '未知' }}
                </span>
                <span class="request-time">
                  {{ formatTime(request.created_at) }}
                </span>
                </div>
              </div>
            </div>
            
            <div class="approval-content">
              <div class="request-tags">
                <strong>申请标签:</strong>
                <div class="tag-list">
                  <span 
                    v-for="tagId in request.tag_ids" 
                    :key="tagId"
                    class="tag-badge"
                    :style="{ backgroundColor: getTagColorById(tagId) }">
                    {{ getTagNameById(tagId) }}
                  </span>
                </div>
              </div>
              
              <div v-if="request.request_message" class="request-message">
                <strong>申请说明:</strong>
                <p>{{ request.request_message }}</p>
              </div>
              
              <div v-if="request.review_message" class="review-message">
                <strong>审核意见:</strong>
                <p>{{ request.review_message }}</p>
                <span class="reviewer">
                  审核人: {{ request.reviewer?.real_name || request.reviewer?.username || '未知' }}
                  ({{ formatTime(request.reviewed_at) }})
                </span>
              </div>
              
              <div v-if="request.status === 'pending'" class="approval-actions">
                <button @click="openReviewDialog(request)" class="btn btn-primary">
                  审核
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 题目预览弹窗 -->
    <div v-if="showProblemPreview" class="modal-overlay" @click="showProblemPreview = false">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h3>📋 题目预览</h3>
          <button @click="showProblemPreview = false" class="close-btn">✕</button>
        </div>
        <div class="modal-content">
          <div class="preview-container">
            <div class="preview-info">
              <h4>{{ problemForm.chineseName || '题目中文名称' }}</h4>
              <p class="problem-name">英文名称: {{ problemForm.name || '题目英文名称' }}</p>
            </div>
            <div class="preview-content" v-html="formattedDescription"></div>
            <div class="testcases-preview">
              <h5>📝 测试用例</h5>
              <div v-for="(testcase, index) in problemForm.testcases" :key="index" class="testcase-preview">
                <div class="testcase-preview-header">测试用例 {{ index + 1 }}</div>
                <div class="io-preview">
                  <div class="input-preview">
                    <strong>输入:</strong>
                    <pre>{{ testcase.input || '（无输入数据）' }}</pre>
                  </div>
                  <div class="output-preview">
                    <strong>输出:</strong>
                    <pre>{{ testcase.output || '（无输出数据）' }}</pre>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="problemForm.referenceAnswer" class="reference-preview">
              <h5>💻 参考代码</h5>
              <div class="code-preview-container">
                <pre class="code-preview">{{ problemForm.referenceAnswer }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 审核对话框：使用ProblemTagDialog -->
    <div v-if="showReviewDialog" class="modal-overlay" @click="closeReviewDialog">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h3>审核标签申请</h3>
          <button @click="closeReviewDialog" class="close-btn">✕</button>
        </div>
        <div class="modal-content">
          <ProblemTagDialog 
            v-if="selectedProblemForReview"
            :problemInfo="selectedProblemForReview"
            :reviewMode="true"
            :reviewRequest="currentRequest"
            @cancel="closeReviewDialog"
            @reviewed="handleReviewCompleted"
          />
        </div>
      </div>
    </div>
    
    <!-- 打标签对话框 -->
    <div v-if="showTagDialog" class="modal-overlay" @click="closeTagDialog">
      <ProblemTagDialog 
        :problemInfo="selectedProblem"
        @cancel="closeTagDialog"
        @saved="handleTagsSaved"
        @click.stop
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getProblemCategories, getProblemsByCategory, updateProblem as updateProblemAPI, deleteProblem as deleteProblemAPI } from '../../api/problems';
import { useRoute } from 'vue-router';
import { logUserOperation, OperationType } from '../../utils/logger';
import TagManager from '../../components/TagManager.vue';
import ProblemTagDialog from '../../components/ProblemTagDialog.vue';
import { getTagTypes, getTags, getProblemTags, setProblemTags, getBatchProblemTags, getApprovalRequests, approveTagRequest } from '../../api/tags';
import enhancedProblemsAPI from '../../api/enhancedProblems';
import { createCustomProblem } from '../../api/problems';
import { smartFormatProblem } from '../../utils/problemFormatter';

// 获取路由参数
const route = useRoute();

// 状态变量
const activeTab = ref('problems');
const categories = ref([]);
const selectedCategory = ref('');
const problems = ref([]);
const loading = ref(false);
const error = ref(null);
// 自定义题目相关状态
const isSubmitting = ref(false);

// 题目描述模板
const DESCRIPTION_TEMPLATE = `题目描述：
计算两个整数的最大公约数

输入：
两个正整数 a 和 b，用空格分隔

输出：
输出它们的最大公约数

输入示例：
16 24

输出示例：
8

数据范围：
1 ≤ a, b ≤ 10^9

注意：
请使用辗转相除法实现`;

// 表单数据
const problemForm = ref({
  name: '',
  chineseName: '',
  description: '',
  testcases: [
    { input: '', output: '' }
  ],
  referenceAnswer: ''
});

// 验证错误
const errors = ref({});

// 安全限制
const LIMITS = {
  description: 10000,
  testcase_input: 2000,
  testcase_output: 2000,
  max_testcases: 20,
  name_max_length: 50,
  chinese_name_max_length: 100,
  reference_answer: 50000
};

// 题目描述预览相关状态
const showDescriptionPreview = ref(false);
const showFormatHelp = ref(false);
const showProblemPreview = ref(false);
const showReferencePreview = ref(false);

// 打标签相关状态
const showTagDialog = ref(false);
const selectedProblem = ref(null);
const selectedTagsForProblem = ref([]);

// 上传题库标签选择状态
const selectedTagsForUpload = ref([]);

// 标签相关状态
const tagTypes = ref([]);
const allTags = ref([]); // 存储所有标签
const selectedTagIds = ref({}); // 存储每种标签类型的选中值
const problemTags = ref({}); // 存储每个问题的标签
const tagTypeMap = ref({}); // 存储标签类型ID到名称的映射

// 审核相关状态
const approvalRequests = ref([]);
const approvalLoading = ref(false);
const approvalFilter = ref('pending');
const pendingCount = ref(0);
const showReviewDialog = ref(false);
const currentRequest = ref(null);
const selectedProblemForReview = ref(null);

// 选择标签
const selectTag = (tagTypeId, tagId) => {
  selectedTagIds.value[tagTypeId] = tagId;
  loadProblems();
};

// 加载所有数据（优化版本）
const loadAllData = async (options = {}) => {
  loading.value = true;
  error.value = null;
  
  try {
    console.log('开始加载所有数据（优化版本）');
    
    // 构建过滤选项
    const filterOptions = {};
    
    // 收集所有选中的标签ID
    const selectedTags = [];
    for (const tagTypeId in selectedTagIds.value) {
      if (selectedTagIds.value[tagTypeId]) {
        selectedTags.push(selectedTagIds.value[tagTypeId]);
      }
    }
    
    // 如果有选中标签，传递给API进行交集筛选
    if (selectedTags.length > 0) {
      filterOptions.tagIds = selectedTags;
    }
    
    // 如果有强制刷新选项，传递给API
    if (options.forceRefresh) {
      filterOptions.forceRefresh = true;
    }
    
    // 一次性获取所有数据
    const allData = await enhancedProblemsAPI.getAllData(filterOptions);
    
    // 更新状态
    categories.value = allData.categories;
    problems.value = allData.problems;
    tagTypes.value = allData.tagTypes;
    allTags.value = allData.tags;
    problemTags.value = allData.problemTags;
    
    // 初始化selectedTagIds对象和tagTypeMap
    tagTypes.value.forEach(tagType => {
      if (!(tagType.id in selectedTagIds.value)) {
        selectedTagIds.value[tagType.id] = '';
      }
      tagTypeMap.value[tagType.id] = tagType.name;
    });
    
    console.log('所有数据加载完成:', {
      categories: categories.value.length,
      problems: problems.value.length,
      tagTypes: tagTypes.value.length,
      tags: allTags.value.length,
      problemTags: Object.keys(problemTags.value).length
    });
    
  } catch (err) {
    console.error('加载所有数据失败:', err);
    error.value = '加载数据失败';
    ElMessage.error('加载数据失败');
  } finally {
    loading.value = false;
  }
};

// 兼容的加载分类函数（已被loadAllData替代，但保留用于向后兼容）
const loadCategories = async () => {
  try {
    categories.value = await enhancedProblemsAPI.getCategories();
    if (categories.value.length === 0) {
      ElMessage.warning('未找到题库分类，请确保题库目录已正确配置');
    }
  } catch (err) {
    console.error('加载题库分类失败:', err);
    ElMessage.error('加载题库分类失败');
  }
};

// 兼容的加载标签函数（已被loadAllData替代，但保留用于向后兼容）
const loadTags = async () => {
  try {
    const tagsData = await enhancedProblemsAPI.getTagsData();
    tagTypes.value = tagsData.tagTypes;
    allTags.value = tagsData.tags;
    
    // 初始化selectedTagIds对象和tagTypeMap
    tagTypes.value.forEach(tagType => {
      if (!(tagType.id in selectedTagIds.value)) {
      selectedTagIds.value[tagType.id] = '';
      }
      tagTypeMap.value[tagType.id] = tagType.name;
    });
  } catch (err) {
    console.error('加载标签失败:', err);
    ElMessage.error('加载标签失败');
  }
};

// 根据标签类型获取标签
const getTagsByType = (tagTypeId) => {
  return allTags.value.filter(tag => tag.tag_type_id === tagTypeId);
};

// 加载试题列表（优化版本）
const loadProblems = async () => {
  // 直接调用loadAllData，因为它已经包含了过滤逻辑
  await loadAllData();
};
    
// 兼容的加载问题标签函数（已被loadAllData替代，但保留用于向后兼容）
const loadProblemTags = async () => {
  if (problems.value.length === 0) return;
  
  try {
    // 收集所有问题的data_path
    const allPaths = problems.value
      .filter(problem => problem.data_path)
      .map(problem => problem.data_path);
    
    if (allPaths.length === 0) return;
    
    // 使用增强API批量获取所有问题的标签
    console.log(`批量获取${allPaths.length}个问题的标签`);
    const encodedPaths = allPaths.map(path => encodeURIComponent(path));
    const batchTags = await enhancedProblemsAPI.getBatchProblemTags(encodedPaths);
    
    // 为所有问题设置标签数据，包括没有标签的题目
    for (const problem of problems.value) {
      if (problem.data_path) {
        const encodedPath = encodeURIComponent(problem.data_path);
        // 关键修复：即使没有标签也要设置为空数组，而不是跳过
        problemTags.value[problem.data_path] = batchTags[encodedPath] || [];
      }
    }
  } catch (err) {
    console.error(`批量获取问题标签失败:`, err);
  }
};

// 根据标签类型分组标签
const groupTagsByType = (tags) => {
  const grouped = {};
  
  if (!tags) return grouped;
  
  tags.forEach(tag => {
    const typeName = tag.tag_type_id ? (tagTypeMap.value[tag.tag_type_id] || '未分类') : '未分类';
    if (!grouped[typeName]) {
      grouped[typeName] = [];
    }
    grouped[typeName].push(tag);
  });
  
  return grouped;
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

// 打开标签对话框
const openTagDialog = (problem) => {
    if (!problem.data_path) {
      console.error('问题缺少data_path字段:', problem);
      ElMessage.error('无法获取问题标识符');
      return;
    }
  selectedProblem.value = problem;
  showTagDialog.value = true;
};

// 关闭标签对话框
const closeTagDialog = () => {
  showTagDialog.value = false;
  selectedProblem.value = null;
  selectedTagsForProblem.value = [];
};

// 处理标签保存成功
const handleTagsSaved = (selectedTagIds) => {
    logUserOperation(OperationType.UPDATE_PROBLEM_TAGS, `试题: ${selectedProblem.value.chinese_name}`);
    
    // 更新本地标签缓存
  if (selectedTagIds.length > 0) {
    const selectedTags = allTags.value.filter(tag => selectedTagIds.includes(tag.id));
      problemTags.value[selectedProblem.value.data_path] = selectedTags;
    } else {
      delete problemTags.value[selectedProblem.value.data_path];
    }
    
    closeTagDialog();
};

// 确认删除试题
const confirmDelete = (problem) => {
  ElMessageBox.confirm(`确定要删除试题 "${problem.chinese_name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteProblem(problem);
  }).catch(() => {
    // 取消删除
  });
};

// 删除试题
const deleteProblem = async (problem) => {
  try {
    await deleteProblemAPI(problem.data_path);
    ElMessage.success('删除试题成功');
    logUserOperation(OperationType.DELETE_PROBLEM, `试题: ${problem.chinese_name}`);
    loadProblems(); // 重新加载试题列表
  } catch (err) {
    console.error('删除试题失败:', err);
    ElMessage.error('删除试题失败');
  }
};

// 处理标签更新
const handleTagsUpdate = async () => {
  ElMessage.success('标签更新成功');
  // 使用增强API的缓存失效功能，然后重新加载所有数据
  enhancedProblemsAPI.invalidateAfterUpdate('tag');
  await loadAllData({ forceRefresh: true });
};

// ================= 自定义题目相关函数 =================

// 验证题目名称
const validateProblemName = (name) => {
  if (!name || name.trim() === '') {
    return '题目名称不能为空';
  }
  if (name.length > LIMITS.name_max_length) {
    return `题目名称不能超过${LIMITS.name_max_length}个字符`;
  }
  if (!/^[a-zA-Z0-9_]+$/.test(name)) {
    return '题目名称只能包含字母、数字和下划线';
  }
  return null;
};

// 验证中文名称
const validateChineseName = (name) => {
  if (!name || name.trim() === '') {
    return '题目中文名称不能为空';
  }
  if (name.length > LIMITS.chinese_name_max_length) {
    return `题目中文名称不能超过${LIMITS.chinese_name_max_length}个字符`;
  }
  return null;
};

// 验证题目描述
const validateDescription = (description) => {
  if (!description || description.trim() === '') {
    return '题目描述不能为空';
  }
  if (description.length > LIMITS.description) {
    return `题目描述不能超过${LIMITS.description}个字符`;
  }
  return null;
};

// 验证测试用例
const validateTestcaseData = (input, output) => {
  if (!input || input.trim() === '') {
    return '输入数据不能为空';
  }
  if (!output || output.trim() === '') {
    return '输出数据不能为空';
  }
  if (input.length > LIMITS.testcase_input) {
    return `输入数据不能超过${LIMITS.testcase_input}个字符`;
  }
  if (output.length > LIMITS.testcase_output) {
    return `输出数据不能超过${LIMITS.testcase_output}个字符`;
  }
  return null;
};

// 验证单个字段
const validateField = (fieldName) => {
  switch (fieldName) {
    case 'name':
      errors.value.name = validateProblemName(problemForm.value.name);
      break;
    case 'chineseName':
      errors.value.chineseName = validateChineseName(problemForm.value.chineseName);
      break;
    case 'description':
      errors.value.description = validateDescription(problemForm.value.description);
      break;
  }
};

// 验证测试用例
const validateTestcase = (index) => {
  const testcase = problemForm.value.testcases[index];
  if (testcase) {
    errors.value[`testcase_${index}`] = validateTestcaseData(testcase.input, testcase.output);
  }
};

// 验证整个表单
const validateForm = () => {
  errors.value = {};
  
  // 验证基本字段
  validateField('name');
  validateField('chineseName'); 
  validateField('description');
  
  // 验证测试用例
  problemForm.value.testcases.forEach((testcase, index) => {
    validateTestcase(index);
  });
  
  // 检查是否有测试用例
  if (problemForm.value.testcases.length === 0) {
    errors.value.testcases = '至少需要一个测试用例';
  }
  
  return Object.keys(errors.value).every(key => !errors.value[key]);
};

// 计算表单是否有效
const isFormValid = computed(() => {
  return problemForm.value.name && 
         problemForm.value.chineseName && 
         problemForm.value.description && 
         problemForm.value.testcases.length > 0 &&
         problemForm.value.testcases.every(tc => tc.input && tc.output) &&
         Object.keys(errors.value).every(key => !errors.value[key]);
});

// 格式化后的题目描述预览
const formattedDescription = computed(() => {
  if (!problemForm.value.description) {
    return '<p class="no-content">请输入题目描述...</p>';
  }
  
  try {
    return smartFormatProblem({
      name: problemForm.value.name || '题目',
      chineseName: problemForm.value.chineseName || '题目',
      description: problemForm.value.description
    });
  } catch (error) {
    console.error('格式化题目描述失败:', error);
    return '<p class="error">格式化失败，请检查输入内容</p>';
  }
});

// 添加测试用例
const addTestcase = () => {
  if (problemForm.value.testcases.length < LIMITS.max_testcases) {
    problemForm.value.testcases.push({ input: '', output: '' });
  }
};

// 删除测试用例
const removeTestcase = (index) => {
  if (problemForm.value.testcases.length > 1) {
    problemForm.value.testcases.splice(index, 1);
    // 清除对应的错误信息
    delete errors.value[`testcase_${index}`];
  }
};

// 重置表单
const resetForm = () => {
  problemForm.value = {
    name: '',
    chineseName: '',
    description: '',
    testcases: [{ input: '', output: '' }],
    referenceAnswer: ''
  };
  errors.value = {};
  selectedTagsForUpload.value = []; // 重置标签选择
  ElMessage.success('表单已重置');
};

// 切换上传题库标签选择
const toggleUploadTag = (tagId) => {
  const index = selectedTagsForUpload.value.indexOf(tagId);
  if (index === -1) {
    selectedTagsForUpload.value.push(tagId);
  } else {
    selectedTagsForUpload.value.splice(index, 1);
  }
};

// 使用描述模板
const useDescriptionTemplate = () => {
  problemForm.value.description = DESCRIPTION_TEMPLATE;
  validateField('description');
  ElMessage.success('已填充描述模板');
};

// 预览题目
const previewProblem = () => {
  if (!validateForm()) {
    ElMessage.warning('请完善表单信息');
    return;
  }
  
  // 显示预览弹窗
  showProblemPreview.value = true;
};

// 提交自定义题目
const submitCustomProblem = async () => {
  if (!validateForm()) {
    ElMessage.error('请检查表单中的错误');
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    ElMessage.info('正在创建题目...');
    
    // 构造API调用数据
    const problemData = {
      name: problemForm.value.name,
      chineseName: problemForm.value.chineseName,
      description: problemForm.value.description,
      testcases: problemForm.value.testcases,
      tag_ids: selectedTagsForUpload.value, // 添加标签ID列表
      reference_answer: problemForm.value.referenceAnswer || null // 添加参考答案
    };
    
    // 调用真正的API
    const result = await createCustomProblem(problemData);
    
    if (result.success) {
      // 显示成功弹窗，指导用户去题库维护查看
      ElMessageBox.alert(
        '题目创建成功！您可以在"题库维护"标签页中查看和管理已创建的题目与标签。',
        '创建成功',
        {
          confirmButtonText: '前往题库维护',
          type: 'success'
        }
      ).then(() => {
        // 用户点击确认后，切换到题库维护标签页
        activeTab.value = 'problems';
        // 强制刷新题库数据
        loadAllData({ forceRefresh: true });
      }).catch(() => {
        // 用户取消也要刷新数据
        loadAllData({ forceRefresh: true });
      });
      
      logUserOperation(OperationType.CREATE_CUSTOM_PROBLEM, 
        `题目: ${problemForm.value.chineseName}`);
      
      // 重置表单
      resetForm();
      
    } else {
      ElMessage.error(result.message || '创建题目失败');
    }
    
  } catch (error) {
    console.error('创建题目失败:', error);
    ElMessage.error(error.message || '创建题目失败，请重试');
  } finally {
    isSubmitting.value = false;
  }
};

// 审核相关方法
const loadApprovalRequests = async () => {
  approvalLoading.value = true;
  try {
    const status = approvalFilter.value === 'pending' ? 'pending' : null;
    const requests = await getApprovalRequests(status);
    
    // 用户信息已在后端处理，无需额外处理
    
    approvalRequests.value = requests;
    pendingCount.value = requests.filter(r => r.status === 'pending').length;
  } catch (error) {
    console.error('加载审核请求失败:', error);
    ElMessage.error('加载审核请求失败');
  } finally {
    approvalLoading.value = false;
  }
};

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待审核',
    'approved': '已批准',
    'rejected': '已拒绝'
  };
  return statusMap[status] || '未知';
};

const formatTime = (timeStr) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  return date.toLocaleString('zh-CN');
};

const getTagNameById = (tagId) => {
  const tag = allTags.value.find(t => t.id === tagId);
  return tag ? tag.name : '未知标签';
};

const getTagColorById = (tagId) => {
  const tag = allTags.value.find(t => t.id === tagId);
  return tag ? getTagColor(tag.tag_type_id) : '#909399';
};

const openReviewDialog = (request) => {
  currentRequest.value = request;
  // 构造题目信息对象，供ProblemTagDialog使用
  selectedProblemForReview.value = {
    name: request.problem_data_path.split('/').pop(),
    chinese_name: getProblemChineseName(request.problem_data_path),
    data_path: request.problem_data_path,
    // 添加其他可能需要的字段
    time_limit: '1000ms',
    memory_limit: '256M'
  };
  showReviewDialog.value = true;
};

const closeReviewDialog = () => {
  showReviewDialog.value = false;
  currentRequest.value = null;
  selectedProblemForReview.value = null;
};

const handleReviewCompleted = async (reviewResult) => {
  try {
    await approveTagRequest(currentRequest.value.id, {
      status: reviewResult.status,
      review_message: reviewResult.review_message || null
    });
    
    ElMessage.success(`标签申请已${reviewResult.status === 'approved' ? '批准' : '拒绝'}`);
    closeReviewDialog();
    await loadApprovalRequests();
    
    // 如果批准，重新加载题目列表
    if (reviewResult.status === 'approved') {
      await loadProblems();
    }
  } catch (error) {
    console.error('审核失败:', error);
    ElMessage.error('审核失败');
  }
};

// 获取题目中文名称
const getProblemChineseName = (problemPath) => {
  // 从problems列表中查找对应的题目信息
  const problem = problems.value.find(p => p.data_path === problemPath);
  return problem?.chinese_name || '未知题目';
};

// 监听路由参数变化
watch(() => route.query.tab, (newTab) => {
  if (newTab === 'upload') {
    activeTab.value = 'upload';
  } else if (newTab === 'tags') {
    activeTab.value = 'tags';
  } else if (newTab === 'approval') {
    activeTab.value = 'approval';
    loadApprovalRequests();
  } else {
    activeTab.value = 'problems';
  }
}, { immediate: true });

// 监听activeTab变化，当切换到审核页面时加载数据
watch(activeTab, (newTab) => {
  if (newTab === 'approval') {
    loadApprovalRequests();
  }
});

// 页面加载时获取所有数据（优化版本）
onMounted(async () => {
  // 预加载基础数据到缓存
  await enhancedProblemsAPI.preloadData({ preloadAllProblems: true });
  
  // 加载所有数据到页面
  await loadAllData();
  
  // 记录优化后的加载完成
  console.log('页面数据加载完成，使用了优化的API');
});
</script>

<style scoped>
.maintenance-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 60px;
  
  /* 设计系统变量 */
  --primary-color: #667eea;
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --secondary-color: #f093fb;
  --text-primary: #2d3748;
  --text-secondary: #4a5568;
  --border-color: #e2e8f0;
  --bg-light: #f7fafc;
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  /* 标签颜色 */
  --tag-color-0: #409eff; /* 蓝色 */
  --tag-color-1: #67c23a; /* 绿色 */
  --tag-color-2: #e6a23c; /* 橙色 */
  --tag-color-3: #f56c6c; /* 红色 */
  --tag-color-4: #909399; /* 灰色 */
  --tag-color-5: #9c27b0; /* 紫色 */
  --tag-color-6: #2196f3; /* 浅蓝 */
  --tag-color-7: #ff9800; /* 橙黄 */
  --tag-color-8: #795548; /* 棕色 */
  --tag-color-9: #607d8b; /* 蓝灰 */
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #dcdfe6;
  margin-bottom: 20px;
}

.tab {
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-right: 20px;
}

.tab.active {
  border-bottom-color: #409eff;
  color: #409eff;
}

.tab-content {
  padding: 10px 0;
}

/* 新增标签筛选布局样式 */
.tags-filter-container {
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  background-color: #f5f7fa;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.tag-type-row {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.tag-type-row:last-child {
  margin-bottom: 0;
}

.tag-type-label {
  width: 100px;
  text-align: right;
  padding-right: 15px;
  padding-top: 6px;
  font-weight: 500;
  color: #606266;
  flex-shrink: 0;
}

.tag-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex-grow: 1;
}

.tag-item {
  padding: 6px 12px;
  border-radius: 4px;
  background-color: #ffffff;
  border: 1px solid #dcdfe6;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  user-select: none;
}

.tag-item:hover {
  background-color: #ecf5ff;
  color: var(--primary-color);
  border-color: #c6e2ff;
}

.tag-item.active {
  color: #ffffff;
  background-color: var(--tag-color, var(--primary-color));
  border-color: var(--tag-color, var(--primary-color));
}

.loading, .error, .empty-state {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.error {
  color: #f56c6c;
}

.problems-table-container {
  overflow-x: auto;
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

.tags-cell {
  max-width: 500px; /* 增加标签单元格宽度 */
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

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-edit {
  background-color: #67c23a;
  color: white;
}

.btn-delete {
  background-color: #f56c6c;
  color: white;
}

.upload-section {
  width: 100%;
}



/* 打标签对话框样式 */
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
  z-index: 1000;
  padding: 0;
}

.modal {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.large-modal {
  width: 1200px;
  max-width: 95vw;
  max-height: 90vh;
  overflow: hidden;
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
}

.tag-dialog-content {
  overflow-y: auto;
  max-height: 60vh;
  padding-right: 10px;
}

.tag-type-section {
  margin-bottom: 20px;
}

.tag-type-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #606266;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-list .tag-item {
  padding: 6px 12px;
  background-color: #f4f4f5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.tag-list .tag-item:hover {
  background-color: #e9e9eb;
}

.tag-list .tag-item.selected {
  background-color: #409eff;
  color: white;
}

.dialog-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 审核相关样式 */
.approval-section {
  max-width: 100%;
}

.approval-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.approval-header h3 {
  margin: 0;
  color: #303133;
}

.filter-tabs {
  display: flex;
  gap: 10px;
}

.filter-tab {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  background-color: #fff;
  color: #606266;
  transition: all 0.3s;
}

.filter-tab:hover {
  border-color: #409eff;
  color: #409eff;
}

.filter-tab.active {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.approval-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.approval-item {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.approval-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #e6a23c, #f5b041);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.approval-item.pending::before {
  opacity: 1;
}

.approval-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.approval-item.pending {
  border-left: none;
  background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%);
}

.approval-header-info {
  margin-bottom: 12px;
}

.request-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.problem-info-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}

.problem-names {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.problem-name-cn {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
  line-height: 1.3;
}

.problem-name-en {
  font-size: 13px;
  color: #909399;
  font-family: 'Courier New', monospace;
}

.btn-view-problem {
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-view-problem:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.problem-name {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background-color: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.status-badge.approved {
  background-color: #f0f9ff;
  color: #67c23a;
  border: 1px solid #b3d8ff;
}

.status-badge.rejected {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
}

.requestor, .request-time {
  color: #909399;
  font-size: 14px;
}

.approval-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.request-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.request-tags strong {
  color: #606266;
  font-size: 14px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-badge {
  padding: 6px 12px;
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.tag-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.request-message, .review-message {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.request-message strong, .review-message strong {
  color: #606266;
  font-size: 14px;
}

.request-message p, .review-message p {
  margin: 0;
  color: #303133;
  line-height: 1.5;
  background-color: #f8f9fa;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.reviewer {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

.approval-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f2f5;
}

.approval-actions .btn {
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.approval-actions .btn-primary {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.approval-actions .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

/* 查看题目详情对话框样式 */
.modal-overlay .modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px 8px 0 0;
}

.modal-overlay .modal .modal-header h3 {
  margin: 0;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.modal-overlay .modal .close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: white;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.modal-overlay .modal .close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.modal-overlay .modal .modal-content {
  padding: 0;
  overflow: hidden;
}

/* ================= 现代化表单样式 ================= */

.upload-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem 0;
  background: linear-gradient(135deg, var(--primary-gradient));
  color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.page-subtitle {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.problem-form {
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: var(--transition);
}

.form-card {
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: var(--transition);
  margin-bottom: 1.5rem;
}

.form-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 1rem 1.5rem;
  border-bottom: 2px solid var(--primary-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
}

.card-title::before {
  content: '';
  width: 4px;
  height: 20px;
  background: var(--primary-gradient);
  margin-right: 10px;
  border-radius: 2px;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.card-body {
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.field-label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.875rem;
  margin: 0;
}

.field-label.required::after {
  content: ' *';
  color: #ef4444;
  font-weight: bold;
}

.required-mark {
  color: #ef4444;
  font-weight: bold;
}

.field-input, .field-textarea {
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  transition: var(--transition);
  background-color: #fafbfc;
  font-family: inherit;
  resize: vertical;
}

.field-input:focus, .field-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.field-input.error, .field-textarea.error {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.field-input.error:focus, .field-textarea.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.error-message {
  color: #ef4444;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.error-message::before {
  content: '⚠';
}

.field-hint {
  color: #6b7280;
  font-size: 0.75rem;
  font-style: italic;
}

.field-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  gap: 1rem;
}

.char-count {
  color: #6b7280;
  font-size: 0.75rem;
  white-space: nowrap;
}

.testcases-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.testcase-card {
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 2px solid #e2e8f0;
  border-radius: var(--radius-md);
  padding: 1rem;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.testcase-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--primary-gradient);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.testcase-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.testcase-card:hover::before {
  opacity: 1;
}

.testcase-card.error {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
}

.testcase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.testcase-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.case-number {
  background: var(--primary-gradient);
  color: white;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
}

.remove-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.remove-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.testcase-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.io-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  position: relative;
}

.io-label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.io-input {
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  transition: var(--transition);
  background-color: #fafbfc;
  resize: vertical;
  min-height: 4rem;
}

.io-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.char-counter {
  position: absolute;
  bottom: 0.5rem;
  right: 0.75rem;
  font-size: 0.625rem;
  color: #6b7280;
  background: rgba(255, 255, 255, 0.9);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  pointer-events: none;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  border: none;
  text-decoration: none;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1rem;
  line-height: 1;
}

.template-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.template-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.preview-btn, .help-btn {
  background: linear-gradient(135deg, #6b7280, #9ca3af);
  color: white;
  box-shadow: 0 2px 4px rgba(107, 114, 128, 0.2);
}

.preview-btn:hover:not(:disabled), .help-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(107, 114, 128, 0.3);
}

.primary-btn {
  background: var(--primary-gradient);
  color: white;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.secondary-btn {
  background: linear-gradient(135deg, #6b7280, #9ca3af);
  color: white;
  box-shadow: 0 2px 4px rgba(107, 114, 128, 0.2);
}

.secondary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(107, 114, 128, 0.3);
}

.info-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.info-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.add-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.add-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.action-card {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border: 2px solid var(--primary-color);
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

/* 格式帮助和预览样式 */
.format-help {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border: 2px solid #3b82f6;
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1rem;
}

.format-help h5 {
  color: #1e40af;
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.format-help p {
  margin: 0.5rem 0;
  color: #374151;
  font-size: 0.875rem;
}

.help-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
  margin: 0.75rem 0;
}

.help-item {
  background: rgba(255, 255, 255, 0.8);
  padding: 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: #374151;
}

.help-note {
  background: rgba(59, 130, 246, 0.1);
  padding: 0.75rem;
  border-radius: var(--radius-sm);
  margin: 0.75rem 0 0 0;
  color: #1e40af;
}

.preview-panel {
  margin-top: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: var(--radius-md);
  background: white;
  overflow: hidden;
}

.preview-header {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #d1d5db;
}

.preview-header h5 {
  margin: 0;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
}

.preview-content {
  padding: 1rem;
  min-height: 8rem;
  max-height: 20rem;
  overflow-y: auto;
  background: white;
}

/* 预览弹窗样式 */
.preview-container {
  max-height: 70vh;
  overflow-y: auto;
}

.preview-info {
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.preview-info h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 700;
}

.problem-name {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.testcases-preview {
  margin-top: 1.5rem;
  border-top: 2px solid #e2e8f0;
  padding-top: 1.5rem;
}

.testcases-preview h5 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
}

.testcase-preview {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-sm);
  padding: 1rem;
  margin-bottom: 1rem;
}

.testcase-preview-header {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.io-preview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.input-preview, .output-preview {
  background: white;
  border-radius: var(--radius-sm);
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
}

.input-preview strong, .output-preview strong {
  color: var(--text-primary);
  font-size: 0.875rem;
  display: block;
  margin-bottom: 0.5rem;
}

.input-preview pre, .output-preview pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.75rem;
  white-space: pre-wrap;
  word-break: break-word;
  color: #374151;
  background: #f9fafb;
  padding: 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid #e5e7eb;
}

/* 预览内容样式 - 模拟HTML显示效果 */
.preview-content .SimSun {
  font-size: 14px;
  font-family: 宋体, SimSun, serif;
}

/* 代码预览样式 */
.code-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
}

.code-preview {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 1rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.reference-preview {
  margin-top: 1.5rem;
  border-top: 2px solid #e2e8f0;
  padding-top: 1.5rem;
}

.reference-preview h5 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
}

.code-preview-container {
  background: #1e1e1e;
  border-radius: 0.375rem;
  overflow: hidden;
}

.preview-content .title {
  font-family: 宋体, SimSun, serif;
  font-size: 18px;
  font-weight: bold;
  color: Green;
  text-align: center;
  margin-bottom: 20px;
}

.preview-content .section-title {
  font-family: 宋体, SimSun, serif;
  font-size: 16px;
  font-weight: bold;
  color: Green;
  margin-left: 20px;
  margin-top: 15px;
  margin-bottom: 5px;
}

.preview-content .content {
  line-height: 22px;
  margin-left: 20px;
  margin-right: 20px;
}

.preview-content .note-text {
  color: #FF0000;
}

.preview-content .sample-data {
  font-family: monospace;
  background-color: #f5f5f5;
  padding: 5px;
  border: 1px solid #ddd;
  margin: 5px 0;
}

/* 上传题库布局样式 */
.upload-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.form-container {
  flex: 1;
  min-width: 0;
}

.tags-sidebar {
  width: 350px;
  flex-shrink: 0;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  position: sticky;
  top: 20px;
}

.tags-sidebar-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 1rem 1.5rem;
  border-bottom: 2px solid var(--primary-color);
}

.tags-sidebar-header h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.sidebar-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.4;
}

.tags-selection-content {
  padding: 1.5rem;
  max-height: 600px;
  overflow-y: auto;
}

.tags-selection-content .tag-type-section {
  margin-bottom: 1.5rem;
}

.tags-selection-content .tag-type-section h5 {
  margin: 0 0 0.75rem 0;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 600;
}

.tags-selection-content .tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tags-selection-content .tag-item {
  padding: 0.5rem 0.75rem;
  background-color: #f4f4f5;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
  font-size: 0.75rem;
  border: 1px solid #dcdfe6;
  user-select: none;
}

.tags-selection-content .tag-item:hover {
  background-color: #e9e9eb;
  transform: translateY(-1px);
}

.tags-selection-content .tag-item.selected {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.selected-tags-summary {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.selected-tags-summary h5 {
  margin: 0 0 0.75rem 0;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 600;
}

.selected-tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selected-tags-list .tag-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .maintenance-container {
    padding: 1rem;
  }
  
  .upload-container {
    padding: 0;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1rem;
  }
  
  .header-actions {
    align-self: stretch;
    justify-content: center;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .testcase-content {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-btn {
    justify-content: center;
  }
  
  .help-grid {
    grid-template-columns: 1fr;
  }
  
  .tag-type-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .tag-type-label {
    width: auto;
    text-align: left;
    padding: 0;
  }
  
  /* 移动端上传题库布局 */
  .upload-layout {
    flex-direction: column;
    gap: 1rem;
  }
  
  .tags-sidebar {
    width: 100%;
    position: static;
  }
  
  .tags-selection-content {
    max-height: none;
  }
}
</style> 