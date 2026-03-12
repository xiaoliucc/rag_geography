import json
import dashscope
from http import HTTPStatus
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# ====================== 配置区域 ======================
api_key = os.getenv("DASHSCOPE_API_KEY")
# =====================================================


def select_json_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    json_file_path = filedialog.askopenfilename(
        title="请选择chunks.json文件",
        defaultextension=".json",
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        initialfile="chunks.json",
    )
    root.destroy()
    return json_file_path


def output_json_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    output_file = filedialog.asksaveasfilename(
        title="请选择输出embeddings.json文件",
        defaultextension=".json",
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        initialfile="embeddings.json",
    )
    root.destroy()
    return output_file


def main():
    """
    主函数，处理文本向量化
    :return: None
    """
    print("=" * 80)
    print("文本向量化工具")
    print("=" * 80)

    # 检查API密钥
    if not api_key:
        print("错误: 未找到 DASHSCOPE_API_KEY 环境变量")
        messagebox.showerror(
            "错误",
            "未找到 DASHSCOPE_API_KEY 环境变量！\n\n请在 .env 文件中设置 API 密钥。",
        )
        return

    # 选择输入文件
    print("\n请选择chunks.json文件...")
    json_file_path = select_json_file()

    if not json_file_path:
        print("未选择输入文件，程序退出。")
        return

    print(f"已选择输入文件: {json_file_path}")

    # 选择输出文件
    print("\n请选择输出embeddings.json文件...")
    output_path = output_json_file()

    if not output_path:
        print("未选择输出文件，程序退出。")
        return

    print(f"已选择输出文件: {output_path}")

    print("\n" + "=" * 80)
    print("正在读取数据...")
    print("=" * 80)

    try:
        # 从json文件中提取所有文本
        sentences = []
        data = []
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                sentences.append(item["content"])

        print(f"\n共读取 {len(sentences)} 个文本片段")

        print("\n" + "=" * 80)
        print("正在向量化...")
        print("=" * 80)

        # 对所有文本进行向量化
        embeddings = []
        for i, sentence in enumerate(sentences):
            if i % 20 == 0:
                print(f"处理进度: {i}/{len(sentences)}")

            resp = dashscope.TextEmbedding.call(
                model="text-embedding-v4", input=sentence
            )

            if resp.status_code == HTTPStatus.OK:
                embeddings.append(resp.output["embeddings"][0]["embedding"])
            else:
                print(f"错误: {resp.code} - {resp.message}")
                embeddings.append([0.0] * 1024)  # 出错时用零向量填充

        print("\n" + "=" * 80)
        print("向量化完成！")
        print("=" * 80)

        import numpy as np

        embeddings_array = np.array(embeddings)

        print(f"\n向量维度: {embeddings_array.shape}")
        print(f"第一个向量（前10维）: {embeddings_array[0][:10]}")

        # 保存向量结果
        output_data = []
        for i, item in enumerate(data):
            output_data.append(
                {
                    "page_num": item["page_num"],
                    "chunk_num": item["chunk_num"],
                    "content": item["content"],
                    "embedding": embeddings_array[i].tolist(),
                }
            )

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n向量化结果已保存到: {output_path}")

        messagebox.showinfo(
            "成功",
            f"文本向量化完成！\n\n"
            f"共处理 {len(sentences)} 个文本片段\n"
            f"保存位置: {output_path}",
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
        messagebox.showerror("错误", f"文本向量化时出错:\n\n{str(e)}")


if __name__ == "__main__":
    main()
