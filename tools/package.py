import os
import shutil
import subprocess
from datetime import datetime


def clean_build():
    """清理构建文件"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理: {dir_name}")


def build_exe():
    """使用PyInstaller构建exe"""
    version = datetime.now().strftime("%Y%m%d_%H%M")
    exe_name = f"BezierCurveEditor_v{version}"

    # PyInstaller命令
    cmd = [
        'pyinstaller',
        '--name', exe_name,
        '--icon', 'resources/icon.ico',
        '--windowed',
        '--clean',
        '--noconsole',
        '--add-data', 'resources;resources',
        '--hidden-import', 'pygame',
        '--hidden-import', 'matplotlib',
        '--hidden-import', 'numpy',
        'main.py'
    ]

    print("开始构建...")
    subprocess.run(cmd)

    # 移动exe到dist根目录
    src_exe = os.path.join('dist', exe_name, f'{exe_name}.exe')
    if os.path.exists(src_exe):
        dst_exe = os.path.join('dist', f'{exe_name}.exe')
        shutil.move(src_exe, dst_exe)
        shutil.rmtree(os.path.join('dist', exe_name))
        print(f"构建完成: {dst_exe}")


if __name__ == "__main__":
    clean_build()
    build_exe()