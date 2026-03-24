from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
import os
import json

sys.path.append(os.path.dirname(__file__))  # 确保可以导入 rag_system
from rag_system import search, generate_answer_stream  # 导入搜索和生成回答的函数

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许携带凭证（如 Cookies）
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有头信息
)  # 配置 CORS 中间件，允许所有来源、方法和头

# 基础材料路径
base_materials_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # 获取项目根目录
    "materials",
    "processed",
    "renjiao",
)

# 挂载默认材料（bixiu_1）
default_materials_path = os.path.join(base_materials_path, "bixiu_1", "pdf_extracted")
if os.path.exists(default_materials_path):
    app.mount(
        "/materials", StaticFiles(directory=default_materials_path), name="materials"
    )

# 动态挂载材料


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    documents: list = None
    distances: list = None


import time


@app.post("/api/search")
async def api_search(request: QueryRequest):
    print(f"[API] 接收到搜索请求: {request.query}")
    search_results = await search(request.query, request.top_k)
    print("[API] 搜索结果:", search_results)
    if search_results is None:
        return {
            "documents": [],
            "distances": [],
            "metadatas": [],
        }
    return {
        "documents": search_results["documents"][0],
        "distances": search_results["distances"][0],
        "metadatas": search_results["metadatas"][0],
    }


@app.post("/api/generate")
async def api_generate(request: QueryRequest):
    print(f"[API] 接收到生成请求: {request.query}")
    # 开始总计时（包括搜索和生成）
    total_start_time = time.time()

    if request.documents:
        documents = request.documents
        distances = request.distances
        print(f"[API] 使用前端传递的 {len(documents)} 个文档")
    else:
        print("[API] 前端未传递文档，重新搜索")
        search_results = await search(request.query, request.top_k)
        documents = search_results["documents"][0]
        distances = search_results["distances"][0]

    def generate():
        # 开始生成计时
        generate_start_time = time.time()

        for chunk in generate_answer_stream(request.query, documents, distances):
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"

        # 结束生成计时
        generate_end_time = time.time()
        generate_time = generate_end_time - generate_start_time
        print(f"生成回答耗时: {generate_time:.2f} 秒")

        # 结束总计时
        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        print(f"总耗时（搜索+生成）: {total_time:.2f} 秒")

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/")
async def root():
    return {"message": "高中地理 RAG API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/pdf/{textbook}/{page_num}")
async def get_pdf_page(textbook: str, page_num: int):
    """
    根据教材名称和页码获取 PDF 页面图片
    """
    pdf_path = os.path.join(
        base_materials_path,
        textbook,
        "pdf_extracted",
        "full_pages",
        f"page_{page_num}.png",
    )

    if os.path.exists(pdf_path):
        return FileResponse(pdf_path)
    else:
        # 尝试默认教材
        default_pdf_path = os.path.join(
            default_materials_path, "full_pages", f"page_{page_num}.png"
        )
        if os.path.exists(default_pdf_path):
            return FileResponse(default_pdf_path)
        else:
            return {"error": "页面不存在"}
