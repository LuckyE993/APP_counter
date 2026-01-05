<template>
  <div class="container">
    <div class="card">
      <div class="header">
        <h2>账本查看 - Fava</h2>
        <div class="status">
          <span :class="['status-dot', favaRunning ? 'running' : 'stopped']"></span>
          <span class="status-text">{{ favaRunning ? 'Fava运行中' : 'Fava未运行' }}</span>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="checkStatus" class="btn btn-primary" style="margin-top: 1rem;">
          重试
        </button>
      </div>

      <div v-else-if="!favaRunning" class="not-running">
        <p>Fava服务未运行</p>
        <p style="font-size: 0.875rem; color: #666; margin: 1rem 0;">
          Fava是Beancount的Web界面，可以查看账户余额、交易记录、统计报表等
        </p>
        <button @click="handleStart" class="btn btn-primary">
          启动Fava
        </button>
      </div>

      <div v-else class="actions">
        <a :href="favaUrl" target="_blank" class="btn btn-primary">
          在新窗口打开Fava
        </a>
        <button @click="handleStop" class="btn btn-secondary">
          停止Fava
        </button>
      </div>
    </div>

    <!-- Fava iframe -->
    <div v-if="favaRunning && !error" class="fava-container">
      <iframe 
        :src="favaUrl" 
        frameborder="0"
        class="fava-iframe"
        title="Fava - Beancount Web Interface"
      ></iframe>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getFavaStatus, startFava, stopFava } from '../api'

const favaRunning = ref(false)
const favaUrl = ref('')
const loading = ref(false)
const loadingMessage = ref('检查服务状态...')
const error = ref('')
let statusCheckInterval = null

const checkStatus = async () => {
  try {
    loading.value = true
    loadingMessage.value = '检查Fava状态...'
    error.value = ''
    
    const status = await getFavaStatus()
    favaRunning.value = status.running
    if (status.running && status.port) {
      // 使用当前主机地址 + Fava 端口
      const host = window.location.hostname
      favaUrl.value = `${window.location.origin}/api/fava/proxy/`
    }
  } catch (err) {
    error.value = '无法连接到后端服务: ' + (err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}

const handleStart = async () => {
  try {
    loading.value = true
    loadingMessage.value = '正在启动Fava服务...'
    error.value = ''
    
    const result = await startFava()
    if (result.success) {
      favaRunning.value = true
      // 使用当前主机地址 + Fava 端口
      const host = window.location.hostname
      favaUrl.value = `${window.location.origin}/api/fava/proxy/`
      // 等待一下让Fava完全启动
      setTimeout(() => {
        loading.value = false
      }, 2000)
    }
  } catch (err) {
    error.value = '启动Fava失败: ' + (err.response?.data?.detail || err.message)
    loading.value = false
  }
}

const handleStop = async () => {
  try {
    loading.value = true
    loadingMessage.value = '正在停止Fava服务...'
    error.value = ''
    
    const result = await stopFava()
    if (result.success) {
      favaRunning.value = false
      favaUrl.value = ''
    }
  } catch (err) {
    error.value = '停止Fava失败: ' + (err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkStatus()
  // 每30秒检查一次状态
  statusCheckInterval = setInterval(checkStatus, 30000)
})

onUnmounted(() => {
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

@media (max-width: 480px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
}

h2 {
  margin: 0;
  font-size: 1.125rem;
}

@media (min-width: 768px) {
  h2 {
    font-size: 1.25rem;
  }
}

.status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
}

@media (min-width: 768px) {
  .status {
    font-size: 0.875rem;
  }
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.running {
  background: #4DBA87;
  box-shadow: 0 0 0 2px rgba(77, 186, 135, 0.2);
}

.status-dot.stopped {
  background: #999;
}

.status-text {
  color: #666;
}

.loading {
  text-align: center;
  padding: 2rem 1rem;
}

.loading p {
  font-size: 0.875rem;
  color: #666;
}

.spinner {
  width: 32px;
  height: 32px;
  margin: 0 auto 1rem;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4DBA87;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@media (min-width: 768px) {
  .spinner {
    width: 40px;
    height: 40px;
    border-width: 4px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 2rem 1rem;
  color: #f44336;
}

.not-running {
  text-align: center;
  padding: 2rem 1rem;
}

.not-running p:first-child {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.not-running p:last-of-type {
  font-size: 0.8rem;
  color: #666;
  margin: 1rem 0;
  line-height: 1.4;
}

@media (min-width: 768px) {
  .not-running p:last-of-type {
    font-size: 0.875rem;
  }
}

.actions {
  display: flex;
  gap: 0.5rem;
  flex-direction: column;
}

@media (min-width: 480px) {
  .actions {
    flex-direction: row;
  }
}

.actions .btn {
  flex: 1;
  min-height: 44px;
}

.fava-container {
  margin-top: 1rem;
  height: calc(100vh - 200px);
  min-height: 400px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

@media (min-width: 768px) {
  .fava-container {
    height: calc(100vh - 280px);
    min-height: 600px;
  }
}

@media (min-width: 1024px) {
  .fava-container {
    height: calc(100vh - 320px);
    min-height: 700px;
  }
}

.fava-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .btn {
    min-height: 48px;
  }
}
</style>
