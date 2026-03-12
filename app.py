import streamlit as st
import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "backend")
)  # 添加后端目录到系统路径

from rag_system import (
    embed_text,  # 文本向量化函数
    search,  # 向量检索函数
    generate_answer_stream,  # 回答生成流函数
    rag_query,
)

st.set_page_config(page_title="高中地理 RAG 系统", page_icon="📚", layout="wide")

st.title("📚 高中地理 RAG 系统")
st.markdown("基于增强推理的高中地理问答系统")

st.sidebar.header("配置")
top_k = st.sidebar.slider("检索文档数量 (Top-k)", 1, 20, 5)
temperature = st.sidebar.slider("生成随机性 (Temperature)", 0.0, 1.0, 0.7, 0.1)

st.sidebar.markdown("---")
st.sidebar.markdown("### 关于本系统")
st.sidebar.markdown("本系统使用向量检索 + 大语言模型，基于高中地理教材内容回答问题。")

st.markdown("---")

user_query = st.text_input(
    "请输入你的问题：", placeholder="例如：为什么地球是太阳系中特殊的行星？"
)

if st.button("🔍 提问", type="primary") and user_query:
    with st.spinner("正在检索和生成回答..."):
        try:
            search_results = search(user_query, top_k)
            context_docs = search_results["documents"][0]
            distances = search_results["distances"][0]

            st.subheader("📄 检索到的参考资料")
            for i in range(len(context_docs)):
                with st.expander(
                    f"[资料 {i+1}] 页码: {search_results['metadatas'][0][i]['page_num']} (相关度距离: {distances[i]:.4f})"
                ):
                    st.write(context_docs[i])

            st.subheader("💬 回答")
            answer_placeholder = st.empty()
            full_answer = ""

            for chunk in generate_answer_stream(user_query, context_docs, distances):
                full_answer += chunk
                answer_placeholder.markdown(full_answer)

        except Exception as e:
            st.error(f"发生错误: {str(e)}")
            st.info("请确保向量数据库已正确构建，并且 API Key 已配置。")
