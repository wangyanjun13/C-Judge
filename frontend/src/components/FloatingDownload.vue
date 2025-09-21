<template>
  <div class="floating-download" v-if="showButton">
    <div 
      class="floating-button" 
      :class="{ 'expanded': isExpanded }"
      @click="toggleExpanded"
    >
      <div class="button-icon">
        <span v-if="!isExpanded">💻</span>
        <span v-else>✕</span>
      </div>
    </div>
    
    <div 
      class="floating-panel" 
      :class="{ 'show': isExpanded }"
      @click.stop
    >
      <div class="panel-header">
        <h3>工具下载</h3>
      </div>
      
      <div class="download-options">
        <button class="download-btn" @click="downloadDevCpp">
          <span class="download-icon">📥</span>
          下载 Dev-C++
        </button>
        
        <button class="download-btn practice-btn" @click="openPracticeSystem">
          <span class="download-icon">🏫</span>
          校内练习系统
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const isExpanded = ref(false);

// 只在练习页面显示
const showButton = computed(() => {
  const path = route.path;
  return path.includes('/exercises') || path.includes('/exercise/');
});

// 监听路由变化，离开练习页面时关闭面板
watch(showButton, (newValue) => {
  if (!newValue) {
    isExpanded.value = false;
  }
});

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
};

const downloadDevCpp = () => {
  const link = document.createElement('a');
  link.href = '/devcpp-4.9.9.2_setup.exe';
  link.download = 'devcpp-4.9.9.2_setup.exe';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // 下载后关闭面板
  isExpanded.value = false;
};

const openPracticeSystem = () => {
  window.open('http://222.28.84.2/train/login.aspx', '_blank');
  
  // 点击后关闭面板
  isExpanded.value = false;
};

// 点击外部关闭面板
const handleClickOutside = (event) => {
  if (isExpanded.value && !event.target.closest('.floating-download')) {
    isExpanded.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.floating-download {
  position: fixed;
  bottom: 80px;
  right: 30px;
  z-index: 1000;
  font-family: var(--font-family);
}

.floating-button {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.floating-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.floating-button:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
}

.floating-button:hover::before {
  opacity: 1;
}

.floating-button.expanded {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
}

.floating-button.expanded:hover {
  box-shadow: 0 12px 35px rgba(255, 107, 107, 0.6);
}

.button-icon {
  font-size: 16px;
  color: white;
  transition: transform 0.3s ease;
  z-index: 1;
}

.floating-button.expanded .button-icon {
  transform: rotate(45deg);
}

.floating-panel {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 200px;
  background: var(--bg-card);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(20px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  opacity: 0;
  transform: translateY(20px) scale(0.95);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
  overflow: hidden;
}

.floating-panel.show {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: all;
}

.panel-header {
  padding: 15px 15px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-white);
}

.download-options {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.download-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.download-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.download-icon {
  font-size: 16px;
}

.practice-btn {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%) !important;
}

.practice-btn:hover {
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.4) !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .floating-download {
    bottom: 70px;
    right: 20px;
  }
  
  .floating-panel {
    width: 180px;
    right: -10px;
  }
  
  .floating-button {
    width: 35px;
    height: 35px;
  }
  
  .button-icon {
    font-size: 14px;
  }
}

/* 动画效果 */
@keyframes pulse {
  0% {
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }
  50% {
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5), 0 0 0 8px rgba(102, 126, 234, 0.1);
  }
  100% {
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }
}

.floating-button:not(.expanded) {
  animation: pulse 2s infinite;
}
</style>
