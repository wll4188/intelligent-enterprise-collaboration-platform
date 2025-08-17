import { createApp } from 'vue'
import { createPinia } from 'pinia'
import persist from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/theme.css'
import App from './App.vue'
import router from './router'

// 在开发环境下，提前猴补丁全局 ResizeObserver：
// 1) 将回调延迟到下一帧执行，避免在同一帧内读写布局触发循环
// 2) 保护性捕获异常，防止无害的循环告警污染控制台
if (import.meta.env.DEV && typeof window !== 'undefined' && 'ResizeObserver' in window) {
  const RawResizeObserver = window.ResizeObserver as any
  class PatchedResizeObserver {
    private _inner: any
    constructor(cb: ResizeObserverCallback) {
      const wrapped: ResizeObserverCallback = (entries, observer) => {
        // 将处理逻辑推迟到下一帧，降低与布局写操作的竞争
        requestAnimationFrame(() => {
          try {
            cb(entries, observer)
          } catch (err) {
            // 忽略由第三方组件引发的非致命异常
          }
        })
      }
      // @ts-ignore - 构造内部真实的 ResizeObserver
      this._inner = new RawResizeObserver(wrapped)
    }
    observe(target: Element, options?: ResizeObserverOptions) {
      this._inner.observe(target, options)
    }
    unobserve(target: Element) {
      this._inner.unobserve(target)
    }
    disconnect() {
      this._inner.disconnect()
    }
  }
  // @ts-ignore 将全局 ResizeObserver 替换为补丁版本（仅开发环境）
  window.ResizeObserver = PatchedResizeObserver
}

// 初始化主题：优先本地存储，其次系统偏好
(() => {
  const saved = localStorage.getItem('theme') as 'light' | 'dark' | null
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  const theme = saved ?? (prefersDark ? 'dark' : 'light')
  document.documentElement.setAttribute('data-theme', theme)

  // 若用户没有显式选择，跟随系统变化
  if (!saved && window.matchMedia) {
    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e: MediaQueryListEvent) => {
      document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light')
    }
    try {
      mql.addEventListener('change', handler)
    } catch {
      // Safari
      // @ts-ignore
      mql.addListener(handler)
    }
  }
})()

const app = createApp(App)

// 过滤 ResizeObserver 警告
if (import.meta.env.DEV) {
  const rawWarn = console.warn
  console.warn = (...args: any[]) => {
    const msg = String(args[0] ?? '')
    if (msg && msg.includes('ResizeObserver loop completed with undelivered notifications.')) {
      return
    }
    rawWarn.apply(console, args as any)
  }
  // 可选：过滤某些由第三方库触发的非致命报错
  const rawError = console.error
  console.error = (...args: any[]) => {
    const msg = String(args[0] ?? '')
    if (msg && msg.includes('ResizeObserver loop limit exceeded')) {
      return
    }
    rawError.apply(console, args as any)
  }
  // 进一步：抑制浏览器层抛出的相关错误事件（仅开发环境）
  window.addEventListener('error', (e) => {
    const m = String((e as any).message || '')
    if (m.includes('ResizeObserver loop') || m.includes('undelivered notifications')) {
      e.stopImmediatePropagation()
    }
  }, true)
}

const pinia = createPinia()
pinia.use(persist)
app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.mount('#app')