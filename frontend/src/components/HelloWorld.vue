<template>
  <div class="landing">
    <el-card class="welcome-card" shadow="hover">
      <div class="card-header">
        <h1 class="title">智能企业协作平台</h1>
        <p class="subtitle">基于 AI 的企业级协作解决方案</p>
      </div>
      
      <div class="feature-grid">
        <div class="feature-item">
          <div class="feature-icon">🤖</div>
          <h3>AI 智能助手</h3>
          <p>与强大的 AI 助手对话，获得专业建议和解决方案</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">💬</div>
          <h3>实时对话</h3>
          <p>支持流式对话和历史会话管理，体验流畅</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🔒</div>
          <h3>安全可靠</h3>
          <p>完善的认证机制和数据保护，确保信息安全</p>
        </div>
      </div>

      <div class="status-section">
        <div class="status-row">
          <div class="status-group">
            <el-tag :type="isBackendHealthy ? 'success' : 'danger'" effect="light" round>
              <span v-if="isBackendHealthy">✓ 后端服务正常</span>
              <span v-else>✗ 后端服务异常</span>
            </el-tag>
          </div>
          <div class="status-group">
            <el-tag :type="isAiHealthy ? 'success' : 'danger'" effect="light" round>
              <span v-if="isAiHealthy">✓ AI 服务正常</span>
              <span v-else>✗ AI 服务异常</span>
            </el-tag>
          </div>
        </div>
      </div>

      <div class="action-section">
        <el-button-group class="action-group">
          <el-button type="primary" size="large" @click="checkBackendHealth" :loading="backendChecking">
            检查后端
          </el-button>
          <el-button type="success" size="large" @click="checkAiHealth" :loading="aiChecking">
            检查 AI
          </el-button>
        </el-button-group>
        
        <el-button-group class="action-group">
          <el-button type="warning" plain @click="testEcho" :loading="echoTesting">
            AI Echo 测试
          </el-button>
          <el-button type="info" plain @click="testStreamEcho" :loading="streamTesting">
            流式测试
          </el-button>
        </el-button-group>

        <div class="nav-actions">
          <router-link to="/chat">
            <el-button type="primary" size="large" round>
              <el-icon><ChatDotRound /></el-icon>
              <span>开始对话</span>
            </el-button>
          </router-link>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.landing {
  min-height: calc(100vh - 160px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.welcome-card {
  max-width: 900px;
  width: 100%;
  border-radius: var(--card-radius);
  box-shadow: var(--shadow-md);
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
}

.card-header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.125rem;
  color: #6b7280;
  margin: 0;
  font-weight: 400;
  line-height: 1.6;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.feature-item {
  text-align: center;
  padding: 24px 16px;
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.feature-item h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.feature-item p {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

.status-section {
  margin-bottom: 32px;
}

.status-row {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.status-group {
  min-width: 140px;
}

.action-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.action-group {
  display: flex;
  gap: 12px;
}

.nav-actions {
  margin-top: 8px;
}

@media (max-width: 768px) {
  .title {
    font-size: 2rem;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .action-group {
    flex-direction: column;
    width: 100%;
    max-width: 280px;
  }
}
</style>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import http from '../utils/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

// 健康检查状态
const isBackendHealthy = ref(false)
const isAiHealthy = ref(false)
const backendChecking = ref(false)
const aiChecking = ref(false)
const echoTesting = ref(false)
const streamTesting = ref(false)

// EventSource for stream testing
let es: EventSource | null = null

const checkBackendHealth = async () => {
  backendChecking.value = true
  try {
    await http.get('/api/healthz/', { timeout: 3000 })
    isBackendHealthy.value = true
    ElMessage.success('后端服务正常')
  } catch (e) {
    isBackendHealthy.value = false
    ElMessage.error('后端服务异常')
  } finally {
    backendChecking.value = false
  }
}

const checkAiHealth = async () => {
  aiChecking.value = true
  try {
    await http.get('/ai/healthz', { timeout: 3000 })
    isAiHealthy.value = true
    ElMessage.success('AI 服务正常')
  } catch (e) {
    isAiHealthy.value = false
    ElMessage.error('AI 服务异常')
  } finally {
    aiChecking.value = false
  }
}

const testEcho = async () => {
  echoTesting.value = true
  try {
    const res = await http.post('/ai/v1/echo', { text: 'Hello from frontend!' })
    ElMessage.success(`AI Echo 测试成功: ${res.data?.response || res.data?.reply || '无回复'}`)
  } catch (error) {
    ElMessage.error('AI Echo 测试失败')
  } finally {
    echoTesting.value = false
  }
}

const testStreamEcho = async () => {
  if (streamTesting.value) return
  streamTesting.value = true
  try {
    const params = new URLSearchParams({ text: '流式测试消息' })
    if (auth.access) params.set('token', auth.access)
    
    es = new EventSource(`/ai/v1/stream_echo?${params.toString()}`)
    let result = ''
    
    es.onmessage = (e) => {
      result += e.data
    }
    
    es.addEventListener('end', () => {
      ElMessage.success(`流式测试完成: ${result}`)
      streamTesting.value = false
      es?.close()
      es = null
    })
    
    es.onerror = () => {
      ElMessage.error('流式测试失败')
      streamTesting.value = false
      es?.close()
      es = null
    }
  } catch (error) {
    ElMessage.error('流式测试异常')
    streamTesting.value = false
  }
}

onMounted(async () => {
  await Promise.all([checkBackendHealth(), checkAiHealth()])
})

// 组件卸载时清理，避免路由切换导致挂起/中断提示
onBeforeUnmount(() => {
  if (es) {
    es.close()
    es = null
  }
})

</script>