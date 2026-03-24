import json
import chromadb
import dashscope
from http import HTTPStatus
import os
import logging
import sys
import asyncio
import asyncio.subprocess

# ====================== 配置区域 ======================
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
# =====================================================


def get_all_vector_dbs() -> list:
    """
    获取所有向量数据库
    :return: 向量数据库列表
    """
    # 检查是否在 Docker 环境中
    # 方法1: 检查是否存在 /proc/1/cgroup 文件（Docker 容器中通常存在）
    # 方法2: 检查环境变量
    is_docker = os.path.exists("/proc/1/cgroup") or os.getenv("DOCKER_ENV") == "true"

    if is_docker:
        root_dir = "/app/materials/processed"
        print(f"当前环境: Docker, 向量数据库根目录: {root_dir}")
    else:
        # 本地环境路径
        root_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "materials", "processed"
        )
        print(f"当前环境: 本地, 向量数据库根目录: {root_dir}")
    vector_dbs = []
    if os.path.exists(root_dir):
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if "vector_db" in dirnames:
                vector_db_full_path = os.path.join(dirpath, "vector_db")
                vector_dbs.append(vector_db_full_path)
                print(f"发现向量数据库: {vector_db_full_path}")
    else:
        print(f"目录不存在: {root_dir}")
    return vector_dbs


# 全局缓存
query_rewrite_cache = {}  # 缓存查询重写结果
text_embedding_cache = {}  # 缓存文本向量化结果


def embed_text(text):
    """
    :param text: 输入文本
    :return: 文本的向量表示（如果成功），否则 None
    """
    # 检查缓存
    if text in text_embedding_cache:
        return text_embedding_cache[text]

    resp = dashscope.TextEmbedding.call(model="text-embedding-v4", input=text)
    if resp.status_code == HTTPStatus.OK:
        embedding = resp.output["embeddings"][0]["embedding"]
        # 存入缓存
        text_embedding_cache[text] = embedding
        return embedding
    else:
        print(f"向量化错误: {resp.code} - {resp.message}")
        return None


def rewrite_query(original_query):
    """
    查询重写：优化用户问题，使其更适合检索
    如果问题与地理无关，则直接返回原问题
    :param original_query: 原始用户问题
    :return: 重写后的查询
    """
    # 检查缓存
    if original_query in query_rewrite_cache:
        return query_rewrite_cache[original_query]

    prompt = f"""你是一个专业的查询优化助手。请对以下高中地理问题进行优化，使其更适合在教材中检索相关内容。

原始问题：{original_query}

请直接输出优化后的查询，不要添加任何解释。优化原则：
1. 补充可能的同义词或相关术语
2. 明确问题的核心概念
3. 保留原始问题的意图
4. 适合用于向量检索"""

    try:
        resp = dashscope.Generation.call(
            model="qwen-turbo", prompt=prompt, temperature=0.3, max_tokens=200
        )
        if resp.status_code == HTTPStatus.OK:
            rewritten = resp.output.text.strip()
            print(f"[查询重写] 原始: {original_query}")
            print(f"[查询重写] 优化: {rewritten}")
            # 存入缓存
            query_rewrite_cache[original_query] = rewritten
            return rewritten
    except Exception as e:
        print(f"[查询重写] 失败: {e}")

    return original_query


