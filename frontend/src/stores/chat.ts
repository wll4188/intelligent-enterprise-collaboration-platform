import { defineStore } from 'pinia'
import http from '../utils/http'
import { useAuthStore } from './auth'

export interface ChatMessage {
  type: 'user' | 'ai'
  text: string
  time: string
}

export interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
  messages: Array<{
    id: number
    role: 'user' | 'ai'
    content: string
    created_at: string
  }>
}

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [
      {
        type: 'ai' as const,
        text: '您好！我是智能企业协作平台的AI助手，有什么可以帮助您的？',
        time: new Date().toLocaleTimeString(),
      },
    ] as ChatMessage[],
    currentConversationId: null as number | null,
    conversations: [] as Conversation[],
    isLoadingHistory: false,
  }),
  actions: {
    addMessage(type: 'user' | 'ai', text: string) {
      this.messages.push({
        type,
        text,
        time: new Date().toLocaleTimeString(),
      })
    },
    setMessageText(index: number, text: string) {
      if (this.messages[index]) this.messages[index].text = text
    },
    appendToMessage(index: number, chunk: string) {
      if (this.messages[index]) this.messages[index].text += chunk
    },
    beginAiMessage() {
      this.addMessage('ai', '')
      return this.messages.length - 1
    },

    clear() {
      this.messages = []
      this.currentConversationId = null
    },

    // 服务器持久化相关方法
    async createNewConversation() {
      try {
        const authStore = useAuthStore()
        if (!authStore.access) return

        const response = await http.post('/api/chat/conversations/', {
          title: '新对话'
        })
        this.currentConversationId = response.data.id
        await this.loadConversations()
        return response.data.id
      } catch (error) {
        console.error('创建对话失败:', error)
      }
    },

    async updateConversationTitle(conversationId: number, title: string) {
      try {
        const authStore = useAuthStore()
        if (!authStore.access) return
        await http.patch(`/api/chat/conversations/${conversationId}/`, { title })
        // 同步本地状态
        const conv = this.conversations.find(c => c.id === conversationId)
        if (conv) conv.title = title
      } catch (error) {
        console.error('更新对话标题失败:', error)
      }
    },

    async saveMessageToServer(type: 'user' | 'ai', content: string) {
      try {
        const authStore = useAuthStore()
        if (!authStore.access) return

        // 如果没有当前对话，创建一个
        if (!this.currentConversationId) {
          await this.createNewConversation()
        }

        if (this.currentConversationId) {
          await http.post(`/api/chat/conversations/${this.currentConversationId}/add_message/`, {
            role: type,
            content: content
          })

          // 刷新会话列表以同步更新时间
          await this.loadConversations()

          // 如果是用户消息，且对话标题为默认值或空，则用用户消息前20字符更新标题
          if (type === 'user') {
            const conv = this.conversations.find(c => c.id === this.currentConversationId!)
            const isDefaultTitle = !conv || conv.title === '新对话' || conv.title === ''
            if (isDefaultTitle) {
              const newTitle = content.trim().slice(0, 20) || '新对话'
              await this.updateConversationTitle(this.currentConversationId!, newTitle)
            }
          }
        }
      } catch (error) {
        console.error('保存消息失败:', error)
      }
    },

    async loadConversations() {
      try {
        const authStore = useAuthStore()
        if (!authStore.access) return

        this.isLoadingHistory = true
        const response = await http.get('/api/chat/conversations/')
        this.conversations = response.data
      } catch (error) {
        console.error('加载对话列表失败:', error)
      } finally {
        this.isLoadingHistory = false
      }
    },

    async loadConversation(conversationId: number) {
      try {
        const authStore = useAuthStore()
        if (!authStore.access) return

        const response = await http.get(`/api/chat/conversations/${conversationId}/`)
        const conversation = response.data

        // 将服务器消息转换为本地格式
        this.messages = conversation.messages.map((msg: any) => ({
          type: msg.role,
          text: msg.content,
          time: new Date(msg.created_at).toLocaleTimeString()
        }))

        this.currentConversationId = conversationId
      } catch (error) {
        console.error('加载对话失败:', error)
      }
    },

    async deleteConversation(conversationId: number) {
      try {
        const authStore = useAuthStore()
        if (!authStore.access) return
        await http.delete(`/api/chat/conversations/${conversationId}/`)
        this.conversations = this.conversations.filter(c => c.id !== conversationId)
        if (this.currentConversationId === conversationId) {
          this.currentConversationId = null
          this.messages = []
        }
      } catch (error) {
        console.error('删除对话失败:', error)
      }
    },

    async deleteAllConversations() {
      try {
        const authStore = useAuthStore()
        if (!authStore.access) return
        for (const conv of [...this.conversations]) {
          try {
            await http.delete(`/api/chat/conversations/${conv.id}/`)
          } catch (e) {
            console.warn('删除对话失败（跳过继续）:', conv.id, e)
          }
        }
        this.conversations = []
        this.currentConversationId = null
        this.messages = []
      } catch (error) {
        console.error('清空会话失败:', error)
      }
    },
  }
})