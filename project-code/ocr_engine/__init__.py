"""
🔍 OCR 引擎模块

支持扫描版PDF和图片的文字识别

依赖：
- pytesseract: Tesseract OCR Python封装
- Tesseract: 需要单独安装 Tesseract-OCR 软件

安装 Tesseract:
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- 安装后添加到 PATH 或设置 pytesseract.pytesseract.tesseract_cmd

中文支持:
- 安装时勾选 Chinese (Simplified) 和 Chinese (Traditional) 语言包
"""

import os
import io
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

# 尝试导入依赖
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    pytesseract = None

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False
    fitz = None


# OCR 可用性检查
def is_ocr_available() -> bool:
    """检查 OCR 功能是否可用"""
    if not HAS_TESSERACT or not HAS_PIL:
        return False
    
    # 检查 Tesseract 是否已安装
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def get_tesseract_languages() -> List[str]:
    """获取已安装的 Tesseract 语言包"""
    if not is_ocr_available():
        return []
    try:
        return pytesseract.get_languages()
    except Exception:
        return []


def has_chinese_support() -> bool:
    """检查是否有中文支持"""
    langs = get_tesseract_languages()
    return 'chi_sim' in langs or 'chi_tra' in langs


@dataclass
class OCRResult:
    """OCR 识别结果"""
    text: str = ""
    confidence: float = 0.0
    language: str = ""
    page_num: int = 0
    
    def is_valid(self) -> bool:
        """检查结果是否有效（有内容且置信度足够）"""
        return len(self.text.strip()) > 0 and self.confidence > 30