def rerank(query, docs, metadatas, distances, top_k=5):
    """
    重排序：对检索结果进行二次排序
    :param query: 用户问题
    :param docs: 文档列表
    :param metadatas: 元数据列表
    :param distances: 距离列表
    :param top_k: 返回前 K 个
    :return: 重排序后的 (docs, metadatas, scores)
    """
    print(f"[重排序] 开始对 {len(docs)} 个结果重排序...")

    # 过滤掉距离过大的文档
    filtered_pairs = []
    for doc, metadata, distance in zip(docs, metadatas, distances):
        # 距离小于 2.0 的文档才保留
        if distance < 2.0:
            filtered_pairs.append((doc, metadata, distance))

    print(f"[重排序] 过滤后剩余 {len(filtered_pairs)} 个文档")

    if not filtered_pairs:
        # 如果过滤后没有文档，返回前top_k个
        return docs[:top_k], metadatas[:top_k], [1.0 - d for d in distances[:top_k]]

    scored_docs = []
    for i, (doc, metadata, distance) in enumerate(filtered_pairs):
        # 修复基础分计算：确保分数在0-1范围内
        # 使用距离的倒数作为相似度分数（距离越小，分数越高）
        if distance <= 0:
            base_score = 1.0
        else:
            # 使用 1/(1+distance) 转换，确保分数在0-1之间
            base_score = 1.0 / (1.0 + distance)

        # 简化评分逻辑，避免LLM调用失败
        # 根据基础分设置LLM分数
        if base_score > 0.8:
            llm_score = 0.9
        elif base_score > 0.6:
            llm_score = 0.7
        elif base_score > 0.4:
            llm_score = 0.5
        elif base_score > 0.2:
            llm_score = 0.3
        else:
            llm_score = 0.1

        # 综合分数
        final_score = 0.8 * base_score + 0.2 * llm_score
        scored_docs.append((final_score, doc, metadata))
        print(
            f"[重排序] 文档 {i+1}: 基础分={base_score:.3f}, LLM分={llm_score:.3f}, 最终分={final_score:.3f}"
        )

    # 按最终分数降序排序
    scored_docs.sort(reverse=True, key=lambda x: x[0])

    # 确保只返回足够相关的文档（分数 > 0.2）
    relevant_docs = []
    relevant_metadatas = []
    relevant_scores = []

    for score, doc, metadata in scored_docs:
        if score > 0.2:
            relevant_docs.append(doc)
            relevant_metadatas.append(metadata)
            relevant_scores.append(score)

    # 如果相关文档不足，补充一些分数较低的文档
    if len(relevant_docs) < top_k:
        for score, doc, metadata in scored_docs:
            if score <= 0.2 and len(relevant_docs) < top_k:
                relevant_docs.append(doc)
                relevant_metadatas.append(metadata)
                relevant_scores.append(score)

    # 确保返回top_k个结果
    top_docs = relevant_docs[:top_k]
    top_metadatas = relevant_metadatas[:top_k]
    top_scores = relevant_scores[:top_k]

    print(f"[重排序] 完成，返回 Top-{len(top_docs)} 个相关文档")

    return top_docs, top_metadatas, top_scores


async def search_db(vector_db_path, query_embedding, retrieve_k):
    """异步处理单个数据库的检索"""
    try:
        client = chromadb.PersistentClient(path=vector_db_path)
        print(f"数据库路径: {vector_db_path}")
        collections = client.list_collections()

        db_results = []
        for collection in collections:
            print(f"集合名称: {collection.name}")
            collection = client.get_collection(name=collection.name)

            # 检索（召回更多结果供重排序）
            print(f"正在检索 Top-{retrieve_k} 结果...")
            results = collection.query(
                query_embeddings=[query_embedding], n_results=retrieve_k
            )

            db_results.append(results)

        return db_results
    except Exception as e:
        print(f"检索数据库 {vector_db_path} 失败: {e}")
        return []


async def search(query_text, top_k=10, enable_rewrite=True, enable_rerank=True):
    """在向量数据库中检索（含查询重写和重排序）"""
    import time

    # 开始计时
    start_time = time.time()

    # 1. 查询重写
    search_query = query_text
    if enable_rewrite:
        search_query = rewrite_query(query_text)

    # 2. 对查询文本向量化
    query_embedding = embed_text(search_query)
    if query_embedding is None:
        return None

    # 3. 获取所有向量数据库
    vector_db_paths = get_all_vector_dbs()
    if not vector_db_paths:
        print("未找到任何向量数据库")
        return None

    # 4. 并行检索所有数据库
    retrieve_k = top_k * 2 if enable_rerank else top_k
    tasks = [
        search_db(db_path, query_embedding, retrieve_k) for db_path in vector_db_paths
    ]
    all_db_results = await asyncio.gather(*tasks)

    # 5. 合并所有数据库的结果
    all_docs = []
    all_metadatas = []
    all_distances = []

    for db_results in all_db_results:
        for collection_results in db_results:
            all_docs.extend(collection_results["documents"][0])
            all_metadatas.extend(collection_results["metadatas"][0])
            all_distances.extend(collection_results["distances"][0])

    # 检查是否有结果
    if not all_docs:
        print("未检索到任何结果")
        return None

    # 6. 重排序
    if enable_rerank and len(all_docs) > 0:
        docs, metadatas, scores = rerank(
            query_text, all_docs, all_metadatas, all_distances, top_k
        )
        all_distances = [1.0 - s for s in scores]
    else:
        docs = all_docs[:top_k]
        metadatas = all_metadatas[:top_k]
        all_distances = all_distances[:top_k]

    # 构建返回结果
    results = {
        "documents": [docs],
        "metadatas": [metadatas],
        "distances": [all_distances],
    }

    # 结束计时并打印
    end_time = time.time()
    total_time = end_time - start_time
    print(f"检索总耗时: {total_time:.2f} 秒")

    return results


