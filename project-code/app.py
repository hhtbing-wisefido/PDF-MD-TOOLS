"""
📄 PDF-MD-TOOLS 桌面应用

Windows桌面应用，批量将PDF转换为Markdown
- 深度提取PDF内容（文本+嵌入图片）
- 语义化Markdown（标题层级、列表、表格、公式）
- 左右分栏显示源PDF和生成MD文件
- 实时日志和转换统计
- 启动时检查老进程
- 支持覆盖模式重新转换
- 多线程加速转换
"""

# ========== 版本信息 ==========
APP_VERSION = "1.1.1"
APP_BUILD_DATE = "2025-12-10"

import os
import sys
import json
import hashlib
import threading
import subprocess
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk


# ========== 进程检查 ==========
APP_NAME = "PDF-MD-TOOLS"
LOCK_FILE = Path(os.environ.get('TEMP', '.')) / "pdf_md_tools.lock"


def check_existing_process() -> bool:
    """检查是否有老进程存在"""
    if not LOCK_FILE.exists():
        return False
    
    try:
        with open(LOCK_FILE, 'r') as f:
            old_pid = int(f.read().strip())
        
        # 检查进程是否存在
        result = subprocess.run(
            ['tasklist', '/FI', f'PID eq {old_pid}', '/NH'],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        return 'python' in result.stdout.lower() or 'pdf' in result.stdout.lower()
    except:
        return False


def kill_existing_process() -> bool:
    """关闭老进程"""
    if not LOCK_FILE.exists():
        return True
    
    try:
        with open(LOCK_FILE, 'r') as f:
            old_pid = int(f.read().strip())
        
        subprocess.run(['taskkill', '/F', '/PID', str(old_pid)], 
                      capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        LOCK_FILE.unlink(missing_ok=True)
        return True
    except:
        return False


def create_lock_file():
    """创建锁文件"""
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))


def remove_lock_file():
    """删除锁文件"""
    LOCK_FILE.unlink(missing_ok=True)

# 导入PDF处理模块
from pdf_parser.extractor import extract_pdf_content, PDFContent
from md_generator.converter import convert_to_markdown


class ConvertStatus(Enum):
    """转换状态"""
    PENDING = "待转换"
    CONVERTING = "转换中"
    COMPLETED = "已完成"
    ERROR = "错误"
    SKIPPED = "已跳过"


@dataclass
class FileItem:
    """文件项"""
    pdf_path: Path
    pdf_name: str
    md_name: str
    size: int
    status: ConvertStatus = ConvertStatus.PENDING
    progress: int = 0
    error_msg: str = ""
    images_count: int = 0
    
    def get_hash(self) -> str:
        """获取文件哈希"""
        md5 = hashlib.md5()
        md5.update(str(self.pdf_path).encode())
        md5.update(str(self.size).encode())
        return md5.hexdigest()[:16]


class ConversionState:
    """转换状态管理（断点续传）"""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.converted: Dict[str, str] = {}
        self.load()
    
    def load(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.converted = json.load(f)
            except:
                self.converted = {}
    
    def save(self):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.converted, f, ensure_ascii=False, indent=2)
    
    def is_converted(self, file_hash: str) -> bool:
        return file_hash in self.converted
    
    def mark_converted(self, file_hash: str, output_path: str):
        self.converted[file_hash] = output_path
        self.save()


