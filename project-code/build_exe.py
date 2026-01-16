"""
🔧 PDF-MD-TOOLS 打包脚本

生成Windows可执行文件（.exe）
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 项目信息
APP_NAME = "PDF-MD-TOOLS"
APP_VERSION = "2.0.0"
MAIN_SCRIPT = "app.py"  # 相对于project-code目录

def clean_build():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", f"{APP_NAME}.spec"]
    for d in dirs_to_clean:
        path = Path(d)
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    print("✅ 清理完成")

def build_exe():
    """构建EXE"""
    print(f"🔧 正在构建 {APP_NAME} v{APP_VERSION}...")
    
    # PyInstaller参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",           # 单文件
        "--windowed",          # 无控制台窗口
        "--noconfirm",         # 覆盖已有
        "--clean",             # 清理缓存
        # 添加数据文件（相对于project-code目录）
        "--add-data", "pdf_parser;pdf_parser",
        "--add-data", "md_generator;md_generator",
        "--add-data", "office_parser;office_parser",
        # 隐藏导入（只包含必要的）
        "--hidden-import", "customtkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "fitz",
        "--hidden-import", "pdfplumber",
        "--hidden-import", "pdfminer",
        # Office文档支持
        "--hidden-import", "docx",
        "--hidden-import", "pptx",
        "--hidden-import", "openpyxl",
        "--hidden-import", "win32com",
        "--hidden-import", "win32com.client",
        "--hidden-import", "pythoncom",
        # 排除不必要的大型库
        "--exclude-module", "torch",
        "--exclude-module", "torchvision",
        "--exclude-module", "tensorflow",
        "--exclude-module", "keras",
        "--exclude-module", "pandas",
        "--exclude-module", "numpy.distutils",
        "--exclude-module", "scipy",
        "--exclude-module", "matplotlib",
        "--exclude-module", "IPython",
        "--exclude-module", "notebook",
        "--exclude-module", "jupyter",
        "--exclude-module", "pytest",
        "--exclude-module", "black",
        "--exclude-module", "flake8",
        # 图标（如果有）
        # "--icon", "icon.ico",
        # 主脚本
        MAIN_SCRIPT,
    ]
    
    print(f"📦 执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(Path(__file__).parent))
    
    if result.returncode == 0:
        exe_path = Path("dist") / f"{APP_NAME}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / 1024 / 1024
            print(f"✅ 构建成功!")
            print(f"📁 文件: {exe_path.absolute()}")
            print(f"📊 大小: {size_mb:.1f} MB")
            return True
    
    print("❌ 构建失败")
    return False

def create_release_package():
    """创建发布包"""
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    
    exe_path = Path("dist") / f"{APP_NAME}.exe"
    if not exe_path.exists():
        print("❌ EXE文件不存在，请先构建")
        return False
    
    # 复制EXE
    release_exe = release_dir / f"{APP_NAME}_v{APP_VERSION}.exe"
    shutil.copy(exe_path, release_exe)
    
    # 创建README
    readme_content = f"""# {APP_NAME} v{APP_VERSION}

## 📥 下载说明

直接下载 `{APP_NAME}_v{APP_VERSION}.exe` 即可使用，无需安装Python。

## 🚀 使用方法

1. 双击运行 `{APP_NAME}_v{APP_VERSION}.exe`
2. 选择源目录（包含PDF的文件夹）
3. 选择目标目录（输出MD的文件夹）
4. 点击"扫描PDF"
5. 点击"开始转换"

## ⚠️ 注意事项

- 首次运行可能需要几秒钟加载
- Windows Defender可能会提示，请选择"仍要运行"
- 如遇问题，请以管理员身份运行

## 📋 系统要求

- Windows 10/11 64位
- 无需安装Python

---

发布日期: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
"""
    
    (release_dir / "README.md").write_text(readme_content, encoding='utf-8')
    
    print(f"✅ 发布包创建完成!")
    print(f"📁 目录: {release_dir.absolute()}")
    print(f"📦 文件: {release_exe.name}")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print(f"🔨 {APP_NAME} 构建工具")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_build()
    else:
        clean_build()
        if build_exe():
            create_release_package()
