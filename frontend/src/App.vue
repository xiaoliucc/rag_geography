<template>
  <div class="app-container" :class="{ dark: isDark }">
    <Sidebar v-if="sidebarVisible" :history="history" :current-index="currentIndex" :is-dark="isDark"
      :style="{ width: sidebarWidth + 'px', minWidth: sidebarWidth + 'px' }" @load="loadHistory" @clear="clearHistory"
      @delete-single="deleteSingleHistory" />

    <div v-if="sidebarVisible" class="resizer" @mousedown="startResize('sidebar', $event)"></div>

    <main class="main-content">
      <div class="content-scroll">
        <header>
          <div class="header-content">
            <div class="header-left">
              <button class="toggle-sidebar-btn" @click="toggleSidebar" :title="sidebarVisible ? '隐藏历史记录' : '显示历史记录'">
                {{ sidebarVisible ? '◀' : '▶' }}
              </button>
              <div class="header-title">
                <h1>🌍 高中地理 RAG 系统</h1>
                <p>基于增强推理的高中地理问答系统</p>
              </div>
            </div>
            <div class="header-buttons">
              <button class="theme-toggle" @click="toggleTheme">
                {{ isDark ? '☀️' : '🌙' }}
              </button>
              <button class="reset-btn" @click="resetLayout" title="重置布局">↺</button>
            </div>
          </div>
        </header>

        <div class="suggestions" v-if="!answer && !loading && !generating">
          <span class="suggestions-label">试试这些问题：</span>
          <div class="suggestion-chips">
            <button v-for="q in suggestions" :key="q" class="suggestion-chip" @click="query = q; askQuestion()">
              {{ q }}
            </button>
          </div>
        </div>

        <AnswerSection :answer="answer" :generating="generating" :is-dark="isDark" @regenerate="regenerateAnswer" />

        <ResultsSection :documents="documents" :distances="distances" :metadatas="metadatas" :is-dark="isDark"
          @open-viewer="openPDFViewer" />

        <div v-if="error" class="error-section">
          <p class="error">{{ error }}</p>
        </div>
      </div>

      <div class="input-fixed">
        <InputSection v-model="query" :loading="loading" :generating="generating" :is-dark="isDark"
          @ask="askQuestion" />
      </div>
    </main>

    <div v-if="pdfViewerVisible" class="resizer" @mousedown="startResize('pdfViewer', $event)"></div>

    <PDFViewer v-if="pdfViewerVisible" :page-num="pdfViewerPage" :doc-content="pdfViewerContent"
      :textbook="pdfViewerTextbook" :is-dark="isDark"
      :style="{ width: pdfViewerWidth + 'px', minWidth: pdfViewerWidth + 'px' }" @close="closePDFViewer"
      @update:page-num="pdfViewerPage = $event" />
  </div>
</template>

