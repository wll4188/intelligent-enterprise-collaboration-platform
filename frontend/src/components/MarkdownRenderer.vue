<template>
  <div v-html="renderedHtml" class="markdown-renderer"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ content: string }>()

// 简易Markdown渲染，可替换为更强大的markdown-it等
const renderedHtml = computed(() => {
  return props.content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre class="code-block" data-lang="${lang}">
        <div class="code-header">
          <span class="language">${lang || 'text'}</span>
          <button class="copy-btn" onclick="navigator.clipboard.writeText(\`${code.replace(/`/g, '\\`')}\`)">复制</button>
        </div>
        <code>${code}</code>
      </pre>`
    })
})
</script>

<style scoped>
.markdown-renderer {
  line-height: 1.6;
  word-wrap: break-word;
}
.markdown-renderer code {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', monospace;
}
.code-block {
  background: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin: 8px 0;
  overflow: hidden;
}
.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #eee;
  padding: 8px 12px;
  border-bottom: 1px solid #ddd;
}
.language { font-size: 12px; color: #666; }
.copy-btn {
  background: #409eff;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}
.copy-btn:hover { background: #337ecc; }
.code-block code {
  display: block;
  padding: 12px;
  background: transparent;
  white-space: pre-wrap;
  font-family: 'Consolas', 'Monaco', monospace;
}
</style>