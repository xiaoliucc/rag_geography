<template>
  <aside class="sidebar" :class="{ dark: isDark }">
    <div class="sidebar-header">
      <h3>📜 历史记录</h3>
      <button class="clear-btn" @click="clearHistory" v-if="history.length">清空</button>
    </div>
    <div class="history-list">
      <div v-for="(item, index) in history" :key="index" class="history-item"
        :class="{ active: currentIndex === index }">
        <div class="history-content" @click="loadHistory(index)">
          <div class="history-question">{{ item.question }}</div>
          <div class="history-time">{{ formatTime(item.time) }}</div>
        </div>
        <button class="delete-single-btn" @click.stop="deleteSingle(index)" title="删除这条记录">
          ✕
        </button>
      </div>
      <div v-if="history.length === 0" class="no-history">
        暂无历史记录
      </div>
    </div>
  </aside>
</template>

<script setup>
  const props = defineProps({
    history: {
      type: Array,
      default: () => []
    },
    currentIndex: {
      type: Number,
      default: -1
    },
    isDark: {
      type: Boolean,
      default: false
    }
  })

  const emit = defineEmits(['load', 'clear', 'delete-single'])

  function loadHistory(index) {
    emit('load', index)
  }

  function clearHistory() {
    emit('clear')
  }

  function deleteSingle(index) {
    if (confirm('确定要删除这条记录吗？')) {
      emit('delete-single', index)
    }
  }

  function formatTime(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date

    if (diff < 60000) {
      return '刚刚'
    } else if (diff < 3600000) {
      return `${Math.floor(diff / 60000)} 分钟前`
    } else if (diff < 86400000) {
      return `${Math.floor(diff / 3600000)} 小时前`
    } else {
      return date.toLocaleDateString('zh-CN')
    }
  }
</script>

<style scoped>
  .sidebar {
    background-color: white;
    border-right: 1px solid #e1e8ed;
    display: flex;
    flex-direction: column;
  }

  .sidebar-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e1e8ed;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .sidebar-header h3 {
    margin: 0;
    font-size: 1.1rem;
    color: #2c3e50;
  }

  .clear-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
    background-color: #e74c3c;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .clear-btn:hover {
    background-color: #c0392b;
  }

  .history-list {
    flex: 1;
    overflow-y: auto;
  }

  .history-item {
    padding: 0.8rem 1.5rem;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.8rem;
    transition: background-color 0.2s;
  }

  .history-item:hover {
    background-color: #f8f9fa;
  }

  .history-item.active {
    background-color: #e3f2fd;
    border-left: 3px solid #3498db;
  }

  .history-content {
    flex: 1;
    cursor: pointer;
    overflow: hidden;
  }

  .history-question {
    font-size: 0.95rem;
    color: #2c3e50;
    margin-bottom: 0.3rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .delete-single-btn {
    width: 1.8rem;
    height: 1.8rem;
    padding: 0;
    font-size: 1rem;
    background-color: transparent;
    color: #bdc3c7;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .delete-single-btn:hover {
    background-color: #fdeaea;
    color: #e74c3c;
  }

  .history-time {
    font-size: 0.8rem;
    color: #7f8c8d;
  }

  .no-history {
    padding: 2rem;
    text-align: center;
    color: #7f8c8d;
  }

  /* 深色主题 */
  .sidebar.dark {
    background-color: #16213e;
    border-color: #2d3a5a;
  }

  .sidebar.dark .sidebar-header {
    border-color: #2d3a5a;
  }

  .sidebar.dark .sidebar-header h3 {
    color: #ecf0f1;
  }

  .sidebar.dark .history-item {
    border-color: #2d3a5a;
  }

  .sidebar.dark .history-item:hover {
    background-color: #1a2a4a;
  }

  .sidebar.dark .history-item.active {
    background-color: #1e3a5f;
    border-left-color: #3498db;
  }

  .sidebar.dark .history-question {
    color: #ecf0f1;
  }

  .sidebar.dark .history-time {
    color: #95a5a6;
  }

  .sidebar.dark .no-history {
    color: #95a5a6;
  }

  .sidebar.dark .delete-single-btn:hover {
    background-color: #3d2020;
  }
</style>
