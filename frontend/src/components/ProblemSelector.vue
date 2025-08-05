<template>
  <div class="problem-selector-container">
    <div class="header-section">
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
      <div class="action-buttons">
        <button @click="selectAll" class="btn btn-secondary">全选</button>
        <button @click="deselectAll" class="btn btn-secondary">全清</button>
        <button @click="confirmSelection" class="btn btn-primary">确定</button>
        <button @click="cancel" class="btn btn-cancel">取消</button>
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
            <th style="width: 50px">选择</th>
            <th>序号</th>
            <th>试题名称</th>
            <th>试题中文名称</th>
            <th>标签</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(problem, index) in problems" :key="problem.name">
            <td>
              <input 
                type="checkbox" 
                :value="problem" 
                v-model="selectedProblems"
                @change="updateSelectedCount"
              />
            </td>
            <td>{{ index + 1 }}</td>
            <td>{{ problem.name }}</td>
            <td>{{ problem.chinese_name }}</td>
            <td>
              <div v-if="problem.tags && problem.tags.length > 0" class="problem-tags">
                <template v-for="(tags, tagType) in groupTagsByType(problem.tags)" :key="tagType">
                  <div class="tag-group">
                    <span class="tag-type">{{ tagType }}:</span>
                    <span 
                      v-for="tag in tags" 
                      :key="tag.id" 
                      class="tag-badge"
                      :style="{ backgroundColor: tag.tag_type_id ? `var(--tag-color-${tag.tag_type_id % 10})` : '#409eff' }"
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

    <div class="selection-info">
      已选择 {{ selectedProblems.length }} 道题目
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getProblemCategories, getProblemsByCategory } from '../api/problems';
import { getTagTypes, getTags, getProblemTags, getBatchProblemTags } from '../api/tags';
import enhancedProblemsAPI from '../api/enhancedProblems';

// 组件接收的属性
const props = defineProps({
  exerciseId: {
    type: [String, Number],
    required: true
  }
});

// 组件触发的事件
const emit = defineEmits(['confirm', 'cancel']);

// 状态变量
const categories = ref([]);
const selectedCategory = ref('');
const problems = ref([]);
const selectedProblems = ref([]);
const loading = ref(false);
const error = ref(null);

// 标签相关状态
const tagTypes = ref([]);
const allTags = ref([]); // 存储所有标签
const selectedTagIds = ref({}); // 存储每种标签类型的选中值
const problemTags = ref({}); // 存储每个问题的标签
const tagTypeMap = ref({}); // 存储标签类型ID到名称的映射

// 选择标签
const selectTag = (tagTypeId, tagId) => {
  selectedTagIds.value[tagTypeId] = tagId;
  loadProblems();
};

// 加载所有数据（简化安全版本）
const loadAllData = async (options = {}) => {
  loading.value = true;
  error.value = null;
  
  try {
    console.log('ProblemSelector: 开始加载所有数据（简化版本）');
    
    // 并行加载基础数据
    const [categoriesData, tagsData] = await Promise.all([
      getProblemCategories(),
      Promise.all([getTagTypes(), getTags()])
    ]);
    
    // 更新基础数据
    categories.value = categoriesData;
    tagTypes.value = tagsData[0];
    allTags.value = tagsData[1];
    
    // 初始化selectedTagIds对象和tagTypeMap
    tagTypes.value.forEach(tagType => {
      if (!(tagType.id in selectedTagIds.value)) {
        selectedTagIds.value[tagType.id] = '';
      }
      tagTypeMap.value[tagType.id] = tagType.name;
    });
    
    // 加载所有题目
    await loadProblemsFromAllCategories();
    
    console.log('ProblemSelector: 所有数据加载完成:', {
      categories: categories.value.length,
      problems: problems.value.length,
      tagTypes: tagTypes.value.length,
      tags: allTags.value.length
    });
    
  } catch (err) {
    console.error('ProblemSelector: 加载所有数据失败:', err);
    error.value = '加载数据失败';
    ElMessage.error('加载数据失败');
  } finally {
    loading.value = false;
  }
};

