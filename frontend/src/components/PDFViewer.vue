<template>
    <div class="pdf-viewer-panel" :class="{ dark: isDark }">
        <div class="panel-header">
            <div class="panel-title">
                <span class="page-icon">📄</span>
                <span>第 {{ pageNum }} 页</span>
            </div>
            <div class="panel-actions">
                <button v-if="pageNum > 1" class="nav-btn" @click="prevPage" title="上一页">
                    ◀
                </button>
                <button v-if="pageNum < 150" class="nav-btn" @click="nextPage" title="下一页">
                    ▶
                </button>
                <button class="close-btn" @click="close" title="关闭">✕</button>
            </div>
        </div>
        <div class="panel-content">
            <div v-if="pageImageUrl" class="page-image-container">
                <img :src="pageImageUrl" :alt="'第 ' + pageNum + ' 页'" class="page-image" @error="onImageError" />
            </div>
            <div v-else class="placeholder">
                <div class="placeholder-icon">📚</div>
                <p>页面图片加载中...</p>
                <p class="placeholder-hint" v-if="docContent">
                    原文内容：{{ docContent.substring(0, 100) }}...
                </p>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { computed } from 'vue'

    const props = defineProps({
        pageNum: {
            type: Number,
            default: 1
        },
        docContent: {
            type: String,
            default: ''
        },
        textbook: {
            type: String,
            default: 'bixiu_1'
        },
        isDark: {
            type: Boolean,
            default: false
        }
    })

    const emit = defineEmits(['close', 'update:pageNum'])

    const pageImageUrl = computed(() => {
        // 使用环境变量或当前页面域名
        let baseURL = import.meta.env.VITE_API_BASE_URL
        if (!baseURL) {
            // 获取当前页面的域名和协议
            baseURL = `${window.location.protocol}//${window.location.host}`
        }
        return `${baseURL}/api/pdf/${props.textbook}/${props.pageNum}?t=${Date.now()}`
    })

    function close() {
        emit('close')
    }

    function prevPage() {
        if (props.pageNum > 1) {
            emit('update:pageNum', props.pageNum - 1)
        }
    }

    function nextPage() {
        if (props.pageNum < 150) {
            emit('update:pageNum', props.pageNum + 1)
        }
    }

    function onImageError() {
        console.warn('页面图片加载失败:', pageImageUrl.value)
    }
</script>

<style scoped>
    .pdf-viewer-panel {
        height: 100%;
        display: flex;
        flex-direction: column;
        background: #fff;
        border-left: 1px solid #e0e0e0;
    }

    .pdf-viewer-panel.dark {
        background: #1e1e1e;
        border-left-color: #333;
    }

    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid #e0e0e0;
        background: #f5f5f5;
    }

    .pdf-viewer-panel.dark .panel-header {
        background: #2d2d2d;
        border-bottom-color: #333;
    }

    .panel-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        color: #333;
    }

    .pdf-viewer-panel.dark .panel-title {
        color: #e0e0e0;
    }

    .page-icon {
        font-size: 18px;
    }

    .panel-actions {
        display: flex;
        gap: 8px;
        align-items: center;
    }

    .nav-btn,
    .close-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 14px;
        transition: background 0.2s;
    }

    .nav-btn:hover {
        background: #e0e0e0;
    }

    .pdf-viewer-panel.dark .nav-btn:hover {
        background: #444;
    }

    .close-btn {
        color: #666;
        font-weight: bold;
    }

    .close-btn:hover {
        background: #ff4444;
        color: white;
    }

    .panel-content {
        flex: 1;
        overflow: auto;
        padding: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }

    .page-image-container {
        width: 100%;
        display: flex;
        justify-content: center;
    }

    .page-image {
        max-width: 100%;
        max-height: calc(100vh - 200px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border-radius: 4px;
    }

    .placeholder {
        text-align: center;
        color: #999;
        padding: 40px 20px;
    }

    .placeholder-icon {
        font-size: 48px;
        margin-bottom: 16px;
    }

    .placeholder-hint {
        font-size: 14px;
        color: #666;
        margin-top: 16px;
        max-width: 400px;
        line-height: 1.5;
    }

    .pdf-viewer-panel.dark .placeholder-hint {
        color: #aaa;
    }
</style>