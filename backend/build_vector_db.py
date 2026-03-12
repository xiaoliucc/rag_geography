import json
import chromadb
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def select_embeddings_file():
    """
    选择 embeddings.json 文件
    :return: 文件路径
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    file_path = filedialog.askopenfilename(
        title="请选择 embeddings.json 文件",
        defaultextension=".json",
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        initialfile="embeddings.json",
    )
    root.destroy()
    return file_path


def select_output_directory():
    """
    选择输出目录
    :return: 目录路径
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    output_dir = filedialog.askdirectory(
        title="请选择保存 ChromaDB 的目录",
        initialdir=os.path.join(
            os.path.dirname(__file__), "..", "materials", "processed"
        ),
    )
    root.destroy()
    return output_dir


def main():
    """
    主函数，构建向量数据库
    :return: None
    """
    print("=" * 80)
    print("构建向量数据库工具")
    print("=" * 80)

    # 选择输入文件
    print("\n请选择 embeddings.json 文件...")
    embeddings_file = select_embeddings_file()

    if not embeddings_file:
        print("未选择输入文件，程序退出。")
        return

    print(f"已选择输入文件: {embeddings_file}")

    # 选择输出目录
    print("\n请选择保存 ChromaDB 的目录...")
    output_dir = select_output_directory()

    if not output_dir:
        print("未选择输出目录，程序退出。")
        return

    # 构建数据库路径
    db_path = os.path.join(output_dir, "vector_db")
    print(f"数据库将保存到: {db_path}")

    collection_name = "geography_full"

    print("\n" + "=" * 80)
    print("正在初始化 ChromaDB...")
    print("=" * 80)

    try:
        # 初始化 ChromaDB 客户端
        client = chromadb.PersistentClient(path=db_path)

        # 获取或创建集合
        collection = client.get_or_create_collection(
            name=collection_name, metadata={"description": "高中地理全书内容"}
        )

        print("\n" + "=" * 80)
        print("正在读取向量化数据...")
        print("=" * 80)

        # 读取向量化数据
        with open(embeddings_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"共读取 {len(data)} 条记录")

        # 提取教材名称（从目录路径中获取）
        textbook_name = os.path.basename(output_dir)
        print(f"教材名称: {textbook_name}")

        # 准备数据
        ids = []  # 文档ID列表
        documents = []  # 文档内容列表
        metadatas = []  # 文档元数据列表
        embeddings = []  # 文档向量化列表

        for i, item in enumerate(data):
            # 处理没有页码信息的情况
            if "page_num" in item:
                page_num = item["page_num"]
            else:
                page_num = 0  # 默认为0
            # 处理没有chunk_num的情况
            if "chunk_num" in item:
                chunk_num = item["chunk_num"]
            else:
                chunk_num = 0  # 默认为0
            # 添加唯一索引确保ID不重复
            ids.append(f"page_{page_num}_chunk_{chunk_num}_{i}")
            documents.append(item["content"])
            metadatas.append(
                {
                    "page_num": page_num,
                    "chunk_num": chunk_num,
                    "textbook": textbook_name,  # 添加教材标识
                }
            )
            embeddings.append(item["embedding"])

        print("\n" + "=" * 80)
        print("正在添加到 ChromaDB...")
        print("=" * 80)

        # 添加到集合
        collection.add(
            ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
        )

        print("\n" + "=" * 80)
        print("添加完成！")
        print("=" * 80)

        print(f"\n集合中的文档数量: {collection.count()}")
        print(f"数据库已保存到: {db_path}")

        # 简单测试一下检索
        print("\n" + "=" * 80)
        print("测试检索：查询'地球的宇宙环境'")
        print("=" * 80)

        # 这里我们先用第一个文档的向量做个演示
        test_query_embedding = embeddings[0]

        results = collection.query(query_embeddings=[test_query_embedding], n_results=3)

        print("\n检索结果:")
        for i, doc in enumerate(results["documents"][0]):
            print(f"\n[{i+1}] 相关度: {results['distances'][0][i]:.4f}")
            print(f"    文档: {doc[:100]}...")
            print(f"    页码: {results['metadatas'][0][i]['page_num']}")
        print(f"集合名称: {collection_name}")

        # 验证检索效果
        print("\n" + "=" * 80)
        print("验证索引检索（前3条）...")
        results = collection.query(query_embeddings=[test_query_embedding], n_results=3)
        print(f"检索到的文档ID: {results['ids'][0]}")
        print(f"第一条文档元数据: {results['metadatas'][0][0]}")

        messagebox.showinfo(
            "成功",
            f"向量数据库构建完成！\n\n"
            f"共添加 {len(data)} 条记录\n"
            f"保存位置: {db_path}",
        )

    except json.JSONDecodeError as e:
        print(f"JSON文件解析错误: {str(e)}")
        messagebox.showerror(
            "错误", f"JSON文件解析错误:\n\n{str(e)}\n\n请确保选择的是有效的JSON文件。"
        )
    except FileNotFoundError as e:
        print(f"文件不存在: {str(e)}")
        messagebox.showerror("错误", f"文件不存在:\n\n{str(e)}")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        messagebox.showerror("错误", f"构建向量数据库时出错:\n\n{str(e)}")


if __name__ == "__main__":
    main()
