import { defineStore } from 'pinia'
import http from '../utils/http'

interface User { id: number; username: string }

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    access: '' as string,
    refresh: '' as string,
  }),
  actions: {
    async login(username: string, password: string) {
      const res = await http.post('/api/auth/login/', { username, password })
      this.user = res.data.user
      this.access = res.data.access
      this.refresh = res.data.refresh
      // Authorization 由 http 拦截器自动注入
    },
    async register(username: string, password: string) {
      await http.post('/api/auth/register/', { username, password })
    },
    async refreshAccess(): Promise<boolean> {
      if (!this.refresh) return false
      try {
        const res = await http.post('/api/auth/refresh/', { refresh: this.refresh })
        const newAccess = res.data?.access
        if (newAccess) {
          this.access = newAccess
          return true
        }
      } catch (e) {
        // 刷新失败，清空登录状态
        this.logout()
      }
      return false
    },
    logout() {
      this.user = null
      this.access = ''
      this.refresh = ''
      // 无需手动删除默认头，拦截器会根据 access 是否存在注入
    }
  },
  persist: { key: 'collab-auth' }
})