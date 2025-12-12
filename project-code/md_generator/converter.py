"""
🔄 PDF内容转Markdown转换器

支持：
- 文本结构保留（标题、段落、列表）
- 图片引用
- 复杂页面图片嵌入
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import quote# 导入PDF解析结果类型
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from pdf_parser.extractor import PDFContent, PageContent, ExtractedImage


def convert_to_markdown(
    pdf_content: PDFContent,
    pdf_path: Path,
    images_subdir: str = "images"
) -> str:
    """
    将PDF内容转换为Markdown
    
    Args:
        pdf_content: 提取的PDF内容
        pdf_path: 原始PDF路径
        images_subdir: 图片子目录名
    
    Returns:
        Markdown文本
    """
    lines = []
    
    # 文档头
    title = pdf_content.metadata.get("title") or pdf_path.stem
    lines.append(f"# {title}")
    lines.append("")
    
    # 元信息（包含源文件追溯信息）
    lines.append("> **源文件名**: " + pdf_path.name)
    lines.append(f"> **源文件绝对路径**: `{pdf_path.absolute()}`")
    if pdf_content.metadata.get("author"):
        lines.append(f"> **作者**: {pdf_content.metadata['author']}")
    if pdf_content.metadata.get("title"):
        lines.append(f"> **PDF标题**: {pdf_content.metadata['title']}")
    if pdf_content.metadata.get("subject"):
        lines.append(f"> **主题**: {pdf_content.metadata['subject']}")
    if pdf_content.metadata.get("creator"):
        lines.append(f"> **创建程序**: {pdf_content.metadata['creator']}")
    lines.append(f"> **页数**: {pdf_content.metadata.get('page_count', len(pdf_content.pages))}")
    try:
        file_size = pdf_path.stat().st_size / 1024
        lines.append(f"> **文件大小**: {file_size:.1f} KB")
    except (OSError, FileNotFoundError):
        pass  # 文件不存在时跳过
    lines.append(f"> **转换时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if pdf_content.total_images > 0:
        lines.append(f"> **提取图片**: {pdf_content.total_images} 张")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 逐页转换
    for page in pdf_content.pages:
        page_md = _convert_page(page, pdf_path.stem, images_subdir)
        lines.append(page_md)
    
    return "\n".join(lines)


def _convert_page(
    page: PageContent, 
    base_name: str,
    images_subdir: str
) -> str:
    """转换单页内容"""
    lines = []
    
    # 如果有整页渲染图片（复杂图表页面）
    if page.page_image:
        lines.append(f"<!-- 页面 {page.page_num} 包含复杂图形，已渲染为图片 -->")
        lines.append(f"![页面 {page.page_num}]({images_subdir}/{page.page_image})")
        lines.append("")
    
    # 转换文本块
    for block in page.text_blocks:
        block_md = _convert_text_block(block)
        if block_md:
            lines.append(block_md)
            lines.append("")
    
    # 插入提取的图片
    if page.images and not page.page_image:
        for img in page.images:
            img_filename = img.get_filename(base_name)
            # URL编码图片文件名，处理中文和特殊字符
            encoded_filename = quote(img_filename)
            alt_text = f"图片 {img.page_num}-{img.image_index}"
            if img.width and img.height:
                alt_text += f" ({img.width}x{img.height})"
            lines.append(f"![{alt_text}]({images_subdir}/{encoded_filename})")
            lines.append("")
    
    # 页面分隔
    if page.page_num < 100:  # 避免太多分隔线
        lines.append(f"<!-- 第 {page.page_num} 页结束 -->")
        lines.append("")
    
    return "\n".join(lines)


def _convert_text_block(block: Dict[str, Any]) -> str:
    """转换单个文本块为Markdown"""
    block_type = block.get("type", "paragraph")
    content = block.get("content", "").strip()
    
    if not content:
        return ""
    
    # 清理内容
    content = _clean_content(content)
    
    converters = {
        "heading1": lambda c: f"## {_get_first_line(c)}",  # 文档标题已用#，这里用##
        "heading2": lambda c: f"### {_get_first_line(c)}",
        "heading3": lambda c: f"#### {_get_first_line(c)}",
        "list_item": lambda c: _convert_list_items(c),
        "numbered_list": lambda c: _convert_numbered_list(c),
        "code_block": lambda c: _convert_code_block(c),
        "blockquote": lambda c: _convert_blockquote(c),
        "paragraph": lambda c: _convert_paragraph(c),
    }
    
    converter = converters.get(block_type, converters["paragraph"])
    return converter(content)


def _convert_code_block(content: str) -> str:
    """转换代码块"""
    return f"```\n{content}\n```"


def _convert_blockquote(content: str) -> str:
    """转换引用块"""
    lines = content.split("\n")
    quoted_lines = []
    for line in lines:
        # 移除原有的引用符号
        line = line.lstrip(">》「『 ")
        quoted_lines.append(f"> {line}")
    return "\n".join(quoted_lines)


def _convert_paragraph(content: str) -> str:
    """转换段落，检测数学公式"""
    import re
    
    # 检测行内数学公式（简单启发式）
    # 例如：x^2, E=mc^2, ∑, ∫, α, β 等
    math_patterns = [
        (r'\^(\d+|\{[^}]+\})', r'$^{\1}$'),  # 上标
        (r'_(\d+|\{[^}]+\})', r'$_{\1}$'),   # 下标
    ]
    
    for pattern, replacement in math_patterns:
        content = re.sub(pattern, replacement, content)
    
    return content


def _clean_content(content: str) -> str:
    """清理文本内容"""
    # 移除多余空行
    lines = content.split("\n")
    cleaned_lines = []
    prev_empty = False
    
    for line in lines:
        line = line.rstrip()
        is_empty = not line.strip()
        
        if is_empty:
            if not prev_empty:
                cleaned_lines.append("")
            prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
    
    return "\n".join(cleaned_lines)


def _get_first_line(content: str) -> str:
    """获取第一行作为标题"""
    lines = content.split("\n")
    return lines[0].strip() if lines else content


def _convert_list_items(content: str) -> str:
    """转换列表项"""
    lines = content.split("\n")
    result = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 移除原有的列表符号
        for prefix in ["•", "·", "-", "*", "●", "○", "■", "□"]:
            if line.startswith(prefix):
                line = line[len(prefix):].strip()
                break
        
        result.append(f"- {line}")
    
    return "\n".join(result)


def _convert_numbered_list(content: str) -> str:
    """转换编号列表"""
    lines = content.split("\n")
    result = []
    counter = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 移除原有的编号
        import re
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        
        result.append(f"{counter}. {line}")
        counter += 1
    
    return "\n".join(result)


# 兼容旧API
def convert_blocks_to_markdown(blocks: List[Dict[str, Any]]) -> str:
    """将内容块列表转换为Markdown文本（兼容旧API）"""
    lines = []
    
    for block in blocks:
        block_md = _convert_text_block(block)
        if block_md:
            lines.append(block_md)
    
    return "\n\n".join(lines)
