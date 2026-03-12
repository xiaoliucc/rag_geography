import os
import chromadb


def get_all_vector_dbs() -> list:
    """
    获取所有向量数据库
    :return: 向量数据库列表
    """
    root_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "materials")
    print(f"根目录: {root_dir}")
    print(f"根目录是否存在: {os.path.exists(root_dir)}")
    vector_dbs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "vector_db" in dirnames:
            vector_db_full_path = os.path.join(dirpath, "vector_db")
            vector_dbs.append(vector_db_full_path)
            print(f"发现向量数据库: {vector_db_full_path}")
    return vector_dbs


def get_vector_collection_name() -> str:
    """
    获取所有向量数据库的集合名称
    :return: 集合名称列表
    """
    vector_db_paths = get_all_vector_dbs()
    for vector_db_path in vector_db_paths:
        client = chromadb.PersistentClient(path=vector_db_path)
        collections = client.list_collections()
        for collection in collections:
            print(f"向量数据库 {vector_db_path} 的集合名称为: {collection.name}")


get_vector_collection_name()
