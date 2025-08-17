import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

// 可配置：超时与重试策略
const TIMEOUT_MS = Number(import.meta.env.VITE_HTTP_TIMEOUT_MS ?? 30000)
const RETRY_COUNT = Number(import.meta.env.VITE_HTTP_RETRY_COUNT ?? 0)
const RETRY_BASE_DELAY_MS = Number(import.meta.env.VITE_HTTP_RETRY_BASE_DELAY_MS ?? 300)
const RETRY_MAX_DELAY_MS = Number(import.meta.env.VITE_HTTP_RETRY_MAX_DELAY_MS ?? 3000)

// 创建axios实例
const http: AxiosInstance = axios.create({
  baseURL: '/',
  timeout: TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 刷新令牌（并发安全：全局单例 Promise）
let refreshPromise: Promise<string> | null = null
const doRefreshToken = async (): Promise<string> => {
  const authStore = useAuthStore()
  if (!authStore.refresh) throw new Error('NO_REFRESH_TOKEN')
  if (!refreshPromise) {
    refreshPromise = axios
      .post('/api/auth/refresh/', { refresh: authStore.refresh })
      .then((res) => {
        const newAccess = res.data?.access as string
        if (!newAccess) throw new Error('INVALID_REFRESH_RESPONSE')
        authStore.access = newAccess
        return newAccess
      })
      .catch((err) => {
        // 刷新失败，清理登录状态
        authStore.logout()
        throw err
      })
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

// 请求拦截器
http.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const authStore = useAuthStore()
    
    // 自动注入认证头
    if (authStore.access && config.headers) {
      ;(config.headers as any).Authorization = `Bearer ${authStore.access}`
    }

    // 在请求配置中初始化重试计数（仅当启用重试时）
    if (RETRY_COUNT > 0) {
      ;(config as any).__retryCount = 0
    }
    
    // 开发环境打印请求信息
    if (import.meta.env.DEV) {
      console.log('📤 HTTP Request:', {
        url: config.url,
        method: config.method,
        data: (config as any).data,
        params: config.params,
        timeout: (config as any).timeout,
      })
    }
    
    return config as any
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 指数退避
const backoffDelay = (attempt: number) => {
  const base = RETRY_BASE_DELAY_MS * Math.pow(2, attempt)
  return Math.min(base, RETRY_MAX_DELAY_MS)
}

// 响应拦截器
http.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    // 优先处理取消的请求：axios v1 对 AbortController 取消错误设置 code 为 'ERR_CANCELED'
    if (axios.isCancel(error) || error?.code === 'ERR_CANCELED' || error?.name === 'AbortError') {
      if (import.meta.env.DEV) {
        console.info('⏹️ Request canceled:', error.config?.url)
      }
      return Promise.reject(error) // 静默返回，不重试、不弹Toast
    }

    const config = error.config as AxiosRequestConfig & { __retryCount?: number; _retry401?: boolean }
    const response = error.response as AxiosResponse | undefined

    // 简易重试：网络错误或5xx时进行有限次指数退避重试
    const shouldRetry = () => {
      const isNetworkError = !response
      const is5xx = !!response && response.status >= 500
      return (isNetworkError || is5xx) && RETRY_COUNT > 0 && !!config
    }

    if (shouldRetry()) {
      const cfg = config as any
      cfg.__retryCount = (cfg.__retryCount || 0) + 1
      if (cfg.__retryCount <= RETRY_COUNT) {
        const delay = backoffDelay(cfg.__retryCount - 1)
        if (import.meta.env.DEV) {
          console.warn(`🔁 Retry #${cfg.__retryCount} in ${delay}ms ->`, cfg.url)
        }
        await new Promise((r) => setTimeout(r, delay))
        return http(cfg)
      }
    }

    if (response) {
      const { status, data } = response
      // 详细错误日志（仅开发环境）
      if (import.meta.env.DEV) {
        console.error('Response Error Detail:', {
          url: response.config?.url,
          status,
          data,
        })
      }
      
      switch (status) {
        case 401: {
          const authStore = useAuthStore()
          const url = String(config?.url || '')
          // 避免对鉴权端点自刷新，且避免无限循环
          const isAuthEndpoint = url.includes('/api/auth/')
          if (config?._retry401 || isAuthEndpoint) {
            authStore.logout()
            ElMessage.error('登录已过期，请重新登录')
            if (window.location.pathname !== '/auth') {
              window.location.href = '/auth'
            }
            break
          }
          try {
            // 标记已尝试刷新
            config._retry401 = true
            const newToken = await doRefreshToken()
            if (config && config.headers) {
              ;(config.headers as any).Authorization = `Bearer ${newToken}`
            }
            return http(config)
          } catch (_) {
            authStore.logout()
            ElMessage.error('登录已过期，请重新登录')
            if (window.location.pathname !== '/auth') {
              window.location.href = '/auth'
            }
          }
          break
        }
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 422: {
          // 表单验证错误
          const errorMsg = (data as any)?.detail || '请求参数错误'
          ElMessage.error(errorMsg)
          break
        }
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
      }
    }

    // 统一向上抛出错误
    return Promise.reject(error)
  }
)

export default http