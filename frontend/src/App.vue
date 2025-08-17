<template>
  <div class="app">
    <el-container>
      <el-header class="app-header">
        <div class="header">
          <div class="brand">
            <span class="logo" aria-hidden="true">⚡</span>
            <span>智能企业协作平台</span>
          </div>
          <div class="nav-and-user">
            <el-menu class="nav" mode="horizontal" router :default-active="$route.path">
              <el-menu-item index="/">首页</el-menu-item>
              <el-menu-item index="/chat">AI 聊天</el-menu-item>
              <el-menu-item index="/kb">知识库</el-menu-item>
              <el-menu-item index="/auth" v-if="!loggedIn">登录/注册</el-menu-item>
            </el-menu>
            <el-button link @click="toggleTheme" class="theme-toggle" :title="themeTitle">
              <span v-if="isDark">🌙</span>
              <span v-else>☀️</span>
            </el-button>
            <div class="user-area" v-if="loggedIn">
              <el-tag size="small">{{ username }}</el-tag>
              <el-button size="small" type="danger" @click="onLogout" class="logout-btn">退出</el-button>
            </div>
          </div>
        </div>
      </el-header>
      <el-main>
        <div class="page-container">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loggedIn = computed(() => !!auth.access)
const username = computed(() => auth.user?.username || '用户')

const onLogout = () => {
  auth.logout()
  router.push('/auth')
}

const isDark = ref(document.documentElement.getAttribute('data-theme') === 'dark')
const themeTitle = computed(() => isDark.value ? '切换到浅色' : '切换到深色')
const toggleTheme = () => {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}
</script>

<style scoped>
/* 移除局部 :root，统一使用全局 theme.css 中的变量 */
/* :root {
  --app-bg: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  --card-radius: 12px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.05);
} */

.app { min-height: 100vh; background: var(--app-bg); }
/* 关键约束：允许子级滚动且避免高度撑破导致的循环测量 */
.app :deep(.el-container) { min-height: 0; }
.app :deep(.el-main) { min-height: 0; overflow: auto; padding: 24px; }

.app-header { 
  background: linear-gradient(90deg, #1f6feb 0%, #3b82f6 60%, #60a5fa 100%);
  color: #fff;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}
.header { display: flex; align-items: center; justify-content: space-between; }
.brand { display:flex; align-items:center; gap: 8px; font-weight: 700; font-size: 18px; letter-spacing: 0.2px; }
.logo { display:inline-flex; width: 24px; height: 24px; align-items:center; justify-content:center; filter: drop-shadow(0 1px 1px rgba(0,0,0,0.2)); }

.nav-and-user { display: flex; align-items: center; gap: 8px; }
.nav { border-bottom: none; background: transparent; color: #fff; }
.nav :deep(.el-menu-item) { color: #eef2ff; }
.nav :deep(.el-menu-item.is-active) { background-color: rgba(255,255,255,0.18); color: #fff; border-radius: 8px; }

.user-area { display: flex; align-items: center; }
.logout-btn { margin-left: 8px; }

.page-container { max-width: 1200px; margin: 0 auto; }
.theme-toggle { color: #fff; font-size: 18px; margin: 0 6px; }
</style>