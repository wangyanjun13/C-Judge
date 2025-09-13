<template>
  <div>
    <!-- 使用教程按钮 -->
    <button class="tutorial-btn glass-effect" @click="showTutorialDialog">
      <span class="tutorial-icon">🎥</span>
      <span>使用教程</span>
    </button>

    <!-- 视频教程弹窗 -->
    <el-dialog
      v-model="tutorialVisible"
      title="使用教程"
      width="80%"
      :before-close="handleClose"
      class="tutorial-dialog"
    >
      <div class="tutorial-content">
        <!-- 视频列表 -->
        <div class="video-list" v-if="videos.length > 0">
          <div
            v-for="(video, index) in videos"
            :key="index"
            class="video-item"
            :class="{ active: currentVideoIndex === index }"
            @click="playVideo(index)"
          >
            <div class="video-thumbnail">
              <span class="play-icon">▶️</span>
            </div>
            <div class="video-info">
              <h4 class="video-title">{{ video.title }}</h4>
              <p class="video-description">{{ video.description }}</p>
            </div>
          </div>
        </div>

        <!-- 视频播放器 -->
        <div class="video-player" v-if="currentVideo">
          <video
            ref="videoPlayer"
            :src="currentVideoUrl"
            controls
            preload="metadata"
            class="tutorial-video"
            @loadstart="onVideoLoadStart"
            @error="onVideoError"
          >
            您的浏览器不支持视频播放。
          </video>
          <div class="video-info-panel">
            <h3 class="current-video-title">{{ currentVideo.title }}</h3>
            <p class="current-video-description">{{ currentVideo.description }}</p>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载视频列表中...</span>
        </div>

        <!-- 错误状态 -->
        <div v-if="error" class="error-container">
          <el-icon><Warning /></el-icon>
          <span>{{ error }}</span>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="tutorialVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Warning } from '@element-plus/icons-vue'
import { getVideoList } from '../api/problems'

// 响应式数据
const tutorialVisible = ref(false)
const videos = ref([])
const currentVideoIndex = ref(0)
const loading = ref(false)
const error = ref('')
const videoPlayer = ref(null)

// 计算属性
const currentVideo = computed(() => {
  return videos.value[currentVideoIndex.value] || null
})

const currentVideoUrl = computed(() => {
  if (!currentVideo.value) return ''
  // 使用完整的API路径
  return `/api/problems/videos/${currentVideo.value.filename}`
})


// 方法
const showTutorialDialog = async () => {
  tutorialVisible.value = true
  if (videos.value.length === 0) {
    await loadVideoList()
  }
}

const loadVideoList = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await getVideoList()
    videos.value = response.videos || []
    
    if (videos.value.length === 0) {
      error.value = '暂无可用教程视频'
    }
  } catch (err) {
    console.error('加载视频列表失败:', err)
    error.value = '加载视频列表失败，请稍后重试'
    ElMessage.error('加载视频列表失败')
  } finally {
    loading.value = false
  }
}

const playVideo = (index) => {
  currentVideoIndex.value = index
  // 重置视频播放器
  if (videoPlayer.value) {
    videoPlayer.value.currentTime = 0
  }
}


const onVideoLoadStart = () => {
  console.log('视频开始加载')
}

const onVideoError = (event) => {
  console.error('视频加载失败:', event)
  ElMessage.error('视频加载失败，请检查网络连接')
}

const handleClose = () => {
  tutorialVisible.value = false
  // 停止当前视频播放
  if (videoPlayer.value) {
    videoPlayer.value.pause()
  }
}

// 监听弹窗关闭，重置状态
watch(tutorialVisible, (newVal) => {
  if (!newVal) {
    currentVideoIndex.value = 0
    error.value = ''
  }
})
</script>

<style scoped>
.tutorial-btn {
  padding: 8px 16px;
  background: var(--bg-card);
  color: var(--text-white);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: var(--transition);
}

.tutorial-btn:hover {
  background: var(--bg-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.tutorial-icon {
  font-size: 16px;
}

.tutorial-dialog {
  --el-dialog-border-radius: 12px;
}

.tutorial-content {
  min-height: 400px;
}

.video-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.video-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition);
}

.video-item:hover {
  background: var(--bg-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.video-item.active {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), var(--bg-secondary));
}

.video-thumbnail {
  width: 60px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.play-icon {
  font-size: 20px;
  color: white;
}

.video-info {
  flex: 1;
  min-width: 0;
}

.video-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
}

.video-description {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-player {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 20px;
  margin-bottom: 20px;
}

.tutorial-video {
  width: 100%;
  max-height: 400px;
  border-radius: var(--radius-sm);
  background: #000;
}

.video-info-panel {
  margin-top: 16px;
}

.current-video-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.current-video-description {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.loading-container,
.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 14px;
}

.error-container {
  color: var(--error-color);
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .video-list {
    grid-template-columns: 1fr;
  }
  
  .video-item {
    flex-direction: column;
    text-align: center;
  }
  
  .video-thumbnail {
    width: 80px;
    height: 60px;
  }
  
  .tutorial-video {
    max-height: 250px;
  }
}
</style>
