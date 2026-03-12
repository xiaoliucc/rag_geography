<template>
  <div v-if="answer" class="answer-section" :class="{ dark: isDark }">
    <div class="answer-header">
      <h3>💬 回答</h3>
      <div class="answer-buttons">
        <button class="regenerate-btn" @click="regenerate" :disabled="generating">
          {{ generating ? '⏳ 重新生成中...' : '🔄 重新生成' }}
        </button>
        <button class="copy-btn" @click="copyAnswer" :class="{ copied: copied }">
          {{ copied ? '✅ 已复制' : '📋 复制' }}
        </button>
      </div>
    </div>
    <div class="answer" v-html="renderedAnswer"></div>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { marked } from 'marked'

  const props = defineProps({
    answer: {
      type: String,
      default: ''
    },
    generating: {
      type: Boolean,
      default: false
    },
    isDark: {
      type: Boolean,
      default: false
    }
  })

  const emit = defineEmits(['regenerate'])

  const copied = ref(false)

  const renderedAnswer = computed(() => {
    if (!props.answer) return ''
    return marked(props.answer)
  })

  function copyAnswer() {
    navigator.clipboard.writeText(props.answer).then(() => {
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, 2000)
    }).catch(err => {
      console.error('复制失败:', err)
    })
  }

  function regenerate() {
    emit('regenerate')
  }
</script>

<style scoped>
  .answer-section {
    margin-top: 2rem;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
    background-color: #e3f2fd;
    padding: 1.5rem 2rem;
    border-radius: 8px;
  }

  .answer-section.dark {
    background-color: #1e3a5f;
  }

  .answer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .answer-section h3 {
    color: #2c3e50;
    margin: 0;
  }

  .answer-section.dark h3 {
    color: #ecf0f1;
  }

  .answer-buttons {
    display: flex;
    gap: 0.8rem;
  }

  .regenerate-btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    background-color: #9b59b6;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .regenerate-btn:hover:not(:disabled) {
    background-color: #8e44ad;
  }

  .regenerate-btn:disabled {
    background-color: #bdc3c7;
    cursor: not-allowed;
  }

  .copy-btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .copy-btn:hover {
    background-color: #2980b9;
  }

  .copy-btn.copied {
    background-color: #27ae60;
  }

  .answer {
    line-height: 1.8;
    color: #2c3e50;
  }

  .answer-section.dark .answer {
    color: #ecf0f1;
  }

  .answer :deep(h1),
  .answer :deep(h2),
  .answer :deep(h3) {
    color: #2c3e50;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
  }

  .answer-section.dark .answer :deep(h1),
  .answer-section.dark .answer :deep(h2),
  .answer-section.dark .answer :deep(h3) {
    color: #ecf0f1;
  }

  .answer :deep(p) {
    margin-bottom: 1rem;
  }

  .answer :deep(ul),
  .answer :deep(ol) {
    padding-left: 2rem;
    margin-bottom: 1rem;
  }

  .answer :deep(li) {
    margin-bottom: 0.5rem;
  }

  .answer :deep(strong) {
    color: #3498db;
  }
</style>
