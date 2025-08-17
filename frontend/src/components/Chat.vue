<template>
  <div class="chat-container">
    <div v-if="!online" class="offline-banner">
      <el-alert type="warning" show-icon :closable="false" title="当前处于离线状态，部分功能不可用。">
        <template #default>
          <div style="margin-top:6px;">
            <el-button size="small" @click="tryReconnect" :loading="reconnecting">尝试重连</el-button>
          </div>
        </template>
      </el-alert>
    </div>
    <div class="chat-layout">
      <!-- 历史对话侧边栏 -->
      <el-card class="chat-sidebar" v-if="showSidebar" body-style="padding: 12px; overflow:auto; max-height:100%;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>历史对话</span>
            <el-button size="small" @click="createNewChat">新建</el-button>
          </div>
        </template>
        <div>
          <el-skeleton v-if="store.isLoadingHistory" :rows="5" animated />
          <div v-else>
            <div v-if="store.conversations.length === 0" class="no-conversations">
              暂无历史对话
            </div>
            <div v-else>
              <div 
                v-for="conv in store.conversations" 
                :key="conv.id"
                :class="['conversation-item', { active: conv.id === store.currentConversationId }]"
                @click="loadConversation(conv.id)"
              >
                <div class="conv-title">{{ conv.title || '新对话' }}</div>
                <div class="conv-time">{{ formatTime(conv.updated_at) }}</div>
                <el-button 
                  size="small" 
                  type="danger" 
                  text 
                  @click.stop="deleteConversation(conv.id)"
                  class="delete-btn"
                >删除</el-button>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 主聊天区域 -->
      <el-card class="chat-main" body-style="padding: 12px; display:flex; flex-direction:column; min-height:0;">
        <template #header>
          <div class="chat-header">
            <el-button 
              size="small" 
              @click="showSidebar = !showSidebar"
              style="margin-right: 8px;"
            >
              <el-icon><Menu /></el-icon>
            </el-button>
            <el-icon><ChatDotRound /></el-icon>
            <span>AI智能助手</span>
            <div style="flex:1"></div>
            <el-tag :type="online ? 'success' : 'danger'" effect="plain" size="small">
              {{ online ? '在线' : '离线' }}
            </el-tag>
            <el-button size="small" @click="clearHistory">清空会话</el-button>
            <el-switch v-model="streamMode" active-text="流式" inactive-text="一次性" style="margin-left:12px;" />
          </div>
        </template>

        <div class="chat-messages" ref="messagesContainer" style="flex:1; min-height:0;">
          <div v-for="(message, index) in messages" :key="index" class="message-item">
            <div :class="['message', message.type]">
              <div class="message-content">
                <div class="message-text"><MarkdownRenderer :content="message.text" /></div>
                <div class="message-time">{{ message.time }}</div>
              </div>
            </div>
          </div>
          <div v-if="isStreaming" class="message-item">
            <div class="message ai">
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="messages.length === 0 && !isStreaming" class="empty-state">
            <el-empty description="开始新的对话吧">
              <el-button type="primary" @click="createNewChat">新建对话</el-button>
            </el-empty>
          </div>
        </div>

        <div class="chat-input">
          <div v-if="errorMessage" style="margin-bottom:8px;">
            <el-alert :title="errorMessage" type="error" show-icon />
          </div>
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="2"
            placeholder="输入您的问题..."
            @keydown.enter.prevent="sendMessage"
            :disabled="isStreaming"
          />
          <div style="margin-top:8px; display:flex; gap:8px;">
            <el-button 
              type="primary" 
              @click="sendMessage"
              :loading="isStreaming"
              :disabled="isStreaming"
            >发送</el-button>
            <el-button v-if="isStreaming" type="danger" plain @click="stopRequest">停止</el-button>
            <el-button v-if="canRetry" type="warning" plain @click="retryLast" :loading="retrying">重试</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ChatDotRound, Menu } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useChatStore } from '../stores/chat'
import { useAuthStore } from '../stores/auth'
import http from '../utils/http'
import MarkdownRenderer from './MarkdownRenderer.vue'

