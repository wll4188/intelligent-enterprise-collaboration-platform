<template>
  <div class="auth-page">
    <el-card class="box">
      <template #header>
        <div class="header">
          <span>{{ mode === 'login' ? '登录' : '注册' }}</span>
          <el-switch v-model="modeIsLogin" active-text="登录" inactive-text="注册" style="margin-left:12px" />
        </div>
      </template>
      <el-form @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="onSubmit">{{ mode === 'login' ? '登录' : '注册' }}</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const store = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)
const modeIsLogin = ref(true)
const mode = computed(() => modeIsLogin.value ? 'login' : 'register')

const onSubmit = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    if (mode.value === 'register') {
      await store.register(username.value, password.value)
      ElMessage.success('注册成功')
    }
    await store.login(username.value, password.value)
    ElMessage.success('登录成功')
    
    // 跳转到预期页面或默认聊天页面
    const redirectTo = route.query.redirect as string || '/chat'
    router.push(redirectTo)
  } catch (error: any) {
    console.error('Auth error:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败，请检查用户名或密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { display:flex; justify-content:center; padding: 64px 16px; }
.box { width: 420px; box-shadow: 0 10px 24px rgba(0,0,0,0.06); border-radius: 14px; overflow: hidden; }
.header { display:flex; align-items:center; font-weight:600; }
</style>