import json
import os
from typing import Dict, Any


def save_data_structure(data: Any, output_path: str, indent: int = 2):
    """保存数据结构到文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    print(f"数据结构已保存到: {output_path}")


def print_data_structure(data: Any, name: str = "root", level: int = 0):
    """打印数据结构"""
    indent = "  " * level
    if isinstance(data, dict):
        print(f"{indent}{name}: {{")
        for key, value in data.items():
            print_data_structure(value, key, level + 1)
        print(f"{indent}}}")
    elif isinstance(data, list):
        if len(data) > 0:
            print(f"{indent}{name}: [ (len={len(data)})")
            print_data_structure(data[0], "[0]", level + 1)
            if len(data) > 1:
                print(f"{indent}  ... (还有 {len(data) - 1} 个元素)")
            print(f"{indent}]")
        else:
            print(f"{indent}{name}: [] (空列表)")
    else:
        data_type = type(data).__name__
        if isinstance(data, str) and len(data) > 50:
            data_str = repr(data[:50] + "...")
        else:
            data_str = repr(data)
        print(f"{indent}{name}: {data_str} ({data_type})")


def create_structure_template() -> Dict:
    """创建数据结构模板"""
    return {
        "说明": "processed_documents.json 数据结构模板",
        "顶层结构": "列表，包含134个页面数据",
        "单页数据结构": {
            "page_num": "int, 页码",
            "title": "str, 页面标题（如果有的话）",
            "content": "str, 拼接后的纯文本内容",
            "images": [
                {
                    "bbox": "list, 图片在页面上的坐标 [x1, y1, x2, y2]",
                    "image_name": "str, 图片文件名",
                }
            ],
            "blocks": [
                {
                    "label": "str, 块类型（text, paragraph_title, image, table等）",
                    "content": "str, 块内容",
                    "bbox": "list, 块坐标 [x1, y1, x2, y2]",
                }
            ],
            "markdown": "str, Markdown 原文",
            "json_path": "str, 原始JSON文件路径",
            "md_path": "str, 原始Markdown文件路径",
        },
        "使用示例": {
            "读取文件": "with open('processed_documents.json', 'r', encoding='utf-8') as f:\n    all_docs = json.load(f)",
            "访问第1页": "page_1 = all_docs[0]",
            "访问第21页": "page_21 = all_docs[20]",
            "获取内容": "content = page_21['content']",
            "获取图片": "images = page_21['images']",
        },
    }


def main():
    input_path = r"d:\Learn\RAG_Geography\materials\materials\processed_documents.json"
    output_dir = r"d:\Learn\RAG_Geography\materials\materials"

    if not os.path.exists(input_path):
        print(f"输入文件不存在: {input_path}")
        return

    print("=" * 80)
    print("📋 processed_documents.json 数据结构")
    print("=" * 80)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n" + "=" * 80)
    print("📊 数据结构预览:")
    print("=" * 80)
    print_data_structure(data)

    print("\n" + "=" * 80)
    print("💾 保存数据结构模板:")
    print("=" * 80)

    template = create_structure_template()
    template_path = os.path.join(output_dir, "data_structure_template.json")
    save_data_structure(template, template_path)

    print("\n" + "=" * 80)
    print("✅ 完成！")
    print("=" * 80)
    print("\n📁 生成的文件:")
    print(f"  - {template_path} (数据结构模板)")


if __name__ == "__main__":
    main()
