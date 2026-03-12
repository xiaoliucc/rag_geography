import json
import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def clean_html_tags(text):
    """
    清理HTML标签
    :param text: 输入文本
    :return: 清理后的纯文本
    """
    clean_text = re.sub(r"<[^>]+>", "", text)
    clean_text = re.sub(r"\s+", " ", clean_text)
    return clean_text.strip()


def split_text_by_paragraph(text):
    """
    根据空行将文本分片
    :param text: 输入文本
    :return: 分片后的文本列表
    """
    chunks = text.split("\n\n")
    cleaned_chunks = []
    for chunk in chunks:
        chunk = clean_html_tags(chunk)
        if chunk:
            cleaned_chunks.append(chunk)
    return cleaned_chunks


def select_input_file():
    """
    选择输入JSON文件
    :return: 输入文件路径
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    input_file = filedialog.askopenfilename(
        title="选择输入JSON文件（processed_documents.json）",
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
    )

    root.destroy()
    return input_file


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
        title="请选择对应教材的chunks.json文件",
        defaultextension=".json",
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        initialfile="chunks.json",
    )

    root.destroy()
    return output_file


def main():
    """
    主函数，处理文本分块
    :return: None
    """
    print("=" * 70)
    print("文本分块工具")
    print("=" * 70)

    print("\n请选择输入JSON文件（processed_documents.json）...")
    input_file = select_input_file()

    if not input_file:
        print("未选择输入文件，程序退出。")
        return

    print(f"已选择输入文件: {input_file}")

    print("\n请选择输出JSON文件...")
    output_file = select_output_file()

    if not output_file:
        print("未选择输出文件，程序退出。")
        return

    print(f"已选择输出文件: {output_file}")

    print("\n" + "=" * 70)
    print("开始文本分块...")
    print("=" * 70)

    try:
        # 读取输入文件
        with open(input_file, "r", encoding="utf-8") as f:
            all_data = json.load(f)

        print(f"\n读取成功，共包含 {len(all_data)} 页文档")

        # 处理文本分块
        all_chunks = []
        total_chunks = 0

        for doc in all_data:
            if "markdown" in doc and "page_num" in doc:
                text = doc["markdown"]  # 从markdown中提取文本
                page_num = doc["page_num"]  # 从json中提取页码
                chunks = split_text_by_paragraph(text)

                for i, chunk in enumerate(chunks):
                    all_chunks.append(
                        {"page_num": page_num, "chunk_num": i, "content": chunk}
                    )

                total_chunks += len(chunks)

                if page_num % 10 == 0:
                    print(f"已处理第 {page_num} 页，生成 {total_chunks} 个分块")

        # 保存输出文件
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=4)

        print("\n" + "=" * 70)
        print(f"完成！共生成 {len(all_chunks)} 个文本分块")
        print(f"保存位置: {output_file}")
        print("=" * 70)

        messagebox.showinfo(
            "成功",
            f"文本分块完成！\n\n"
            f"共生成 {len(all_chunks)} 个文本分块\n"
            f"保存位置: {output_file}",
        )

    except json.JSONDecodeError as e:
        print(f"JSON文件解析错误: {str(e)}")
        messagebox.showerror(
            "错误", f"JSON文件解析错误:\n\n{str(e)}\n\n请确保选择的是有效的JSON文件。"
        )
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        messagebox.showerror("错误", f"文本分块时出错:\n\n{str(e)}")


if __name__ == "__main__":
    main()