<script setup>
  import { ref, onMounted, onUnmounted } from 'vue'
  import axios from 'axios'
  import Sidebar from './components/Sidebar.vue'
  import InputSection from './components/InputSection.vue'
  import ResultsSection from './components/ResultsSection.vue'
  import AnswerSection from './components/AnswerSection.vue'
  import PDFViewer from './components/PDFViewer.vue'

  const query = ref('')
  const answer = ref('')
  const documents = ref([])
  const distances = ref([])
  const metadatas = ref([])
  const loading = ref(false)
  const generating = ref(false)
  const error = ref('')
  const history = ref([])
  const currentIndex = ref(-1)
  const isDark = ref(false)
  const pdfViewerVisible = ref(false)
  const pdfViewerPage = ref(1)
  const pdfViewerContent = ref('')
  const pdfViewerTextbook = ref('bixiu_1')

  const sidebarWidth = ref(280)
  const pdfViewerWidth = ref(520)
  const sidebarVisible = ref(true)
  const isResizing = ref(false)
  const resizingType = ref(null)
  const startX = ref(0)
  const startWidth = ref(0)

  const suggestions = [
    '为什么地球是太阳系中特殊的行星？',
    '什么是天体？有哪些类型？',
    '地球自转和公转的地理意义是什么？',
    '太阳辐射对地球有什么影响？',
    '什么是晨昏线？如何判断？'
  ]

  const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || ''
  })

  function loadHistory(index) {
    const item = history.value[index]
    query.value = item.question
    answer.value = item.answer
    documents.value = item.documents
    distances.value = item.distances
    metadatas.value = item.metadatas
    currentIndex.value = index
    error.value = ''
  }

  function clearHistory() {
    history.value = []
    saveToStorage()
  }

  function deleteSingleHistory(index) {
    history.value.splice(index, 1)
    if (currentIndex.value === index) {
      currentIndex.value = -1
    } else if (currentIndex.value > index) {
      currentIndex.value--
    }
    saveToStorage()
  }

  function saveToHistory() {
    const item = {
      question: query.value,
      answer: answer.value,
      documents: [...documents.value],
      distances: [...distances.value],
      metadatas: [...metadatas.value],
      time: Date.now()
    }
    history.value.unshift(item)
    if (history.value.length > 50) {
      history.value.pop()
    }
    currentIndex.value = 0
    saveToStorage()
  }

  function saveToStorage() {
    localStorage.setItem('rag_history', JSON.stringify(history.value))
  }

  function loadFromStorage() {
    const saved = localStorage.getItem('rag_history')
    if (saved) {
      try {
        history.value = JSON.parse(saved)
      } catch (e) {
        console.error('加载历史记录失败:', e)
      }
    }
  }

  function saveLayout() {
    localStorage.setItem('rag_layout', JSON.stringify({
      sidebarWidth: sidebarWidth.value,
      pdfViewerWidth: pdfViewerWidth.value,
      sidebarVisible: sidebarVisible.value
    }))
  }

  function loadLayout() {
    const saved = localStorage.getItem('rag_layout')
    if (saved) {
      try {
        const layout = JSON.parse(saved)
        if (layout.sidebarWidth) sidebarWidth.value = layout.sidebarWidth
        if (layout.pdfViewerWidth) pdfViewerWidth.value = layout.pdfViewerWidth
        if (typeof layout.sidebarVisible === 'boolean') sidebarVisible.value = layout.sidebarVisible
      } catch (e) {
        console.error('加载布局失败:', e)
      }
    }
  }

  function resetLayout() {
    sidebarWidth.value = 280
    pdfViewerWidth.value = 520
    sidebarVisible.value = true
    saveLayout()
  }

  function toggleSidebar() {
    sidebarVisible.value = !sidebarVisible.value
    saveLayout()
  }

  function startResize(type, e) {
    isResizing.value = true
    resizingType.value = type
    startX.value = e.clientX
    if (type === 'sidebar') {
      startWidth.value = sidebarWidth.value
    } else {
      startWidth.value = pdfViewerWidth.value
    }
    document.addEventListener('mousemove', onResize)
    document.addEventListener('mouseup', stopResize)
    document.body.style.userSelect = 'none'
    document.body.style.cursor = 'col-resize'
  }

  function onResize(e) {
    if (!isResizing.value) return
    const delta = e.clientX - startX.value
    if (resizingType.value === 'sidebar') {
      const newWidth = Math.max(200, Math.min(500, startWidth.value + delta))
      sidebarWidth.value = newWidth
    } else {
      const newWidth = Math.max(400, Math.min(800, startWidth.value - delta))
      pdfViewerWidth.value = newWidth
    }
  }

  function stopResize() {
    isResizing.value = false
    resizingType.value = null
    document.removeEventListener('mousemove', onResize)
    document.removeEventListener('mouseup', stopResize)
    document.body.style.userSelect = ''
    document.body.style.cursor = ''
    saveLayout()
  }

  async function askQuestion() {
    if (!query.value.trim()) {
      return
    }
    loading.value = true
    generating.value = false
    answer.value = ''
    error.value = ''
    currentIndex.value = -1

    try {
      const searchResp = await api.post('/api/search', {
        query: query.value,
        top_k: 5
      })
      documents.value = searchResp.data.documents
      distances.value = searchResp.data.distances
      metadatas.value = searchResp.data.metadatas
      loading.value = false
      generating.value = true
      await generateAnswer()
      saveToHistory()
    } catch (err) {
      error.value = '检索失败: ' + err.message
      loading.value = false
    } finally {
      generating.value = false
    }
  }

  async function generateAnswer() {
    const baseURL = import.meta.env.VITE_API_BASE_URL || ''
    try {
      const resp = await fetch(`${baseURL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: query.value,
          documents: documents.value,
          distances: distances.value,
          top_k: 5
        })
      })

      if (!resp.ok) {
        throw new Error(`HTTP error! status: ${resp.status}`)
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              answer.value += data.chunk
            } catch (e) {
              console.error('解析数据失败:', e)
            }
          }
        }
      }
    } catch (err) {
      console.error('生成答案失败:', err)
      error.value = '生成答案失败: ' + err.message
    }
  }

  async function regenerateAnswer() {
    if (!documents.value.length) {
      return
    }
    generating.value = true
    answer.value = ''
    error.value = ''
    currentIndex.value = -1

    try {
      await generateAnswer()
      saveToHistory()
    } catch (err) {
      error.value = '重新生成失败: ' + err.message
    } finally {
      generating.value = false
    }
  }

  function toggleTheme() {
    isDark.value = !isDark.value
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  }

  function openPDFViewer(index) {
    pdfViewerPage.value = metadatas.value[index]?.page_num || 1
    pdfViewerContent.value = documents.value[index] || ''
    pdfViewerTextbook.value = metadatas.value[index]?.textbook || 'bixiu_1'
    pdfViewerVisible.value = true
  }

  function closePDFViewer() {
    pdfViewerVisible.value = false
  }

  onMounted(() => {
    loadFromStorage()
    loadLayout()
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'dark') {
      isDark.value = true
    }
  })

  onUnmounted(() => {
    stopResize()
  })
</script>

<style scoped>
  .app-container {
    display: flex;
    height: 100vh;
    background-color: #f5f7fa;
    transition: background-color 0.3s;
  }

  .app-container.dark {
    background-color: #1a1a2e;
  }

  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100vh;
    position: relative;
    min-width: 0;
  }

  .content-scroll {
    flex: 1;
    overflow-y: auto;
    padding: 2rem 2rem 120px 2rem;
  }

  .input-fixed {
    position: sticky;
    bottom: 0;
    padding: 1rem 2rem;
    background-color: #f5f7fa;
    border-top: 1px solid #e1e8ed;
    z-index: 10;
    transition: background-color 0.3s;
  }

  .app-container.dark .input-fixed {
    background-color: #1a1a2e;
    border-color: #2d3a5a;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 900px;
    margin: 0 auto;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .toggle-sidebar-btn {
    width: 40px;
    height: 40px;
    padding: 0;
    font-size: 1.3rem;
    background-color: transparent;
    color: #7f8c8d;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    flex-shrink: 0;
  }

  .toggle-sidebar-btn:hover {
    background-color: #e1e8ed;
    color: #2c3e50;
  }

  .app-container.dark .toggle-sidebar-btn:hover {
    background-color: #2d3a5a;
    color: #ecf0f1;
  }

  .header-title {
    text-align: left;
  }

  .header-title h1 {
    color: #2c3e50;
    margin-bottom: 0.5rem;
    margin-top: 0;
  }

  .header-title p {
    color: #7f8c8d;
    margin: 0;
  }

  .header-buttons {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .theme-toggle {
    padding: 0.6rem 1.2rem;
    font-size: 0.95rem;
    background-color: #2c3e50;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .theme-toggle:hover {
    background-color: #34495e;
  }

  .reset-btn {
    width: 40px;
    height: 40px;
    padding: 0;
    font-size: 1.2rem;
    background-color: transparent;
    color: #7f8c8d;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .reset-btn:hover {
    background-color: #e1e8ed;
    color: #2c3e50;
  }

  .app-container.dark .reset-btn:hover {
    background-color: #2d3a5a;
    color: #ecf0f1;
  }

  .suggestions {
    max-width: 900px;
    margin: 0 auto 1.5rem;
  }

  .suggestions-label {
    color: #7f8c8d;
    font-size: 0.9rem;
    display: block;
    margin-bottom: 0.8rem;
  }

  .suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
  }

  .suggestion-chip {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    background-color: white;
    color: #3498db;
    border: 1px solid #3498db;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .suggestion-chip:hover {
    background-color: #3498db;
    color: white;
  }

  .error-section {
    margin-top: 2rem;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
  }

  .error {
    color: #e74c3c;
    background-color: #fdeaea;
    padding: 1rem 1.5rem;
    border-radius: 8px;
  }

  .resizer {
    width: 6px;
    background-color: #e1e8ed;
    cursor: col-resize;
    flex-shrink: 0;
    transition: background-color 0.2s;
  }

  .resizer:hover {
    background-color: #3498db;
  }

  .app-container.dark .resizer {
    background-color: #2d3a5a;
  }

  .app-container.dark .resizer:hover {
    background-color: #3498db;
  }

  /* 深色主题 */
  .app-container.dark .header-left .toggle-sidebar-btn {
    color: #95a5a6;
  }

  .app-container.dark .header-title h1 {
    color: #ecf0f1;
  }

  .app-container.dark .header-title p {
    color: #95a5a6;
  }

  .app-container.dark .theme-toggle {
    background-color: #ecf0f1;
    color: #2c3e50;
  }

  .app-container.dark .theme-toggle:hover {
    background-color: #bdc3c7;
  }

  .app-container.dark .suggestions-label {
    color: #95a5a6;
  }

  .app-container.dark .suggestion-chip {
    background-color: #16213e;
    color: #3498db;
    border-color: #3498db;
  }

  .app-container.dark .suggestion-chip:hover {
    background-color: #3498db;
    color: white;
  }
</style>