const store = useChatStore()
const authStore = useAuthStore()
const messages = computed(() => store.messages)

const inputMessage = ref('')
const isStreaming = ref(false)
const streamMode = ref(true)
const messagesContainer = ref<HTMLElement>()
const controller = ref<AbortController | null>(null)
const showSidebar = ref(true)

// 网络状态检测
const online = ref<boolean>(navigator.onLine)
const reconnecting = ref(false)

// 错误与重试控制
const errorMessage = ref('')
const canRetry = ref(false)
const lastUserMessage = ref<string | null>(null)
const retrying = ref(false)

const handleOnline = () => { online.value = true }
const handleOffline = () => { online.value = false }

// 组件挂载时初始化
onMounted(async () => {
  await store.loadConversations()
  if (!store.currentConversationId && store.conversations.length === 0) {
    await store.createNewConversation()
  }
  const persisted = localStorage.getItem('chat-show-sidebar')
  if (persisted !== null) {
    showSidebar.value = persisted === '1'
  }
  // 监听网络状态
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})

const tryReconnect = async () => {
  reconnecting.value = true
  try {
    await http.get('/api/healthz/', { timeout: 3000 })
    online.value = true
    ElMessage.success('网络已恢复')
  } catch (e) {
    ElMessage.warning('仍然离线，稍后再试')
  } finally {
    reconnecting.value = false
  }
}

watch(showSidebar, (v) => {
  localStorage.setItem('chat-show-sidebar', v ? '1' : '0')
})

const formatTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

const createNewChat = async () => {
  store.clear()
  await store.createNewConversation()
}

const loadConversation = async (conversationId: number) => {
  await store.loadConversation(conversationId)
  keepScrolled()
}

const deleteConversation = async (conversationId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '确认删除', {
      type: 'warning'
    })
    await store.deleteConversation(conversationId)
    ElMessage.success('对话已删除')
  } catch (error) {
    // 用户取消删除
  }
}

let scrollScheduled = false
const keepScrolled = () => {
  if (scrollScheduled) return
  scrollScheduled = true
  requestAnimationFrame(() => {
    try {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    } catch (e) {
      // 忽略 ResizeObserver 异常
    } finally {
      scrollScheduled = false
    }
  })
}

const stopStream = () => {
  if (controller.value) {
    controller.value.abort()
  }
  isStreaming.value = false
}

// 统一的停止请求函数（一次性和流式模式通用）
const stopRequest = () => {
  if (controller.value) {
    controller.value.abort()
  }
  isStreaming.value = false
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isStreaming.value) return

  if (!online.value) {
    ElMessage.warning('当前处于离线状态，无法发送消息')
    return
  }

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  store.addMessage('user', userMessage)
  lastUserMessage.value = userMessage
  errorMessage.value = ''
  canRetry.value = false

  if (streamMode.value) {
    await sendMessageStream(userMessage)
  } else {
    await sendMessageOnce(userMessage)
  }
}

const sendMessageOnce = async (userMessage: string) => {
  try {
    isStreaming.value = true
    // 创建 AbortController 以支持取消
    controller.value = new AbortController()
    
    const response = await http.post('/api/chat/conversations/send_message/', {
      text: userMessage,
      conversation_id: store.currentConversationId
    }, {
      signal: controller.value.signal
    })
    const aiContent = response.data.ai_message?.content || ''
    const convId = response.data.conversation_id

    if (convId && !store.currentConversationId) {
      store.currentConversationId = convId
      await store.loadConversations()
    }

    const aiIndex = store.beginAiMessage()
    store.setMessageText(aiIndex, aiContent)

    await nextTick()
    keepScrolled()
  } catch (error: any) {
    // 如果是用户主动取消，不显示错误
    if (error?.name === 'AbortError' || error?.code === 'ECONNABORTED') {
      return
    }
    console.error('发送失败', error)
    errorMessage.value = error?.message || '发送失败，请稍后重试'
    canRetry.value = true
  } finally {
    isStreaming.value = false
    controller.value = null
  }
}

