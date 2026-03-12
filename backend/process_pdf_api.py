import os
import fitz
import shutil
from paddleocr import PaddleOCRVL
import tkinter as tk
from tkinter import filedialog, messagebox

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"


def init_ocr():
    """
    初始化PaddleOCRVL对象
    :return: 初始化的PaddleOCRVL对象
    """
    pipeline = PaddleOCRVL()
    return pipeline


def extract_page_to_image(pdf_path, page_num, output_path):
    """
    将PDF页面提取为图片
    :param pdf_path: PDF文件路径
    :param page_num: 页面编号（从1开始）
    :param output_path: 输出图片路径
    :return: 输出图片路径
    """
    pdf_doc = fitz.open(pdf_path)
    page = pdf_doc[page_num - 1]
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)
    pix.save(output_path)
    pdf_doc.close()
    return output_path


def process_image_with_ocr(ocr, image_path):
    """
    使用OCR处理图片
    :param ocr: 初始化的PaddleOCRVL对象
    :param image_path: 图片路径
    :return: OCR识别结果
    """
    result = ocr.predict(image_path)  # 调用PaddleOCRVL的predict方法进行识别
    return result  # 返回识别结果


def save_page_result(page_num, ocr_result, output_dir):
    """
    保存页面结果
    :param page_num: 页面编号（从1开始）
    :param ocr_result: OCR识别结果
    :param output_dir: 输出目录
    :return: None
    """
    pages_dir = os.path.join(output_dir, "pages")  # 页面目录
    markdown_dir = os.path.join(output_dir, "markdown")  # Markdown目录
    images_dir = os.path.join(output_dir, "images")  # 图片目录

    for dir_path in [pages_dir, markdown_dir, images_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    if ocr_result:
        for i, res in enumerate(ocr_result, 1):
            json_path = os.path.join(pages_dir, f"page_{page_num}.json")
            md_path = os.path.join(markdown_dir, f"page_{page_num}.md")

            res.save_to_json(save_path=json_path)  # 保存JSON格式结果
            res.save_to_markdown(save_path=md_path)  # 保存Markdown格式结果

            temp_img_dir_pages = os.path.join(os.path.dirname(json_path), "imgs")
            temp_img_dir_md = os.path.join(os.path.dirname(md_path), "imgs")

            for temp_img_dir in [temp_img_dir_pages, temp_img_dir_md]:
                if os.path.exists(temp_img_dir):
                    for img_file in os.listdir(temp_img_dir):
                        src_img = os.path.join(temp_img_dir, img_file)
                        dst_img = os.path.join(
                            images_dir, f"page_{page_num}_{img_file}"
                        )
                        shutil.copy2(src_img, dst_img)
                    shutil.rmtree(temp_img_dir)

            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    md_content = f.read()

                import re

                md_content = re.sub(
                    r'src="imgs/([^"]+)"',
                    lambda m: f'src="../images/page_{page_num}_{m.group(1)}"',
                    md_content,
                )

                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md_content)

                print(f"已更新 Markdown 图片路径: {md_path}")

    print(f"第{page_num}页结果已保存")


def create_index_json(output_dir):
    """
    创建index.json索引文件
    :param output_dir: 输出目录
    :return: None
    """
    import json

    index_path = os.path.join(output_dir, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "directories": {
                    "pages": "JSON格式的页面数据",
                    "markdown": "Markdown格式的页面数据",
                    "images": "提取的图片（页面完整图 + 插图）",
                    "visualization": "OCR可视化图像",
                }
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def get_pdf_page_count(pdf_path):
    """
    获取PDF总页数
    :param pdf_path: PDF文件路径
    :return: PDF总页数
    """
    pdf_doc = fitz.open(pdf_path)
    page_count = pdf_doc.page_count
    pdf_doc.close()
    return page_count


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


def main():
    """
    主函数，处理PDF文件
    :return: None
    """
    print("=" * 70)
    print("PDF处理工具")
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

    # 在选择的目录下创建 pdf_extracted 子目录
    output_dir = os.path.join(output_dir, "pdf_extracted")
    print(f"将在以下目录创建输出: {output_dir}")

    total_pages = get_pdf_page_count(pdf_path)

    print("\n" + "=" * 70)
    print("处理范围设置")
    print("=" * 70)
    print(f"PDF总页数: {total_pages}")

    start_page = input(f"开始页码（默认1）: ").strip()
    start_page = int(start_page) if start_page else 1

    end_page = input(f"结束页码（默认{total_pages}）: ").strip()
    end_page = int(end_page) if end_page else total_pages

    if start_page < 1:
        start_page = 1
    if end_page > total_pages:
        end_page = total_pages
    if start_page > end_page:
        print("错误：开始页码不能大于结束页码！")
        return

    print(f"处理页码范围: 第{start_page}-{end_page}页")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    create_index_json(output_dir)

    print("\n" + "=" * 70)
    print("正在初始化PaddleOCR...")
    ocr = init_ocr()
    print("PaddleOCR初始化完成")

    print("\n" + "=" * 70)
    print(f"开始处理PDF文件: {pdf_path}")
    print(f"输出目录: {output_dir}")
    print(f"处理页码范围: 第{start_page}-{end_page}页")
    print("=" * 70)

    for page_num in range(start_page, end_page + 1):
        print(f"\n正在处理第{page_num}页...")

        temp_image_path = f"temp_page_{page_num}.png"
        try:
            extract_page_to_image(pdf_path, page_num, temp_image_path)
            print(f"  第{page_num}页已转换为图片")

            ocr_result = process_image_with_ocr(ocr, temp_image_path)
            print(f"  第{page_num}页OCR处理完成")

            save_page_result(page_num, ocr_result, output_dir)

        except Exception as e:
            print(f"  第{page_num}页处理失败: {str(e)}")
        finally:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    print("\n" + "=" * 70)
    print("处理完成！")
    print(f"共处理 {end_page - start_page + 1} 页")
    print(f"结果保存目录: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