def ocr_image(
    image: "Image.Image",
    lang: str = "chi_sim+eng",
    config: str = ""
) -> OCRResult:
    """
    对单张图片进行 OCR 识别
    
    Args:
        image: PIL Image 对象
        lang: 语言代码，多语言用+连接 (如 "chi_sim+eng")
        config: Tesseract 配置参数
    
    Returns:
        OCRResult: 识别结果
    """
    if not is_ocr_available():
        return OCRResult(text="[OCR不可用: 请安装Tesseract-OCR]")
    
    if image is None:
        return OCRResult(text="")
    
    try:
        # 获取详细数据用于计算置信度
        data = pytesseract.image_to_data(
            image, 
            lang=lang, 
            config=config,
            output_type=pytesseract.Output.DICT
        )
        
        # 计算平均置信度
        confidences = [int(c) for c in data['conf'] if int(c) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # 提取文本
        text = pytesseract.image_to_string(image, lang=lang, config=config)
        
        return OCRResult(
            text=text.strip(),
            confidence=avg_confidence,
            language=lang
        )
    except Exception as e:
        return OCRResult(text=f"[OCR错误: {str(e)}]")


def ocr_image_bytes(
    image_data: bytes,
    lang: str = "chi_sim+eng",
    config: str = ""
) -> OCRResult:
    """
    对图片字节数据进行 OCR 识别
    
    Args:
        image_data: 图片字节数据
        lang: 语言代码
        config: Tesseract 配置参数
    
    Returns:
        OCRResult: 识别结果
    """
    if not HAS_PIL:
        return OCRResult(text="[需要安装Pillow]")
    
    try:
        image = Image.open(io.BytesIO(image_data))
        return ocr_image(image, lang, config)
    except Exception as e:
        return OCRResult(text=f"[图片解析错误: {str(e)}]")


def ocr_pdf_page(
    pdf_path: Path,
    page_num: int,
    lang: str = "chi_sim+eng",
    dpi: int = 300
) -> OCRResult:
    """
    对PDF的指定页面进行OCR识别
    
    Args:
        pdf_path: PDF文件路径
        page_num: 页码（从0开始）
        lang: 语言代码
        dpi: 渲染DPI（越高越清晰，但越慢）
    
    Returns:
        OCRResult: 识别结果
    """
    if not HAS_FITZ:
        return OCRResult(text="[需要安装PyMuPDF]", page_num=page_num)
    
    if not is_ocr_available():
        return OCRResult(text="[OCR不可用]", page_num=page_num)
    
    try:
        doc = fitz.open(str(pdf_path))
        if page_num >= len(doc):
            doc.close()
            return OCRResult(text="[页码超出范围]", page_num=page_num)
        
        page = doc[page_num]
        
        # 渲染页面为图片
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        
        # 转换为PIL Image
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        doc.close()
        
        # OCR识别
        result = ocr_image(image, lang)
        result.page_num = page_num
        return result
        
    except Exception as e:
        return OCRResult(text=f"[PDF处理错误: {str(e)}]", page_num=page_num)


def ocr_pdf_full(
    pdf_path: Path,
    lang: str = "chi_sim+eng",
    dpi: int = 300,
    progress_callback: Optional[callable] = None
) -> List[OCRResult]:
    """
    对整个PDF进行OCR识别
    
    Args:
        pdf_path: PDF文件路径
        lang: 语言代码
        dpi: 渲染DPI
        progress_callback: 进度回调函数 callback(current, total)
    
    Returns:
        List[OCRResult]: 每页的识别结果
    """
    if not HAS_FITZ:
        return [OCRResult(text="[需要安装PyMuPDF]")]
    
    if not is_ocr_available():
        return [OCRResult(text="[OCR不可用: 请安装Tesseract-OCR]")]
    
    results = []
    
    try:
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        
        for page_num in range(total_pages):
            if progress_callback:
                progress_callback(page_num + 1, total_pages)
            
            page = doc[page_num]
            
            # 渲染页面
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            
            # 转换并OCR
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            result = ocr_image(image, lang)
            result.page_num = page_num
            results.append(result)
        
        doc.close()
        return results
        
    except Exception as e:
        return [OCRResult(text=f"[PDF处理错误: {str(e)}]")]


def is_scanned_pdf(pdf_path: Path, sample_pages: int = 3) -> bool:
    """
    检测PDF是否为扫描版（没有可提取文字）
    
    Args:
        pdf_path: PDF文件路径
        sample_pages: 采样页数
    
    Returns:
        bool: True表示是扫描版PDF
    """
    if not HAS_FITZ:
        return False
    
    try:
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        
        # 采样检查
        check_pages = min(sample_pages, total_pages)
        text_found = 0
        
        for i in range(check_pages):
            page = doc[i]
            text = page.get_text().strip()
            if len(text) > 50:  # 有足够文字
                text_found += 1
        
        doc.close()
        
        # 如果大多数页面没有文字，认为是扫描版
        return text_found < check_pages * 0.5
        
    except Exception:
        return False


def get_ocr_status() -> Dict[str, Any]:
    """
    获取OCR功能状态
    
    Returns:
        Dict: OCR状态信息
    """
    status = {
        "available": False,
        "tesseract_installed": False,
        "tesseract_version": "",
        "languages": [],
        "has_chinese": False,
        "message": ""
    }
    
    if not HAS_PIL:
        status["message"] = "缺少Pillow库"
        return status
    
    if not HAS_TESSERACT:
        status["message"] = "缺少pytesseract库"
        return status
    
    try:
        version = pytesseract.get_tesseract_version()
        status["tesseract_installed"] = True
        status["tesseract_version"] = str(version)
        status["languages"] = get_tesseract_languages()
        status["has_chinese"] = has_chinese_support()
        status["available"] = True
        status["message"] = "OCR功能可用"
    except Exception as e:
        status["message"] = f"Tesseract未安装或未配置: {str(e)}"
    
    return status


# 导出
__all__ = [
    'is_ocr_available',
    'get_tesseract_languages', 
    'has_chinese_support',
    'OCRResult',
    'ocr_image',
    'ocr_image_bytes',
    'ocr_pdf_page',
    'ocr_pdf_full',
    'is_scanned_pdf',
    'get_ocr_status',
    'HAS_TESSERACT',
    'HAS_PIL',
]
