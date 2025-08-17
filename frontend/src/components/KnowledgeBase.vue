<template>
  <div class="kb-page">
    <el-row :gutter="16">
      <el-col :span="10">
        <el-card shadow="hover" class="kb-card">
          <template #header>
            <div class="card-header">
              <span>上传文档到知识库</span>
              <el-tag size="small" type="success" v-if="embeddingReady">Embedding 就绪</el-tag>
              <el-tag size="small" type="warning" v-else>Embedding 初始化中</el-tag>
            </div>
          </template>
          <el-form label-position="top">
            <el-form-item label="标题">
              <el-input v-model="form.title" placeholder="输入文档标题" maxlength="80" show-word-limit />
            </el-form-item>
            <el-form-item label="元数据（JSON）">
              <el-input
                type="textarea"
                v-model="form.metadataText"
                :autosize="{ minRows: 2, maxRows: 6 }"
                placeholder='例如：{"tag":"demo","owner":"alice"}'
              />
            </el-form-item>
            <el-form-item label="正文">
              <el-input
                type="textarea"
                v-model="form.content"
                :autosize="{ minRows: 6, maxRows: 14 }"
                placeholder="粘贴文档内容，支持纯文本"
              />
            </el-form-item>
            <el-space>
              <el-button type="primary" :loading="uploading" @click="onUpload">入库</el-button>
              <el-button @click="onReset">重置</el-button>
            </el-space>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="hover" class="kb-card">
          <template #header>
            <div class="card-header">
              <span>知识库检索预览</span>
              <el-switch v-model="useRag" inline-prompt active-text="RAG On" inactive-text="RAG Off" />
            </div>
          </template>
          <el-input
            v-model="query"
            placeholder="输入问题，按下回车或点击搜索"
            clearable
            @keyup.enter.native="onSearch"
          >
            <template #append>
              <el-button type="primary" :loading="searching" @click="onSearch">搜索</el-button>
            </template>
          </el-input>
          <div class="results" v-loading="searching">
            <div v-if="results.length === 0" class="empty">暂无结果</div>
            <el-timeline v-else>
              <el-timeline-item
                v-for="(item, idx) in results"
                :key="idx"
                :timestamp="formatScore(item.score)"
                type="primary"
              >
                <div class="result-item">
                  <div class="title">
                    <el-tag type="info" size="small">{{ idx + 1 }}</el-tag>
                    <span class="title-text">{{ item.title }}</span>
                  </div>
                  <div class="snippet">{{ item.content }}</div>
                  <div class="meta" v-if="item.metadata">
                    <pre>{{ pretty(item.metadata) }}</pre>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../utils/http'

const form = ref({
  title: '',
  metadataText: '',
  content: '',
})
const uploading = ref(false)
const embeddingReady = ref(true)

const useRag = ref(true)
const query = ref('')
const results = ref<Array<any>>([])
const searching = ref(false)

const onReset = () => {
  form.value = { title: '', metadataText: '', content: '' }
}

const parseMetadata = () => {
  if (!form.value.metadataText?.trim()) return {}
  try {
    return JSON.parse(form.value.metadataText)
  } catch (e) {
    ElMessage.error('元数据 JSON 解析失败')
    throw e
  }
}

const onUpload = async () => {
  if (!form.value.title?.trim() || !form.value.content?.trim()) {
    return ElMessage.warning('请填写标题和正文')
  }
  uploading.value = true
  try {
    const payload = {
      title: form.value.title.trim(),
      content: form.value.content,
      metadata: parseMetadata(),
    }
    const res = await http.post('/ai/v1/documents', payload)
    ElMessage.success(`文档入库成功（ID: ${res.data?.document_id ?? '未知'}）`)
    onReset()
  } catch (e) {
    ElMessage.error('文档入库失败')
  } finally {
    uploading.value = false
  }
}

const formatScore = (score: number) => `score: ${score.toFixed(3)}`
const pretty = (obj: any) => JSON.stringify(obj, null, 2)

const onSearch = async () => {
  if (!query.value.trim()) return
  searching.value = true
  try {
    const res = await http.post('/ai/v1/search', { query: query.value, top_k: 5 })
    results.value = res.data?.results || []
    if (results.value.length === 0) {
      ElMessage.info('未检索到相关文档')
    }
  } catch (e) {
    ElMessage.error('检索失败')
  } finally {
    searching.value = false
  }
}
</script>

<style scoped>
.kb-page { display: block; }
.kb-card { margin-bottom: 16px; }
.card-header { display:flex; align-items:center; justify-content: space-between; }
.results { margin-top: 12px; }
.result-item { padding: 4px 0; }
.title { display:flex; align-items:center; gap: 6px; font-weight: 600; }
.title-text { color: var(--el-text-color-primary); }
.snippet { color: var(--el-text-color-regular); margin-top: 6px; }
.meta { margin-top: 6px; background: var(--el-fill-color-lighter); padding: 8px; border-radius: 6px; }
.empty { color: var(--el-text-color-secondary); padding: 12px 0; }
</style>