// 从所有分类加载题目
const loadProblemsFromAllCategories = async () => {
  const allProblems = [];
  
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
  
  // 遍历所有分类获取题目
  for (const category of categories.value) {
    try {
      const categoryProblems = await getProblemsByCategory(category.path, filterOptions);
      allProblems.push(...categoryProblems);
    } catch (err) {
      console.warn(`获取分类 ${category.path} 的题目失败:`, err);
    }
  }
  
  // 去重
  const uniqueProblems = {};
  for (const problem of allProblems) {
    if (problem.data_path && !uniqueProblems[problem.data_path]) {
      uniqueProblems[problem.data_path] = problem;
    }
  }
  
  problems.value = Object.values(uniqueProblems);
  
  // 加载题目标签
  await loadProblemTags();
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

// 根据标签类型分组标签
const groupTagsByType = (tags) => {
  const grouped = {};
  
  if (!tags) return grouped;
  
  tags.forEach(tag => {
    const typeName = tagTypeMap.value[tag.tag_type_id] || '未分类';
    if (!grouped[typeName]) {
      grouped[typeName] = [];
    }
    grouped[typeName].push(tag);
  });
  
  return grouped;
};

// 加载问题标签（简化安全版本）
const loadProblemTags = async () => {
  if (problems.value.length === 0) return;
  
  try {
    // 收集所有问题的data_path
    const problemPaths = problems.value
      .filter(problem => problem.data_path)
      .map(problem => problem.data_path);
    
    if (problemPaths.length === 0) return;
    
    // 使用原有API批量获取所有问题的标签
    const batchTags = await getBatchProblemTags(problemPaths);
  
    // 将结果存储到每个问题对象上
    for (const problem of problems.value) {
      if (problem.data_path && batchTags[problem.data_path]) {
        problem.tags = batchTags[problem.data_path];
      }
    }
  } catch (err) {
    console.error('批量获取问题标签失败:', err);
  }
};

// 加载试题列表（简化版本）
const loadProblems = async () => {
  await loadProblemsFromAllCategories();
};

// 全选
const selectAll = () => {
  selectedProblems.value = [...problems.value];
};

// 全清
const deselectAll = () => {
  selectedProblems.value = [];
};

// 更新选择计数
const updateSelectedCount = () => {
  console.log(`已选择 ${selectedProblems.value.length} 道题目`);
};

// 确认选择
const confirmSelection = () => {
  if (selectedProblems.value.length === 0) {
    ElMessage.warning('请至少选择一道题目');
    return;
  }
  
  // 为选中的题目添加分数设置，但保留原始的时间限制和内存限制
  const problems = selectedProblems.value.map(problem => {
    return {
      ...problem,
      code_check_score: problem.code_check_score || 20,
      runtime_score: problem.runtime_score || 80,
      score_method: 'sum'
    };
  });
  
  // 触发确认事件，将选择的题目传递给父组件
  emit('confirm', {
    exerciseId: props.exerciseId,
    problems: problems
  });
};

// 取消选择
const cancel = () => {
  emit('cancel');
};

// 页面加载时获取所有数据（简化安全版本）
onMounted(async () => {
  console.log('ProblemSelector: 开始加载数据');
  
  // 加载所有数据到页面
  await loadAllData();
  
  console.log('ProblemSelector: 页面数据加载完成');
});
</script>

<style scoped>
.problem-selector-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
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

.header-section {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

/* 新增标签筛选布局样式 */
.tags-filter-container {
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
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
  color: #409eff;
  border-color: #c6e2ff;
}

.tag-item.active {
  color: #ffffff;
  background-color: var(--tag-color, #409eff);
  border-color: var(--tag-color, #409eff);
}

/* 修改操作按钮排版 */
.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 10px;
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
  margin-bottom: 20px;
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

.selection-info {
  text-align: right;
  margin-top: 10px;
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

.btn-cancel {
  background-color: #f0f0f0;
  color: #606266;
}

.btn-cancel:hover {
  background-color: #e0e0e0;
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
  font-size: 0.8em;
  color: #606266;
}

.tag-badge {
  padding: 2px 6px;
  border-radius: 4px;
  background-color: #409eff;
  color: white;
  font-size: 0.8em;
  white-space: nowrap;
}

.no-tags {
  color: #909399;
  font-size: 0.9em;
  font-style: italic;
}
</style> 