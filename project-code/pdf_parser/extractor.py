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
    extract_images: bool = True,
    render_complex_pages: bool = True,
    image_dpi: int = 150
) -> PDFContent:
    """
    深度提取PDF内容
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录（用于保存图片）
        extract_images: 是否提取嵌入图片
        render_complex_pages: 是否将复杂页面渲染为图片
        image_dpi: 渲染DPI
    
    Returns:
        PDFContent: 提取的全部内容
    """
    if not HAS_PYMUPDF:
        raise ImportError("需要安装 PyMuPDF: pip install PyMuPDF")
    
    # 创建图片目录
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_content = PDFContent()
    base_name = pdf_path.stem
    
    doc = fitz.open(pdf_path)
    
    # 提取元数据
    pdf_content.metadata = {
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
        "page_count": len(doc),
        "file_name": pdf_path.name,
    }
    
    image_counter = 0
    
    for page_num, page in enumerate(doc, 1):
        page_content = PageContent(page_num=page_num)
        
        # 1. 提取文本块（保留位置信息）
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        page_content.text_blocks = _parse_text_blocks(text_dict)
        
        # 2. 提取嵌入图片
        if extract_images:
            page_images = _extract_page_images(page, page_num, base_name, images_dir)
            page_content.images = page_images
            image_counter += len(page_images)
        
        # 3. 检测复杂图形（矢量图、图表等）
        if render_complex_pages:
            has_complex = _has_complex_graphics(page)
            page_content.has_complex_graphics = has_complex
            
            # 如果页面有复杂图形且图片少，渲染整页
            if has_complex and len(page_content.images) < 2:
                page_image = _render_page_to_image(page, image_dpi)
                if page_image:
                    # 保存页面图片
                    page_img_name = f"{base_name}_page{page_num}.png"
                    page_img_path = images_dir / page_img_name
                    page_img_path.write_bytes(page_image)
                    page_content.page_image = page_img_name
                    image_counter += 1
        
        pdf_content.pages.append(page_content)
    
    doc.close()
    pdf_content.total_images = image_counter
    
    return pdf_content


def _parse_text_blocks(text_dict: Dict) -> List[Dict[str, Any]]:
    """解析文本块，识别标题、段落等"""
    blocks = []
    
    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:  # 不是文本块
            continue
        
        block_text = ""
        max_font_size = 0
        is_bold = False
        
        for line in block.get("lines", []):
            line_text = ""
            for span in line.get("spans", []):
                line_text += span.get("text", "")
                font_size = span.get("size", 12)
                if font_size > max_font_size:
                    max_font_size = font_size
                if "bold" in span.get("font", "").lower():
                    is_bold = True
            
            block_text += line_text + "\n"
        
        block_text = block_text.strip()
        if not block_text:
            continue
        
        # 判断块类型
        block_type = _detect_block_type(block_text, max_font_size, is_bold)
        
        blocks.append({
            "type": block_type,
            "content": block_text,
            "font_size": max_font_size,
            "is_bold": is_bold,
            "bbox": block.get("bbox", [0, 0, 0, 0]),
        })
    
    return blocks


def _detect_block_type(text: str, font_size: float, is_bold: bool) -> str:
    """检测文本块类型"""
    lines = text.split("\n")
    first_line = lines[0].strip() if lines else ""
    
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
