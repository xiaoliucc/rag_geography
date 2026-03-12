import os
import json
import re
from typing import List, Dict
import tkinter as tk
from tkinter import filedialog, messagebox


def parse_page_json(json_path: str, md_path: str, page_num: int) -> Dict:
    """解析单个页面的JSON和Markdown文件"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    page_data = {
        "page_num": page_num,
        "title": "",
        "content": "",
        "images": [],
        "blocks": [],
        "markdown": md_content,
        "json_path": json_path,
        "md_path": md_path,
    }

    if "parsing_res_list" in data:
        for block in data["parsing_res_list"]:
            block_label = block.get("block_label", "")
            block_content = block.get("block_content", "")

            if (
                block_label in ["text", "paragraph_title", "figure_title", "table"]
                and block_content
            ):
                page_data["content"] += block_content + "\n\n"

            if block_label == "paragraph_title" and block_content:
                page_data["title"] = block_content

            if block_label == "image":
                bbox = block.get("block_bbox", [])
                image_info = {
                    "bbox": bbox,
                    "image_name": f"page_{page_num}_img_in_image_box_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}.jpg",
                }
                page_data["images"].append(image_info)

            page_data["blocks"].append(
                {
                    "label": block_label,
                    "content": block_content,
                    "bbox": block.get("block_bbox", []),
                }
            )

    return page_data


def process_all_pages(data_dir: str) -> List[Dict]:
    """处理所有页面"""
    pages_dir = os.path.join(data_dir, "pages")
    markdown_dir = os.path.join(data_dir, "markdown")

    all_docs = []

    if not os.path.exists(pages_dir) or not os.path.exists(markdown_dir):
        messagebox.showerror(
            "错误",
            f"处理目录必须包含 pages 和 markdown 文件夹！\n\n"
            f"pages目录: {pages_dir} {'存在' if os.path.exists(pages_dir) else '不存在'}\n"
            f"markdown目录: {markdown_dir} {'存在' if os.path.exists(markdown_dir) else '不存在'}",
        )
        return all_docs

    for filename in os.listdir(pages_dir):
        if filename.startswith("page_") and filename.endswith(".json"):
            match = re.match(r"page_(\d+)\.json", filename)
            if match:
                page_num = int(match.group(1))
                json_path = os.path.join(pages_dir, filename)
                md_path = os.path.join(markdown_dir, f"page_{page_num}.md")

                if os.path.exists(md_path):
                    try:
                        doc = parse_page_json(json_path, md_path, page_num)
                        all_docs.append(doc)
                        if page_num % 10 == 0:
                            print(f"已处理第 {page_num} 页")
                    except Exception as e:
                        print(f"处理第 {page_num} 页失败: {e}")

    all_docs.sort(key=lambda x: x["page_num"])
    return all_docs


def save_documents_to_json(documents: List[Dict], output_path: str):
    """将文档保存为JSON文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    print(f"文档已保存到: {output_path}")


def select_input_dir():
    """
    选择输入目录（包含pages和markdown文件夹）
    :return: 输入目录路径
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    input_dir = filedialog.askdirectory(
        title="选择处理目录（必须包含pages和markdown文件夹）"
    )

    root.destroy()
    return input_dir


def select_output_file():
    """
    选择输出JSON文件
    :return: 输出文件路径
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    output_file = filedialog.asksaveasfilename(
        title="请选择对应教材的processed_documents.json文件",
        defaultextension=".json",
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        initialfile="processed_documents.json",
    )

    root.destroy()
    return output_file


def main():
    """
    主函数，处理文档
    :return: None
    """
    print("=" * 70)
    print("文档处理工具")
    print("=" * 70)

    print("\n请选择处理目录（必须包含pages和markdown文件夹）...")
    data_dir = select_input_dir()

    if not data_dir:
        print("未选择处理目录，程序退出。")
        return

    print(f"已选择处理目录: {data_dir}")

    print("\n请选择输出JSON文件...")
    output_file = select_output_file()

    if not output_file:
        print("未选择输出文件，程序退出。")
        return

    print(f"已选择输出文件: {output_file}")

    print("\n" + "=" * 70)
    print("开始处理文档...")
    print("=" * 70)

    try:
        documents = process_all_pages(data_dir)

        print(f"\n共处理 {len(documents)} 页文档")

        if documents:
            save_documents_to_json(documents, output_file)

            print("\n" + "=" * 70)
            print("处理完成！")
            print("=" * 70)

            messagebox.showinfo(
                "成功",
                f"文档处理完成！\n\n"
                f"共处理 {len(documents)} 页文档\n"
                f"保存位置: {output_file}",
            )
        else:
            messagebox.showwarning(
                "警告",
                f"未找到可处理的文档！\n\n"
                f"处理目录: {data_dir}\n"
                f"请确保目录包含 pages 和 markdown 文件夹，且有有效的页面文件。",
            )

    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        messagebox.showerror("错误", f"处理文档时出错:\n\n{str(e)}")


if __name__ == "__main__":
    main()