def generate_answer_stream(query, context_docs, distances=None):
    """
    流式生成回答（生成器）
    :param query: 用户问题
    :param context_docs: 检索到的相关资料
    :param distances: 相关度距离（可选）
    :yield: 文本块
    """
    # 判断是否有相关资料
    has_relevant = False
    if distances:
        # 阈值：distance < 0.7 认为相关（越小越相关）
        min_distance = min(distances)
        if min_distance < 0.7:
            has_relevant = True
    else:
        has_relevant = True

    # 构建提示词
    if has_relevant:
        context_parts = []
        for i, doc in enumerate(context_docs):
            context_parts.append(
                f"[资料 {i+1}] (相关度距离: {distances[i]:.4f})\n{doc}"
            )
        context_str = "\n\n".join(context_parts)

        prompt = f"""你是一位经验丰富、讲解生动的高中地理老师

现在你需要根据以下学习资料，回答学生提出的问题：
{context_str}

用户问题：{query}

请遵循以下教学风格：
1. **基于资料，适当延伸**：优先使用资料中的知识点，如果资料信息不全，可以结合你的专业知识补充，但要确保准确。
2. **清晰易懂**：用高中生容易理解的语言，避免过于学术化的表达，必要时举例说明。
3. **结构分明**：先简要概述核心答案，再分点详细解释；如果问题涉及地理现象的原因、形成过程或原理，请分步骤展示推导过程，让学生理解逻辑关系。
4. **启发思考**：在结尾可加一个引导性问题，鼓励学生进一步思考。"""
    else:
        prompt = f"""你是一位经验丰富、讲解生动的高中地理老师。
        学生提出了一个问题，但当前没有找到直接相关的学习资料。请你根据自己的专业知识，为学生提供清晰、准确的回答。

用户问题：{query}
请遵循以下教学风格：
1. **专业知识优先**：用你的地理知识准确回答，确保内容符合高中地理教学大纲。
2. **通俗易懂**：语言简洁明了，适合高中生理解。
3. **结构清晰**：先概括，再分点说明；对于需要推导的内容（如成因、过程），请分步骤解释，展示逻辑链条。
4. **启发思考**：可以适当提出问题，引导学生深入思考。
要求：回答要清晰、准确、有条理"""

    try:
        # 启用流式输出，设置 stream=True 和 incremental_output=True
        responses = dashscope.Generation.call(
            model="qwen-max",  # 模型名称
            prompt=prompt,  # 完整的提示词
            temperature=0.7,  # 控制生成的随机性（0.7 是一个常用值）
            stream=True,  # 启用流式输出
            incremental_output=True,  # 确保每次返回增量文本
        )
        for resp in responses:
            if resp.status_code == HTTPStatus.OK:
                # 每个块是增量文本，直接 yield
                yield resp.output.text
            else:
                # 出现错误，输出错误信息并终止
                yield f"\n[生成错误: {resp.code} - {resp.message}]"
                break
    except Exception as e:
        yield f"\n[生成异常: {str(e)}]"


def rag_query(query, top_k=5):
    """完整的 RAG 查询流程（流式输出）"""
    import time

    # 开始计时
    start_time = time.time()

    print("=" * 80)
    print(f"用户问题: {query}")
    print("=" * 80)

    # 1. 检索（异步）
    print("\n[1/3] 正在检索相关资料...")
    search_results = asyncio.run(search(query, top_k))
    if search_results is None:
        return

    context_docs = search_results["documents"][0]
    print(f"    找到 {len(context_docs)} 条相关资料")

    # 2. 生成回答（流式）
    print("\n[2/3] 正在生成回答...")
    distances = search_results["distances"][0]
    print("\n" + "=" * 80)
    print("回答：")
    print("=" * 80)
    print()  # 换行

    full_answer = ""  # 可选，用于保存完整回答
    try:
        # 迭代流式生成器，实时打印每个块
        for chunk in generate_answer_stream(query, context_docs, distances):
            print(chunk, end="", flush=True)  # 实时输出，不换行
            full_answer += chunk
    except Exception as e:
        print(f"\n流式输出过程中发生异常: {e}")

    # 3. 展示参考资料
    print("\n\n" + "=" * 80)
    print("参考资料")
    print("=" * 80)
    for i in range(len(context_docs)):
        metadata = search_results["metadatas"][0][i]
        textbook = metadata.get("textbook", "未知教材")
        print(f"\n[{i+1}] 教材: {textbook}")
        print(f"    页码: {metadata['page_num']}")
        print(f"    {context_docs[i][:150]}...")
        print(f"    相关度距离: {distances[i]:.4f}")

    # 结束计时并计算总耗时
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n\n总耗时: {total_time:.2f} 秒")

    return full_answer  # 如果需要，可以返回完整回答


if __name__ == "__main__":
    # 示例查询
    query = "锋面、气旋、反气旋如何影响天气？"
    rag_query(query, top_k=10)
