<template>
  <div v-if="documents.length" class="results-section" :class="{ dark: isDark }">
    <h3>📄 检索到的参考资料 <span class="hint">(点击查看原文)</span></h3>
    <div v-for="(doc, i) in documents" :key="i" class="doc-card" @click="openViewer(i)">
      <div class="doc-header">
        <span class="doc-number">[资料 {{ i + 1 }}]</span>
        <span class="doc-textbook" v-if="metadatas[i].textbook">教材: {{ metadatas[i].textbook }}</span>
        <span class="doc-page">页码: {{ metadatas[i].page_num }}</span>
        <span class="doc-distance">相关度距离: {{ distances[i].toFixed(4) }}</span>
        <span class="view-hint">👆 点击查看</span>
      </div>
      <p class="doc-content">{{ doc }}</p>
    </div>
  </div>
</template>

<script setup>
  const props = defineProps({
    documents: {
      type: Array,
      default: () => []
    },
    distances: {
      type: Array,
      default: () => []
    },
    metadatas: {
      type: Array,
      default: () => []
    },
    isDark: {
      type: Boolean,
      default: false
    }
  })

  const emit = defineEmits(['open-viewer'])

  function openViewer(index) {
    emit('open-viewer', index)
  }
</script>

<style scoped>
  .results-section {
    margin-top: 2rem;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
  }

  .results-section h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
  }

  .results-section.dark h3 {
    color: #ecf0f1;
  }

  .hint {
    font-size: 0.85rem;
    font-weight: normal;
    color: #95a5a6;
    margin-left: 0.5rem;
  }

  .doc-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid transparent;
  }

  .doc-card:hover {
    border-color: #3498db;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.15);
    transform: translateY(-2px);
  }

  .results-section.dark .doc-card {
    background-color: #16213e;
  }

  .doc-header {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    align-items: center;
  }

  .doc-number {
    font-weight: bold;
    color: #3498db;
  }

  .doc-textbook,
  .doc-page,
  .doc-distance {
    color: #7f8c8d;
    font-size: 0.9rem;
  }

  .results-section.dark .doc-textbook,
  .results-section.dark .doc-page,
  .results-section.dark .doc-distance {
    color: #95a5a6;
  }

  .view-hint {
    font-size: 0.8rem;
    color: #3498db;
    margin-left: auto;
    opacity: 0;
    transition: opacity 0.2s;
  }

  .doc-card:hover .view-hint {
    opacity: 1;
  }

  .doc-content {
    color: #2c3e50;
  }

  .results-section.dark .doc-content {
    color: #ecf0f1;
  }
</style>
