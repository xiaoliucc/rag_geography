import os
import fitz
import tkinter as tk
from tkinter import filedialog, messagebox


def select_pdf_file():
    """
    使用文件选择对话框选择PDF文件
    :return: PDF文件路径
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    pdf_path = filedialog.askopenfilename(
        title="选择PDF文件", filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
    )

    root.destroy()
    return pdf_path


def select_output_dir(materials_dir):
    """
    选择输出目录（必须在materials下）
    :param materials_dir: materials目录路径
    :return: 输出目录路径
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    output_dir = filedialog.askdirectory(
        title="选择输出目录（必须在materials下）", initialdir=materials_dir
    )

    root.destroy()

    if output_dir:
        # 转换为统一的大小写进行比较，避免 Windows 盘符大小写问题
        output_path = os.path.abspath(output_dir).lower()
        materials_path = os.path.abspath(materials_dir).lower()
        if not output_path.startswith(materials_path):
            messagebox.showerror(
                "错误",
                f"输出目录必须在 materials 目录下！\n\n"
                f"选择的目录: {output_dir}\n"
                f"materials目录: {materials_dir}",
            )
            return None

    return output_dir


def generate_full_page_images():
    """
    生成PDF页面的完整图片
    :return: None
    """
    print("=" * 70)
    print("PDF页面图片生成工具")
    print("=" * 70)

    materials_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "materials"
    )

    print("\n请选择要处理的PDF文件...")
    pdf_path = select_pdf_file()

    if not pdf_path:
        print("未选择PDF文件，程序退出。")
        return

    print(f"已选择PDF文件: {pdf_path}")

    print("\n请选择输出目录（必须在materials下）...")
    output_dir = select_output_dir(materials_dir)

    if not output_dir:
        print("未选择输出目录，程序退出。")
        return

    print(f"已选择输出目录: {output_dir}")

    # 在选择的目录下创建 pdf_extracted/full_pages 子目录
    output_dir = os.path.join(output_dir, "pdf_extracted", "full_pages")
    print(f"将在以下目录创建输出: {output_dir}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    try:
        pdf_doc = fitz.open(pdf_path)
        total_pages = pdf_doc.page_count

        print("\n" + "=" * 70)
        print(f"开始生成完整PDF页面图片...")
        print(f"PDF路径: {pdf_path}")
        print(f"输出目录: {output_dir}")
        print(f"总页数: {total_pages}")
        print("=" * 70)

        for page_num in range(total_pages):
            page = pdf_doc[page_num]
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)

            output_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
            pix.save(output_path)

            if (page_num + 1) % 10 == 0:
                print(f"已生成第 {page_num + 1}/{total_pages} 页")

        pdf_doc.close()

        print("=" * 70)
        print(f"完成！共生成 {total_pages} 页图片")
        print(f"保存位置: {output_dir}")

        messagebox.showinfo(
            "成功",
            f"PDF页面图片生成完成！\n\n"
            f"共生成 {total_pages} 页图片\n"
            f"保存位置: {output_dir}",
        )

    except Exception as e:
        print(f"生成过程中发生错误: {str(e)}")
        messagebox.showerror("错误", f"生成PDF页面图片时出错:\n\n{str(e)}")


if __name__ == "__main__":
    generate_full_page_images()
