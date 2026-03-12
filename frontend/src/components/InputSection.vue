<template>
  <div class="input-section" :class="{ dark: isDark }">
    <div class="input-wrapper">
      <div class="textarea-container">
        <textarea ref="textareaRef" v-model="localQuery" placeholder="请输入你的问题，例如：为什么地球是太阳系中特殊的行星？" :rows="1"
          @keydown.ctrl.enter="askQuestion" @input="autoResize"></textarea>
        <div class="textarea-actions">
          <button v-if="localQuery" class="clear-btn" @click="localQuery = ''" title="清除">
            ✕
          </button>
          <button class="send-btn" :class="{ loading: loading, generating: generating }" @click="askQuestion"
            :disabled="loading || generating">
            {{ loading ? '⏳' : generating ? '⚡' : '⬆️' }}
          </button>
        </div>
      </div>
    </div>
    <div class="input-hint">
      <span v-if="!loading && !generating">Ctrl+Enter 发送</span>
      <span v-else>{{ loading ? '检索中...' : '生成中...' }}</span>
    </div>
  </div>
</template>

<script setup>
  import { watch, ref, nextTick } from 'vue'

  const props = defineProps({
    modelValue: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
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

  const emit = defineEmits(['update:modelValue', 'ask'])
  const textareaRef = ref(null)
  const localQuery = ref(props.modelValue)

  watch(
    () => props.modelValue,
    (newVal) => {
      localQuery.value = newVal
      nextTick(() => autoResize())
    }
  )

  watch(localQuery, (newVal) => {
    emit('update:modelValue', newVal)
  })

  function autoResize() {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
      textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 150) + 'px'
    }
  }

  function askQuestion() {
    if (localQuery.value.trim()) {
      emit('ask')
    }
  }
</script>

<style scoped>
  .input-section {
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
  }

  .input-wrapper {
    width: 100%;
  }

  .textarea-container {
    position: relative;
    background-color: white;
    border: 2px solid #e1e8ed;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    transition: all 0.2s;
  }

  .textarea-container:focus-within {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  }

  .input-section.dark .textarea-container {
    background-color: #16213e;
    border-color: #2d3a5a;
  }

  .input-section.dark .textarea-container:focus-within {
    border-color: #3498db;
  }

  .textarea-container textarea {
    width: 100%;
    padding: 0;
    padding-right: 80px;
    font-size: 1rem;
    border: none;
    outline: none;
    resize: none;
    min-height: 24px;
    max-height: 150px;
    font-family: inherit;
    line-height: 1.5;
    background-color: transparent;
    color: #2c3e50;
  }

  .input-section.dark .textarea-container textarea {
    color: #ecf0f1;
  }

  .textarea-container textarea::placeholder {
    color: #95a5a6;
  }

  .input-section.dark .textarea-container textarea::placeholder {
    color: #7f8c8d;
  }

  .textarea-actions {
    position: absolute;
    bottom: 0.6rem;
    right: 0.8rem;
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .clear-btn {
    width: 28px;
    height: 28px;
    padding: 0;
    font-size: 1.1rem;
    background-color: #f0f0f0;
    color: #7f8c8d;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .clear-btn:hover {
    background-color: #e1e8ed;
    color: #2c3e50;
  }

  .input-section.dark .clear-btn {
    background-color: #2d3a5a;
    color: #95a5a6;
  }

  .input-section.dark .clear-btn:hover {
    background-color: #3d4a6a;
    color: #ecf0f1;
  }

  .send-btn {
    width: 40px;
    height: 40px;
    padding: 0;
    font-size: 1.2rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .send-btn.loading {
    background-color: #f39c12;
  }

  .send-btn.generating {
    background-color: #9b59b6;
  }

  .send-btn:hover:not(:disabled) {
    background-color: #2980b9;
    transform: scale(1.05);
  }

  .send-btn:disabled {
    cursor: not-allowed;
    opacity: 0.9;
  }

  .input-hint {
    font-size: 0.8rem;
    color: #95a5a6;
    margin-top: 0.5rem;
    text-align: right;
  }

  .input-section.dark .input-hint {
    color: #7f8c8d;
  }
</style>