class PDFtoMDApp(ctk.CTk):
    """PDF转MD桌面应用 - 左右分栏布局"""
    
    def __init__(self):
        super().__init__()
        
        self.title(f"📄 PDF-MD-TOOLS v{APP_VERSION} - PDF转Markdown工具")
        self.geometry("1300x900")
        self.minsize(1100, 700)
        
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        self.source_dir: Optional[Path] = None
        self.target_dir: Optional[Path] = None
        self.file_items: List[FileItem] = []
        self.is_converting = False
        self.should_stop = False
        self.conversion_state: Optional[ConversionState] = None
        
        self.pdf_rows: List[Dict] = []
        self.md_rows: List[Dict] = []
        self.log_messages: List[str] = []
        
        # 转换选项
        self.extract_images = True  # 提取嵌入图片
        self.image_dpi = 150
        self.overwrite_mode = False  # 覆盖模式
        self.max_workers = min(4, os.cpu_count() or 2)  # 并行线程数
        
        self._create_ui()
        
        # 窗口关闭时删除锁文件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_ui(self):
        """创建用户界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=0)
        
        self._create_top_frame()
        self._create_main_frame()
        self._create_result_frame()
        self._create_log_frame()
        self._create_status_bar()
    
    def _create_top_frame(self):
        """创建顶部区域"""
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(4, weight=1)
        
        # 目录选择行
        ctk.CTkLabel(top_frame, text="📁 源目录:", font=("", 13, "bold")).grid(
            row=0, column=0, padx=10, pady=8, sticky="w"
        )
        self.source_entry = ctk.CTkEntry(top_frame, placeholder_text="选择包含PDF的目录...", width=300)
        self.source_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        ctk.CTkButton(top_frame, text="浏览", width=70, command=self._select_source_dir).grid(
            row=0, column=2, padx=5, pady=8
        )
        
        ctk.CTkLabel(top_frame, text="📂 目标目录:", font=("", 13, "bold")).grid(
            row=0, column=3, padx=(20, 10), pady=8, sticky="w"
        )
        self.target_entry = ctk.CTkEntry(top_frame, placeholder_text="选择输出目录...", width=300)
        self.target_entry.grid(row=0, column=4, padx=5, pady=8, sticky="ew")
        ctk.CTkButton(top_frame, text="浏览", width=70, command=self._select_target_dir).grid(
            row=0, column=5, padx=5, pady=8
        )
        ctk.CTkButton(top_frame, text="📁 打开", width=70, command=self._open_target_dir,
                      fg_color="#6b7280").grid(row=0, column=6, padx=5, pady=8)
        
        # 控制按钮行
        ctrl_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        ctrl_frame.grid(row=1, column=0, columnspan=6, pady=5)
        
        self.scan_btn = ctk.CTkButton(
            ctrl_frame, text="🔍 扫描PDF", width=120,
            command=self._scan_files, fg_color="#2563eb"
        )
        self.scan_btn.pack(side="left", padx=10)
        
        self.convert_btn = ctk.CTkButton(
            ctrl_frame, text="▶️ 开始转换", width=120,
            command=self._start_conversion, fg_color="#16a34a", state="disabled"
        )
        self.convert_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(
            ctrl_frame, text="⏹️ 停止", width=100,
            command=self._stop_conversion, fg_color="#dc2626", state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10)
        
        self.clear_btn = ctk.CTkButton(
            ctrl_frame, text="🗑️ 清空", width=100,
            command=self._clear_list, fg_color="#6b7280"
        )
        self.clear_btn.pack(side="left", padx=10)
        
        # 选项
        self.extract_images_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            ctrl_frame, text="提取嵌入图片", variable=self.extract_images_var,
            command=self._update_options
        ).pack(side="left", padx=15)
        
        self.overwrite_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            ctrl_frame, text="覆盖已有文件", variable=self.overwrite_var,
            command=self._update_options, text_color="#ef4444"
        ).pack(side="left", padx=10)
        
        # 版本标签
        version_label = ctk.CTkLabel(
            ctrl_frame, text=f"v{APP_VERSION}", font=("", 10), text_color="#6b7280"
        )
        version_label.pack(side="left", padx=10)
        
        self.stats_label = ctk.CTkLabel(
            ctrl_frame, text="文件: 0 | 待转换: 0 | 已完成: 0 | 错误: 0", font=("", 12)
        )
        self.stats_label.pack(side="right", padx=20)
    
    def _update_options(self):
        """更新转换选项"""
        self.extract_images = self.extract_images_var.get()
        self.overwrite_mode = self.overwrite_var.get()
        
        if self.overwrite_mode:
            self._log("⚠️ 覆盖模式已启用，将重新转换所有文件", "WARNING")
    
    def _create_main_frame(self):
        """创建左右分栏主区域"""
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        left_label = ctk.CTkLabel(main_frame, text="📄 源PDF文件", font=("", 14, "bold"))
        left_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.pdf_frame = ctk.CTkScrollableFrame(main_frame)
        self.pdf_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.pdf_frame.grid_columnconfigure(0, weight=1)
        
        self._create_list_header(self.pdf_frame, "PDF")
        
        right_label = ctk.CTkLabel(main_frame, text="📝 生成MD文件", font=("", 14, "bold"))
        right_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        self.md_frame = ctk.CTkScrollableFrame(main_frame)
        self.md_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.md_frame.grid_columnconfigure(0, weight=1)
        
        self._create_list_header(self.md_frame, "MD")
    
    def _create_list_header(self, parent, file_type: str):
        """创建列表表头"""
        header = ctk.CTkFrame(parent, fg_color=("#e5e7eb", "#374151"), corner_radius=5)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header, text="#", width=40, font=("", 11, "bold")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(header, text=f"{file_type}文件名", font=("", 11, "bold"), anchor="w").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header, text="状态", width=70, font=("", 11, "bold")).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(header, text="进度", width=100, font=("", 11, "bold")).grid(row=0, column=3, padx=5, pady=5)
    
    def _create_result_frame(self):
        """创建转换结果详情栏"""
        result_frame = ctk.CTkFrame(self, height=80)
        result_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        result_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        ctk.CTkLabel(result_frame, text="📊 转换结果", font=("", 13, "bold")).grid(
            row=0, column=0, columnspan=5, padx=10, pady=5, sticky="w"
        )
        
        # 成功
        success_frame = ctk.CTkFrame(result_frame, fg_color=("#dcfce7", "#166534"))
        success_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(success_frame, text="✅ 成功", font=("", 11, "bold")).pack(side="left", padx=10, pady=5)
        self.success_count_label = ctk.CTkLabel(success_frame, text="0", font=("", 14, "bold"))
        self.success_count_label.pack(side="right", padx=10, pady=5)
        
        # 跳过
        skip_frame = ctk.CTkFrame(result_frame, fg_color=("#f3e8ff", "#581c87"))
        skip_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(skip_frame, text="⏭️ 跳过", font=("", 11, "bold")).pack(side="left", padx=10, pady=5)
        self.skip_count_label = ctk.CTkLabel(skip_frame, text="0", font=("", 14, "bold"))
        self.skip_count_label.pack(side="right", padx=10, pady=5)
        
        # 错误
        error_frame = ctk.CTkFrame(result_frame, fg_color=("#fee2e2", "#991b1b"))
        error_frame.grid(row=1, column=2, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(error_frame, text="❌ 错误", font=("", 11, "bold")).pack(side="left", padx=10, pady=5)
        self.error_count_label = ctk.CTkLabel(error_frame, text="0", font=("", 14, "bold"))
        self.error_count_label.pack(side="right", padx=10, pady=5)
        
        # 待处理
        pending_frame = ctk.CTkFrame(result_frame, fg_color=("#f3f4f6", "#374151"))
        pending_frame.grid(row=1, column=3, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(pending_frame, text="⏳ 待处理", font=("", 11, "bold")).pack(side="left", padx=10, pady=5)
        self.pending_count_label = ctk.CTkLabel(pending_frame, text="0", font=("", 14, "bold"))
        self.pending_count_label.pack(side="right", padx=10, pady=5)
        
        # 提取图片数
        images_frame = ctk.CTkFrame(result_frame, fg_color=("#dbeafe", "#1e40af"))
        images_frame.grid(row=1, column=4, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(images_frame, text="🖼️ 图片", font=("", 11, "bold")).pack(side="left", padx=10, pady=5)
        self.images_count_label = ctk.CTkLabel(images_frame, text="0", font=("", 14, "bold"))
        self.images_count_label.pack(side="right", padx=10, pady=5)
    
    def _create_log_frame(self):
        """创建实时日志区域"""
        log_container = ctk.CTkFrame(self)
        log_container.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(1, weight=1)
        
        title_frame = ctk.CTkFrame(log_container, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(title_frame, text="📋 实时日志", font=("", 13, "bold")).pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(
            title_frame, text="📥 导出日志", width=100, height=28,
            command=self._export_log, fg_color="#6b7280"
        )
        export_btn.pack(side="right", padx=5)
        
        copy_btn = ctk.CTkButton(
            title_frame, text="📋 复制", width=80, height=28,
            command=self._copy_log, fg_color="#6b7280"
        )
        copy_btn.pack(side="right", padx=5)
        
        clear_log_btn = ctk.CTkButton(
            title_frame, text="🗑️ 清空", width=80, height=28,
            command=self._clear_log, fg_color="#6b7280"
        )
        clear_log_btn.pack(side="right", padx=5)
        
        log_frame = ctk.CTkFrame(log_container)
        log_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(
            log_frame, height=8, wrap=tk.WORD,
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            font=("Consolas", 10), relief="flat", padx=10, pady=10
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ctk.CTkScrollbar(log_frame, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_frame = ctk.CTkFrame(self, height=50)
        status_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        
        progress_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(progress_frame, text="总进度:", font=("", 12, "bold")).pack(side="left", padx=5)
        
        self.total_progress = ctk.CTkProgressBar(progress_frame, width=500)
        self.total_progress.pack(side="left", padx=10, fill="x", expand=True)
        self.total_progress.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="0%", font=("", 12, "bold"), width=50)
        self.progress_label.pack(side="left", padx=10)
        
        self.status_label = ctk.CTkLabel(
            progress_frame, text="💡 请选择源目录和目标目录，然后点击扫描",
            font=("", 11), text_color="#9ca3af"
        )
        self.status_label.pack(side="right", padx=10)
    
    def _log(self, message: str, level: str = "INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "DEBUG": "🔧"}
        icon = level_icons.get(level, "ℹ️")
        log_line = f"[{timestamp}] {icon} {message}\n"
        
        self.log_messages.append(log_line)
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def _copy_log(self):
        """复制日志到剪贴板"""
        self.log_text.configure(state=tk.NORMAL)
        content = self.log_text.get("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.clipboard_clear()
        self.clipboard_append(content)
        self._log("日志已复制到剪贴板", "SUCCESS")
    
    def _export_log(self):
        """导出日志到文件"""
        file_path = filedialog.asksaveasfilename(
            title="导出日志", defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("日志文件", "*.log")],
            initialfilename=f"pdf_md_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if file_path:
            self.log_text.configure(state=tk.NORMAL)
            content = self.log_text.get("1.0", tk.END)
            self.log_text.configure(state=tk.DISABLED)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._log(f"日志已导出到: {file_path}", "SUCCESS")
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.log_messages.clear()
    
    def _select_source_dir(self):
        """选择源目录"""
        dir_path = filedialog.askdirectory(title="选择包含PDF文件的目录")
        if dir_path:
            self.source_dir = Path(dir_path)
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, dir_path)
            self._update_status("✅ 已选择源目录")
            self._log(f"选择源目录: {dir_path}", "INFO")
    
    def _select_target_dir(self):
        """选择目标目录"""
        dir_path = filedialog.askdirectory(title="选择或新建输出目录")
        if dir_path:
            self.target_dir = Path(dir_path)
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, dir_path)
            state_file = self.target_dir / ".conversion_state.json"
            self.conversion_state = ConversionState(state_file)
            self._update_status("✅ 已选择目标目录")
            self._log(f"选择目标目录: {dir_path}", "INFO")
    
    def _open_target_dir(self):
        """打开目标目录"""
        if not self.target_dir:
            messagebox.showwarning("警告", "请先选择目标目录")
            return
        if not self.target_dir.exists():
            messagebox.showwarning("警告", "目标目录不存在")
            return
        
        # Windows下使用explorer打开目录
        os.startfile(str(self.target_dir))
        self._log(f"打开目标目录: {self.target_dir}", "INFO")
    
    def _scan_files(self):
        """扫描PDF文件"""
        if not self.source_dir:
            messagebox.showwarning("警告", "请先选择源目录")
            return
        if not self.source_dir.exists():
            messagebox.showerror("错误", "源目录不存在")
            return
        
        self.scan_btn.configure(state="disabled", text="🔄 扫描中...")
        self._update_status("🔍 正在扫描PDF文件...")
        self._clear_list()
        self._log("开始扫描PDF文件...", "INFO")
        
        thread = threading.Thread(target=self._scan_thread, daemon=True)
        thread.start()
    
    def _scan_thread(self):
        """扫描线程"""
        try:
            pdf_paths = list(self.source_dir.rglob("*.pdf"))
            skipped = 0
            
            for path in pdf_paths:
                try:
                    if not path.exists():
                        skipped += 1
                        continue
                    file_size = path.stat().st_size
                    file_item = FileItem(
                        pdf_path=path, pdf_name=path.name,
                        md_name=path.stem + ".md", size=file_size
                    )
                    if self.conversion_state and self.conversion_state.is_converted(file_item.get_hash()):
                        file_item.status = ConvertStatus.SKIPPED
                        file_item.progress = 100
                    self.file_items.append(file_item)
                    self.after(0, lambda f=file_item: self._add_file_row(f))
                except (OSError, PermissionError):
                    skipped += 1
                    continue
            
            if skipped > 0:
                self.after(0, lambda c=skipped: self._log(f"跳过 {c} 个无法访问的文件", "WARNING"))
            self.after(0, self._scan_finished)
        except Exception as e:
            self.after(0, lambda err=str(e): self._log(f"扫描错误: {err}", "ERROR"))
            self.after(0, lambda: self.scan_btn.configure(state="normal", text="🔍 扫描PDF"))
    
    def _scan_finished(self):
        """扫描完成"""
        self.scan_btn.configure(state="normal", text="🔍 扫描PDF")
        self._update_stats()
        self._update_result_counts()
        
        if self.file_items:
            self.convert_btn.configure(state="normal")
            self._update_status(f"✅ 扫描完成，找到 {len(self.file_items)} 个PDF文件")
            self._log(f"扫描完成，找到 {len(self.file_items)} 个PDF文件", "SUCCESS")
        else:
            self._update_status("⚠️ 未找到PDF文件")
            self._log("未找到PDF文件", "WARNING")
    
    def _add_file_row(self, file_item: FileItem):
        """添加文件行"""
        idx = len(self.pdf_rows)
        
        # PDF列表行
        pdf_row = ctk.CTkFrame(self.pdf_frame, fg_color="transparent")
        pdf_row.grid(row=idx+1, column=0, sticky="ew", pady=1)
        pdf_row.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(pdf_row, text=str(idx+1), width=40, font=("", 11)).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(pdf_row, text=file_item.pdf_name, font=("", 11), anchor="w").grid(row=0, column=1, padx=5, sticky="w")
        pdf_status = ctk.CTkLabel(pdf_row, text=file_item.status.value, width=70, font=("", 10),
                                   text_color=self._get_status_color(file_item.status))
        pdf_status.grid(row=0, column=2, padx=5)
        pdf_progress = ctk.CTkProgressBar(pdf_row, width=80, height=12)
        pdf_progress.grid(row=0, column=3, padx=5)
        pdf_progress.set(file_item.progress / 100)
        
        self.pdf_rows.append({'frame': pdf_row, 'status': pdf_status, 'progress': pdf_progress})
        
        # MD列表行
        md_row = ctk.CTkFrame(self.md_frame, fg_color="transparent")
        md_row.grid(row=idx+1, column=0, sticky="ew", pady=1)
        md_row.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(md_row, text=str(idx+1), width=40, font=("", 11)).grid(row=0, column=0, padx=5)
        initial_color = "#9ca3af" if file_item.status == ConvertStatus.PENDING else "#ffffff"
        md_name_label = ctk.CTkLabel(md_row, text=file_item.md_name, font=("", 11), anchor="w", text_color=initial_color)
        md_name_label.grid(row=0, column=1, padx=5, sticky="w")
        md_status_text = "—" if file_item.status == ConvertStatus.PENDING else file_item.status.value
        md_status = ctk.CTkLabel(md_row, text=md_status_text, width=70, font=("", 10),
                                  text_color=self._get_status_color(file_item.status))
        md_status.grid(row=0, column=2, padx=5)
        md_progress = ctk.CTkProgressBar(md_row, width=80, height=12)
        md_progress.grid(row=0, column=3, padx=5)
        md_progress.set(file_item.progress / 100)
        
        self.md_rows.append({'frame': md_row, 'name': md_name_label, 'status': md_status, 'progress': md_progress})
    
    def _update_file_row(self, idx: int, file_item: FileItem):
        """更新文件行"""
        if idx < len(self.pdf_rows):
            self.pdf_rows[idx]['status'].configure(text=file_item.status.value, text_color=self._get_status_color(file_item.status))
            self.pdf_rows[idx]['progress'].set(file_item.progress / 100)
            
            md_color = "#ffffff" if file_item.status != ConvertStatus.PENDING else "#9ca3af"
            self.md_rows[idx]['name'].configure(text_color=md_color)
            self.md_rows[idx]['status'].configure(text=file_item.status.value, text_color=self._get_status_color(file_item.status))
            self.md_rows[idx]['progress'].set(file_item.progress / 100)
    
    def _get_status_color(self, status: ConvertStatus) -> str:
        """获取状态颜色"""
        return {
            ConvertStatus.PENDING: "#9ca3af", ConvertStatus.CONVERTING: "#3b82f6",
            ConvertStatus.COMPLETED: "#22c55e", ConvertStatus.ERROR: "#ef4444",
            ConvertStatus.SKIPPED: "#a855f7"
        }.get(status, "#9ca3af")
    
    def _update_stats(self):
        """更新统计"""
        total = len(self.file_items)
        completed = sum(1 for f in self.file_items if f.status == ConvertStatus.COMPLETED)
        skipped = sum(1 for f in self.file_items if f.status == ConvertStatus.SKIPPED)
        errors = sum(1 for f in self.file_items if f.status == ConvertStatus.ERROR)
        pending = sum(1 for f in self.file_items if f.status == ConvertStatus.PENDING)
        
        self.stats_label.configure(text=f"文件: {total} | 待转换: {pending} | 已完成: {completed + skipped} | 错误: {errors}")
        if total > 0:
            self.total_progress.set((completed + skipped) / total)
            self.progress_label.configure(text=f"{int((completed + skipped) / total * 100)}%")
    
    def _update_result_counts(self):
        """更新结果统计"""
        completed = sum(1 for f in self.file_items if f.status == ConvertStatus.COMPLETED)
        skipped = sum(1 for f in self.file_items if f.status == ConvertStatus.SKIPPED)
        errors = sum(1 for f in self.file_items if f.status == ConvertStatus.ERROR)
        pending = sum(1 for f in self.file_items if f.status == ConvertStatus.PENDING)
        total_images = sum(f.images_count for f in self.file_items)
        
        self.success_count_label.configure(text=str(completed))
        self.skip_count_label.configure(text=str(skipped))
        self.error_count_label.configure(text=str(errors))
        self.pending_count_label.configure(text=str(pending))
        self.images_count_label.configure(text=str(total_images))
    
    def _update_status(self, message: str):
        """更新状态"""
        self.status_label.configure(text=message)
    
    def _start_conversion(self):
        """开始转换"""
        if not self.target_dir:
            messagebox.showwarning("警告", "请先选择目标目录")
            return
        
        self.target_dir.mkdir(parents=True, exist_ok=True)
        if not self.conversion_state:
            self.conversion_state = ConversionState(self.target_dir / ".conversion_state.json")
        
        self.is_converting = True
        self.should_stop = False
        self.convert_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.scan_btn.configure(state="disabled")
        
        self._update_status("🔄 正在转换...")
        self._log("开始转换（深度提取：文本+图片+图表）...", "INFO")
        
        thread = threading.Thread(target=self._conversion_thread, daemon=True)
        thread.start()
    
    def _conversion_thread(self):
        """转换线程"""
        for idx, file_item in enumerate(self.file_items):
            if self.should_stop:
                self.after(0, lambda: self._update_status("⏹️ 转换已停止"))
                self.after(0, lambda: self._log("用户停止转换", "WARNING"))
                break
            
            if file_item.status in [ConvertStatus.COMPLETED, ConvertStatus.SKIPPED]:
                # 覆盖模式下重置状态
                if self.overwrite_mode:
                    file_item.status = ConvertStatus.PENDING
                    file_item.progress = 0
                else:
                    continue
            
            file_hash = file_item.get_hash()
            # 覆盖模式下不跳过已转换文件
            if not self.overwrite_mode and self.conversion_state and self.conversion_state.is_converted(file_hash):
                file_item.status = ConvertStatus.SKIPPED
                file_item.progress = 100
                self.after(0, lambda i=idx, f=file_item: self._update_file_row(i, f))
                self.after(0, self._update_stats)
                self.after(0, self._update_result_counts)
                self.after(0, lambda name=file_item.pdf_name: self._log(f"跳过已转换: {name}", "INFO"))
                continue
            
            file_item.status = ConvertStatus.CONVERTING
            file_item.progress = 10
            self.after(0, lambda i=idx, f=file_item: self._update_file_row(i, f))
            self.after(0, lambda name=file_item.pdf_name: self._log(f"开始转换: {name}", "INFO"))
            
            try:
                images_count = self._convert_single_pdf(file_item, idx)
                file_item.status = ConvertStatus.COMPLETED
                file_item.progress = 100
                file_item.images_count = images_count
                
                if self.conversion_state:
                    self.conversion_state.mark_converted(file_hash, str(self.target_dir / file_item.md_name))
                
                self.after(0, lambda name=file_item.pdf_name, md=file_item.md_name, imgs=images_count:
                          self._log(f"转换成功: {name} → {md} ({imgs}张图片)", "SUCCESS"))
            except Exception as e:
                file_item.status = ConvertStatus.ERROR
                file_item.error_msg = str(e)
                self.after(0, lambda name=file_item.pdf_name, err=str(e): self._log(f"转换失败: {name} - {err}", "ERROR"))
                self.should_stop = True
                self.after(0, lambda msg=str(e), name=file_item.pdf_name:
                          messagebox.showerror("转换错误", f"文件: {name}\n错误: {msg}"))
            
            self.after(0, lambda i=idx, f=file_item: self._update_file_row(i, f))
            self.after(0, self._update_stats)
            self.after(0, self._update_result_counts)
        
        self.is_converting = False
        self.after(0, self._conversion_finished)
    
    def _convert_single_pdf(self, file_item: FileItem, idx: int) -> int:
        """转换单个PDF，返回图片数量"""
        file_item.progress = 20
        self.after(0, lambda i=idx, f=file_item: self._update_file_row(i, f))
        
        # 深度提取PDF（只提取嵌入图片，不渲染整页）
        pdf_content = extract_pdf_content(
            pdf_path=file_item.pdf_path,
            output_dir=self.target_dir,
            extract_images=self.extract_images,
            image_dpi=self.image_dpi
        )
        
        file_item.progress = 60
        self.after(0, lambda i=idx, f=file_item: self._update_file_row(i, f))
        
        # 转换为Markdown
        markdown = convert_to_markdown(pdf_content, file_item.pdf_path, "images")
        
        file_item.progress = 80
        self.after(0, lambda i=idx, f=file_item: self._update_file_row(i, f))
        
        # 保存文件（覆盖模式直接覆盖）
        output_path = self.target_dir / file_item.md_name
        if not self.overwrite_mode:
            counter = 1
            base_name = file_item.pdf_path.stem
            while output_path.exists():
                file_item.md_name = f"{base_name}_{counter}.md"
                output_path = self.target_dir / file_item.md_name
                counter += 1
        
        output_path.write_text(markdown, encoding='utf-8')
        return pdf_content.total_images
    
    def _conversion_finished(self):
        """转换完成"""
        self.convert_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.scan_btn.configure(state="normal")
        
        errors = sum(1 for f in self.file_items if f.status == ConvertStatus.ERROR)
        completed = sum(1 for f in self.file_items if f.status == ConvertStatus.COMPLETED)
        skipped = sum(1 for f in self.file_items if f.status == ConvertStatus.SKIPPED)
        total_images = sum(f.images_count for f in self.file_items)
        
        if errors > 0:
            self._update_status(f"⚠️ 转换完成，{errors} 个文件出错")
            self._log(f"转换完成，{errors} 个文件出错", "WARNING")
        else:
            msg = f"转换完成！成功 {completed}，跳过 {skipped}，共提取 {total_images} 张图片"
            self._update_status(f"✅ {msg}")
            self._log(msg, "SUCCESS")
    
    def _stop_conversion(self):
        """停止转换"""
        self.should_stop = True
        self._update_status("⏳ 正在停止...")
        self._log("正在停止转换...", "WARNING")
    
    def _clear_list(self):
        """清空列表"""
        for row in self.pdf_rows:
            row['frame'].destroy()
        for row in self.md_rows:
            row['frame'].destroy()
        
        self.pdf_rows.clear()
        self.md_rows.clear()
        self.file_items.clear()
        
        self._update_stats()
        self._update_result_counts()
        self.convert_btn.configure(state="disabled")
        self.total_progress.set(0)
        self.progress_label.configure(text="0%")
    
    def _on_closing(self):
        """窗口关闭时的处理"""
        if self.is_converting:
            if not messagebox.askyesno("确认", "转换正在进行中，确定要退出吗？"):
                return
            self.should_stop = True
        
        remove_lock_file()
        self.destroy()


def main():
    """主函数"""
    # 检查是否有老进程
    if check_existing_process():
        root = tk.Tk()
        root.withdraw()
        
        result = messagebox.askyesnocancel(
            "检测到老进程",
            "检测到 PDF-MD-TOOLS 已在运行。\n\n"
            "• 点击【是】关闭老进程并启动新窗口\n"
            "• 点击【否】直接启动新窗口（可能冲突）\n"
            "• 点击【取消】退出",
            icon='warning'
        )
        
        root.destroy()
        
        if result is None:  # 取消
            sys.exit(0)
        elif result:  # 是 - 关闭老进程
            kill_existing_process()
    
    # 创建锁文件
    create_lock_file()
    
    try:
        app = PDFtoMDApp()
        app.mainloop()
    finally:
        remove_lock_file()


if __name__ == "__main__":
    main()
