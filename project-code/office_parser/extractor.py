"""
📄 Office文档解析模块

支持的格式:
- Word: .doc, .docx
- PowerPoint: .ppt, .pptx
- Excel: .xls, .xlsx
"""

from .__init__ import (
    extract_office_content,
    office_content_to_markdown,
    OfficeContent,
    ExtractedImage,
    check_dependencies,
    get_supported_extensions,
)

__all__ = [
    "extract_office_content",
    "office_content_to_markdown", 
    "OfficeContent",
    "ExtractedImage",
    "check_dependencies",
    "get_supported_extensions",
]