const sendMessageStream = async (userMessage: string) => {
  const aiIndex = store.beginAiMessage()
  try {
    isStreaming.value = true
    controller.value = new AbortController()

    const fetchWithAuthRetry = async (url: string, init: RequestInit, tried = false): Promise<Response> => {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      }
      if (authStore.access) headers['Authorization'] = `Bearer ${authStore.access}`
      const merged: RequestInit = { ...init, headers: { ...headers, ...(init.headers || {}) } }
      const resp = await fetch(url, merged)
      if (resp.status === 401 && !tried) {
        // 尝试刷新一次 token 后重试
        if (!authStore.refresh) return resp
        try {
          const refreshResp = await http.post('/api/auth/refresh/', { refresh: authStore.refresh })
          const newAccess = refreshResp.data?.access
          if (newAccess) {
            authStore.access = newAccess
            // 重新附加新 token 并重试一次
            return fetchWithAuthRetry(url, init, true)
          }
        } catch (e) {
          // 刷新失败则直接返回原始响应，由外层处理
        }
      }
      return resp
    }

    const resp = await fetchWithAuthRetry('/api/chat/conversations/stream_chat/', {
      method: 'POST',
      body: JSON.stringify({ text: userMessage, conversation_id: store.currentConversationId }),
      signal: controller.value.signal
    })
    if (resp.status === 401) {
      authStore.logout()
      if (window.location.pathname !== '/auth') {
        window.location.href = '/auth'
      }
      throw new Error('未授权或登录已过期')
    }
    if (!resp.ok || !resp.body) throw new Error(`HTTP ${resp.status}`)

    const reader = resp.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let endedByServer = false

    const handleLine = (line: string) => {
      const trimmed = line.trim()
      if (!trimmed) return
      if (trimmed.startsWith('data: ')) {
        const jsonStr = trimmed.slice(6)
        try {
          const payload = JSON.parse(jsonStr)
          const { type, data } = payload
          if (type === 'conversation_id') {
            if (!store.currentConversationId && typeof data === 'number') {
              store.currentConversationId = data
              store.loadConversations()
            }
          } else if (type === 'ai_chunk') {
            store.appendToMessage(aiIndex, String(data))
            keepScrolled()
          } else if (type === 'ai_message') {
            const full = (data && data.content) ? String(data.content) : ''
            store.setMessageText(aiIndex, full)
          } else if (type === 'error') {
            throw new Error(String(data))
          }
        } catch (e) {
          // 忽略无法解析的行
        }
      } else if (trimmed.startsWith('event: end')) {
        endedByServer = true
      }
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk
      let idx: number
      while ((idx = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, idx)
        buffer = buffer.slice(idx + 1)
        handleLine(line)
      }
      if (endedByServer) break
    }

    await store.loadConversations()
    await nextTick()
    keepScrolled()
  } catch (error: any) {
    if (error?.name === 'AbortError') {
      // 用户主动停止或服务端正常结束，不视为错误
    } else {
      console.error('流式发送失败', error)
      errorMessage.value = error?.message || '流式发送失败，请稍后重试'
      canRetry.value = true
    }
  } finally {
    isStreaming.value = false
    controller.value = null
  }
}

