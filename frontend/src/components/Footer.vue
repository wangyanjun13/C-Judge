<template>
  <footer class="app-footer" :class="{ 'sticky': isHomePage }">
    <div class="footer-content">
      <p>© {{ currentYear }} Just For Fun - 编程系统</p>
      <p class="license">
        <span class="license-link" @click="showLicense">MIT License - MIT 许可证</span>
      </p>
    </div>
    
    <!-- LICENSE 底部滑出式弹窗 -->
    <div v-if="licenseVisible" class="bottom-slide-overlay" @click="licenseVisible = false">
      <div class="bottom-slide-panel" @click.stop>
        <div class="bottom-slide-header">
          <h3>MIT License</h3>
          <button class="close-btn" @click="licenseVisible = false">&times;</button>
        </div>
        <div class="bottom-slide-content">
          <div class="license-content">
            <p>Copyright (c) {{ currentYear }} wangyanjun13</p>
            <p>
              Permission is hereby granted, free of charge, to any person obtaining a copy
              of this software and associated documentation files (the "Software"), to deal
              in the Software without restriction, including without limitation the rights
              to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
              copies of the Software, and to permit persons to whom the Software is
              furnished to do so, subject to the following conditions:
            </p>
            <p>
              The above copyright notice and this permission notice shall be included in all
              copies or substantial portions of the Software.
            </p>
            <p>
              THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
              IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
              FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
              AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
              LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
              OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
              SOFTWARE.
            </p>
          </div>
        </div>
        <div class="bottom-slide-footer">
          <button class="btn-primary" @click="licenseVisible = false">关闭</button>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';

// 计算当前年份，用于版权信息
const currentYear = computed(() => new Date().getFullYear());

// LICENSE 弹窗控制
const licenseVisible = ref(false);
const showLicense = () => {
  licenseVisible.value = true;
};

// 获取当前路由
const route = useRoute();

// 判断是否为首页
const isHomePage = computed(() => {
  return route.path === '/' || route.path === '/login';
});
</script>

<style scoped>
.app-footer {
  padding: 20px 0;
  background: var(--primary-gradient);
  color: var(--text-white);
  text-align: center;
  font-size: 14px;
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(10px);
  width: 100%;
  z-index: 50;
}

/* 只有首页固定在底部 */
.app-footer.sticky {
  position: sticky;
  bottom: 0;
}

/* 非首页作为普通内容，不固定 */
.app-footer:not(.sticky) {
  position: relative;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content p {
  margin: 8px 0;
  color: var(--text-light);
}

.license {
  font-size: 12px;
  color: var(--text-light);
}

.license-link {
  cursor: pointer;
  text-decoration: underline;
  transition: var(--transition-fast);
  color: var(--text-light);
}

.license-link:hover {
  color: var(--text-white);
  text-decoration: none;
}

/* 底部弹出按钮样式 */
.btn-primary {
  padding: 10px 20px;
  background: var(--primary-gradient);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition);
}

.btn-primary:hover {
  background: var(--primary-gradient-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* 底部滑出式许可证内容样式补充 */
.license-content p {
  margin-bottom: 12px;
  color: #333333 !important;
}
</style> 