import { createRouter, createWebHistory } from 'vue-router'
import HelloWorld from '../components/HelloWorld.vue'
import Chat from '../components/Chat.vue'
import Auth from '../components/Auth.vue'
import { useAuthStore } from '../stores/auth'
import KnowledgeBase from '../components/KnowledgeBase.vue'

const routes = [
  { path: '/', name: 'home', component: HelloWorld },
  { path: '/chat', name: 'chat', component: Chat, meta: { requiresAuth: true } },
  { path: '/auth', name: 'auth', component: Auth },
  { path: '/kb', name: 'knowledge', component: KnowledgeBase, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

// 全局登录守卫（支持静默刷新）
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 如果已登录，避免进入登录页，直接跳转到目标或聊天页
  if (to.path === '/auth' && authStore.access) {
    const target = (to.query.redirect as string) || '/chat'
    return next(target)
  }

  if (to.meta.requiresAuth) {
    if (authStore.access) {
      return next()
    }
    // 无 access，尝试用 refresh 静默刷新
    if (authStore.refresh) {
      const ok = await authStore.refreshAccess()
      if (ok) return next()
    }
    // 携带重定向参数
    const redirect = encodeURIComponent(to.fullPath)
    return next(`/auth?redirect=${redirect}`)
  }
  return next()
})