// 重试上一次失败的消息
const retryLast = async () => {
  if (isStreaming.value || !lastUserMessage.value) return
  errorMessage.value = ''
  canRetry.value = false
  retrying.value = true
  
  try {
    isStreaming.value = true
    const response = await http.post('/api/chat/conversations/send_message/', { 
      text: lastUserMessage.value, 
      conversation_id: store.currentConversationId 
    })
    const reply = response.data.reply || response.data.ai_message?.content || response.data.choices?.[0]?.message?.content || ''
    
    const aiIndex = store.beginAiMessage()
    store.setMessageText(aiIndex, reply)
    await nextTick()
    keepScrolled()
  } catch (error: any) {
    console.error('重试失败', error)
    errorMessage.value = error?.message || '重试失败，请稍后再试'
    canRetry.value = true
  } finally {
    isStreaming.value = false
    retrying.value = false
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('将删除所有会话及消息，且不可恢复，确定继续？', '清空会话', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
  } catch {
    return
  }
  try {
    if (authStore.access) {
      await store.deleteAllConversations()
      ElMessage.success('已清空所有会话')
    } else {
      store.clear()
      ElMessage.success('已清空本地会话')
    }
  } catch (e) {
    ElMessage.error('清空失败，请稍后再试')
  }
}
</script>

<style scoped>
/* 优化聊天消息气泡 */
.message.user .bubble {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  color: #fff;
  border-radius: 18px 18px 4px 18px;
  box-shadow: 0 6px 14px rgba(59,130,246,0.25), 0 4px 6px rgba(59,130,246,0.2);
}
.message.ai .bubble {
  background: #ffffff;
  border-radius: 18px 18px 18px 4px;
  box-shadow: var(--shadow-sm);
}
.message .bubble { padding: 12px 14px; line-height: 1.75; font-size: 15px; }

/* 调整消息区留白和滚动体验 */
.chat-messages { padding: 18px; }

/* 侧栏 hover 与选中态 */
.conversation-item { transition: transform .18s ease, box-shadow .18s ease; }
.conversation-item:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); }
.conversation-item.active { outline: 2px solid rgba(59,130,246,0.18); }

/* 输入区按钮样式统一 */
.chat-actions .el-button { border-radius: 10px; }
.chat-container { max-width: 1200px; margin: 0 auto; height: calc(100vh - 120px); contain: layout; }
.chat-layout { display: flex; gap: 16px; height: 100%; }
.chat-sidebar { width: 300px; min-height: 0; }
@media (max-width: 1200px) { .chat-sidebar { width: 260px; } }
.chat-main { flex: 1; min-height: 0; min-width: 0; border-radius: var(--card-radius); box-shadow: 0 10px 24px rgba(0,0,0,0.06); }
.chat-header { display: flex; align-items: center; gap: 8px; font-weight: 600; }
.chat-messages { max-height: 100%; overflow-y: auto; padding: 16px 0; border-bottom: 1px solid #eee; contain: layout style; }
.message-item { margin-bottom: 16px; }
.message { display: flex; max-width: 70%; }
.message.user { margin-left: auto; }
.message.user .message-content { background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); color: white; border-radius: 18px 18px 4px 18px; box-shadow: 0 6px 14px rgba(59,130,246,0.25); }
.message.ai .message-content { background: #f5f7fa; color: #333; border-radius: 18px 18px 18px 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.06); }
.message-content { padding: 12px 16px; max-width: 100%; }
.message-text { word-wrap: break-word; line-height: 1.6; }
.message-time { font-size: 12px; opacity: 0.7; margin-top: 4px; }
.empty-state { padding: 24px 0; }
.chat-input { padding: 16px 0; }
.typing-indicator { display: flex; gap: 4px; align-items: center; }
.typing-indicator span { width: 8px; height: 8px; border-radius: 50%; background: #ccc; animation: typing 1.4s infinite ease-in-out; }
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes typing { 0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }

.no-conversations { text-align: center; color: #999; padding: 20px; }
.conversation-item { 
  padding: 12px; 
  margin-bottom: 8px; 
  border: 1px solid #eee; 
  border-radius: var(--card-radius); 
  cursor: pointer; 
  position: relative;
  transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
}
.conversation-item:hover { background: #f5f7fa; box-shadow: 0 6px 12px rgba(0,0,0,0.06); transform: translateY(-1px); }
.conversation-item.active { border-color: #409eff; background: #ecf5ff; }
.conv-title { font-weight: 600; margin-bottom: 4px; }
.conv-time { font-size: 12px; color: #999; }
.delete-btn { 
  position: absolute; 
  top: 8px; 
  right: 8px; 
  opacity: 0; 
  transition: opacity 0.2s;
}
.conversation-item:hover .delete-btn { opacity: 1; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #a8a8a8; }
.offline-banner { position: sticky; top: 0; z-index: 10; margin-bottom: 8px; }
</style>