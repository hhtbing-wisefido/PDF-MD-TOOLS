"""
📖 PDF深度解析器

支持：
- 文本提取（保留结构）
- 图片提取（嵌入图片、矢量图渲染）
- 页面渲染为图片（用于包含复杂图表的页面）
"""

import os
import io
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    fitz = None


@dataclass
class ExtractedImage:
    """提取的图片"""
    image_data: bytes
    image_ext: str  # png, jpg, etc.
    page_num: int
    image_index: int
    width: int = 0
    height: int = 0
    
    def get_filename(self, base_name: str) -> str:
        """生成图片文件名"""
        return f"{base_name}_p{self.page_num}_img{self.image_index}.{self.image_ext}"


@dataclass
class PageContent:
    """页面内容"""
    page_num: int
    text_blocks: List[Dict[str, Any]] = field(default_factory=list)
    images: List[ExtractedImage] = field(default_factory=list)
    has_complex_graphics: bool = False  # 是否包含复杂图形
    page_image: Optional[bytes] = None  # 整页渲染图片


@dataclass
class PDFContent:
    """PDF全部内容"""
    pages: List[PageContent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    total_images: int = 0


def extract_pdf_content(
    pdf_path: Path,
    output_dir: Path,
    images_subdir: str = "images",
    extract_images: bool = True,
    image_dpi: int = 150
) -> PDFContent:
    """
    深度提取PDF内容（只提取嵌入图片，不渲染整页）
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录（图片子目录的父目录）
        images_subdir: 图片子目录名（默认"images"）
        extract_images: 是否提取嵌入图片
        image_dpi: 图片DPI
    
    Returns:
        PDFContent: 提取的全部内容
    """
    if not HAS_PYMUPDF:
        raise ImportError("需要安装 PyMuPDF: pip install PyMuPDF")
    
    # 创建图片目录
    images_dir = output_dir / images_subdir
    images_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_content = PDFContent()
    base_name = pdf_path.stem
    
    doc = fitz.open(pdf_path)
    
    # 提取元数据
    pdf_content.metadata = {
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
        "subject": doc.metadata.get("subject", ""),
        "creator": doc.metadata.get("creator", ""),
        "page_count": len(doc),
        "file_name": pdf_path.name,
    }
    
    image_counter = 0
    
    for page_num, page in enumerate(doc, 1):
        page_content = PageContent(page_num=page_num)
        
        # 1. 提取文本块（保留位置信息，支持多栏布局）
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        page_content.text_blocks = _parse_text_blocks(text_dict)
        
        # 2. 提取嵌入图片（只提取PDF中本身就是图片的元素）
        if extract_images:
            page_images = _extract_page_images(page, page_num, base_name, images_dir)
            page_content.images = page_images
            image_counter += len(page_images)
        
        pdf_content.pages.append(page_content)
    
    doc.close()
    pdf_content.total_images = image_counter
    
    return pdf_content


def _parse_text_blocks(text_dict: Dict) -> List[Dict[str, Any]]:
    """解析文本块，识别标题、段落等，并去除页眉页脚"""
    blocks = []
    page_height = text_dict.get("height", 842)  # A4默认高度
    page_width = text_dict.get("width", 595)
    
    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:  # 不是文本块
            continue
        
        bbox = block.get("bbox", [0, 0, 0, 0])
        
        # 去噪：过滤页眉（顶部5%）和页脚（底部8%）
        if bbox[1] < page_height * 0.05:  # 顶部区域
            continue
        if bbox[3] > page_height * 0.92:  # 底部区域
            continue
        
        block_text = ""
        max_font_size = 0
        is_bold = False
        is_mono = False  # 等宽字体（代码）
        
        for line in block.get("lines", []):
            line_text = ""
            for span in line.get("spans", []):
                line_text += span.get("text", "")
                font_size = span.get("size", 12)
                font_name = span.get("font", "").lower()
                if font_size > max_font_size:
                    max_font_size = font_size
                if "bold" in font_name:
                    is_bold = True
                if any(mono in font_name for mono in ["mono", "courier", "consolas", "code"]):
                    is_mono = True
            
            block_text += line_text + "\n"
        
        block_text = block_text.strip()
        if not block_text:
            continue
        
        # 去噪：过滤纯页码
        if _is_page_number(block_text):
            continue
        
        # 判断块类型
        block_type = _detect_block_type(block_text, max_font_size, is_bold, is_mono)
        
        blocks.append({
            "type": block_type,
            "content": block_text,
            "font_size": max_font_size,
            "is_bold": is_bold,
            "is_mono": is_mono,
            "bbox": bbox,
            "x": bbox[0],  # 用于多栏排序
        })
    
    # 按阅读顺序排序（先上后下，同行先左后右）
    blocks.sort(key=lambda b: (b["bbox"][1] // 50, b["x"]))
    
    return blocks


def _is_page_number(text: str) -> bool:
    """检测是否为页码"""
    text = text.strip()
    # 纯数字
    if text.isdigit() and len(text) <= 4:
        return True
    # "第X页" 或 "Page X"
    import re
    if re.match(r'^(第\s*\d+\s*页|page\s*\d+|p\.\s*\d+|\d+\s*/\s*\d+)$', text, re.IGNORECASE):
        return True
    return False


def _detect_block_type(text: str, font_size: float, is_bold: bool, is_mono: bool = False) -> str:
    """检测文本块类型"""
    lines = text.split("\n")
    first_line = lines[0].strip() if lines else ""
    
    # 代码块检测
    if is_mono and len(lines) >= 2:
        return "code_block"
    
    # 引用块检测（以引用符号开头）
    if first_line.startswith((">", "》", "「", "『")):
        return "blockquote"
    
    # 根据字体大小判断标题级别
    if font_size >= 18 or (is_bold and font_size >= 14):
        if len(first_line) < 100:
            return "heading1"
    elif font_size >= 14 or (is_bold and font_size >= 12):
        if len(first_line) < 100:
            return "heading2"
    elif is_bold and len(first_line) < 80:
        return "heading3"
    
    # 检测列表
    if first_line.startswith(("•", "·", "-", "*", "●")):
        return "list_item"
    if len(first_line) > 2 and first_line[0].isdigit() and first_line[1] in ".):":
        return "numbered_list"
    
    return "paragraph"


def _extract_page_images(
    page, 
    page_num: int, 
    base_name: str, 
    images_dir: Path
) -> List[ExtractedImage]:
    """提取页面中的嵌入图片"""
    images = []
    image_list = page.get_images(full=True)
    
    for img_index, img_info in enumerate(image_list):
        try:
            xref = img_info[0]
            
            # 提取图片
            base_image = page.parent.extract_image(xref)
            if not base_image:
                continue
            
            image_data = base_image["image"]
            image_ext = base_image["ext"]
            width = base_image.get("width", 0)
            height = base_image.get("height", 0)
            
            # 过滤太小的图片（可能是图标或装饰）
            if width < 50 or height < 50:
                continue
            
            extracted_img = ExtractedImage(
                image_data=image_data,
                image_ext=image_ext,
                page_num=page_num,
                image_index=img_index + 1,
                width=width,
                height=height,
            )
            
            # 保存图片
            img_filename = extracted_img.get_filename(base_name)
            img_path = images_dir / img_filename
            img_path.write_bytes(image_data)
            
            # 存储文件名而非数据
            extracted_img.image_data = b""  # 清空数据节省内存
            images.append(extracted_img)
            
        except Exception as e:
            # 跳过无法提取的图片
            continue
    
    return images


def _has_complex_graphics(page) -> bool:
    """检测页面是否包含复杂图形（矢量图、图表等）"""
    try:
        # 获取页面绘图命令
        drawings = page.get_drawings()
        
        # 如果有很多绘图命令，可能是复杂图表
        if len(drawings) > 20:
            return True
        
        # 检查是否有路径绘制
        for d in drawings:
            if d.get("items"):
                # 包含线条、曲线等
                return True
        
        return False
    except:
        return False


def _render_page_to_image(page, dpi: int = 150) -> Optional[bytes]:
    """将页面渲染为PNG图片"""
    try:
        # 计算缩放比例
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        
        # 渲染页面
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # 转换为PNG
        return pix.tobytes("png")
    except Exception as e:
        return None


# 兼容旧API
def extract_text(pdf_path: Path) -> str:
    """从PDF提取全部文本（兼容旧API）"""
    if not HAS_PYMUPDF:
        raise ImportError("需要安装 PyMuPDF: pip install PyMuPDF")
    
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_pages(pdf_path: Path) -> List[Dict[str, Any]]:
    """逐页提取PDF内容（兼容旧API）"""
    if not HAS_PYMUPDF:
        return []
    
    pages = []
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc):
        pages.append({
            "page_num": page_num + 1,
            "text": page.get_text(),
            "width": page.rect.width,
            "height": page.rect.height,
        })
    doc.close()
    return pages


# ========== OCR 支持 ==========

# 尝试导入 OCR 引擎
try:
    from ocr_engine import (
        is_ocr_available, 
        is_scanned_pdf, 
        ocr_pdf_page,
        get_ocr_status
    )
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    is_ocr_available = lambda: False
    is_scanned_pdf = lambda *args, **kwargs: False


def extract_pdf_content_with_ocr(
    pdf_path: Path,
    output_dir: Path,
    images_subdir: str = "images",
    extract_images: bool = True,
    image_dpi: int = 150,
    enable_ocr: bool = True,
    ocr_lang: str = "chi_sim+eng",
    ocr_dpi: int = 300,
    progress_callback: callable = None
) -> PDFContent:
    """
    提取PDF内容，支持扫描版PDF的OCR识别
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
        images_subdir: 图片子目录名
        extract_images: 是否提取图片
        image_dpi: 图片DPI
        enable_ocr: 是否启用OCR（仅对扫描版PDF有效）
        ocr_lang: OCR语言（默认中英文）
        ocr_dpi: OCR渲染DPI（越高越清晰但越慢）
        progress_callback: 进度回调 callback(message, current, total)
    
    Returns:
        PDFContent: 提取的内容
    """
    if not HAS_PYMUPDF:
        raise ImportError("需要安装 PyMuPDF: pip install PyMuPDF")
    
    # 检测是否为扫描版PDF
    use_ocr = False
    if enable_ocr and HAS_OCR and is_ocr_available():
        if is_scanned_pdf(pdf_path):
            use_ocr = True
            if progress_callback:
                progress_callback("检测到扫描版PDF，将使用OCR识别...", 0, 0)
    
    # 如果不需要OCR，使用普通提取
    if not use_ocr:
        return extract_pdf_content(
            pdf_path, output_dir, images_subdir, extract_images, image_dpi
        )
    
    # OCR 提取流程
    images_dir = output_dir / images_subdir
    images_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_content = PDFContent()
    base_name = pdf_path.stem
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    # 提取元数据
    pdf_content.metadata = {
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
        "subject": doc.metadata.get("subject", ""),
        "creator": doc.metadata.get("creator", ""),
        "page_count": total_pages,
        "file_name": pdf_path.name,
        "ocr_processed": True,
        "ocr_language": ocr_lang,
    }
    
    image_counter = 0
    
    for page_num in range(total_pages):
        if progress_callback:
            progress_callback(f"OCR识别第 {page_num+1}/{total_pages} 页...", page_num+1, total_pages)
        
        page = doc[page_num]
        page_content = PageContent(page_num=page_num + 1)
        
        # OCR 识别该页
        ocr_result = ocr_pdf_page(pdf_path, page_num, lang=ocr_lang, dpi=ocr_dpi)
        
        if ocr_result.text.strip():
            # 将OCR文本作为段落添加
            # 简单按段落分割
            paragraphs = ocr_result.text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para:
                    page_content.text_blocks.append({
                        "type": "paragraph",
                        "content": para,
                        "font_size": 12,
                        "is_bold": False,
                        "is_mono": False,
                        "bbox": [0, 0, 0, 0],
                        "x": 0,
                        "ocr_confidence": ocr_result.confidence,
                    })
        
        # 仍然提取嵌入图片
        if extract_images:
            page_images = _extract_page_images(page, page_num + 1, base_name, images_dir)
            page_content.images = page_images
            image_counter += len(page_images)
        
        pdf_content.pages.append(page_content)
    
    doc.close()
    pdf_content.total_images = image_counter
    
    return pdf_content


def check_ocr_status() -> dict:
    """检查OCR功能状态"""
    if not HAS_OCR:
        return {
            "available": False,
            "message": "OCR模块未安装"
        }
    return get_ocr_status()

