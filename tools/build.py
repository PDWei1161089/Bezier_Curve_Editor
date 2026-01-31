# build.py - 一键打包脚本（适配新的目录结构）
import os
import sys
import shutil
import subprocess
import platform
import json
from datetime import datetime

# 如果build.py需要导入其他模块，确保路径正确
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def get_version():
    """获取版本信息"""
    version_file = os.path.join(current_dir, "docs", "CHANGELOG.md")
    version = "5.0.0"  # 默认版本

    if os.path.exists(version_file):
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('## v'):
                        version = line.split('## v')[1].strip()
                        break
        except:
            pass

    return version


def clean_build_folders():
    """清理之前的打包文件"""
    folders = ['build', 'dist']
    for folder in folders:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"✅ 已清理: {folder}")
            except Exception as e:
                print(f"❌ 清理 {folder} 失败: {e}")


def collect_resource_files():
    """收集所有资源文件（适配新的目录结构）"""
    resource_files = []

    print("📁 收集资源文件...")

    # 1. 收集 resources 文件夹（主要资源）
    if os.path.exists('resources'):
        print("  收集 resources 文件夹...")
        for root, dirs, files in os.walk('resources'):
            for file in files:
                src_path = os.path.join(root, file)
                # 保持完整的相对路径结构
                rel_dir = os.path.relpath(root, '.')
                resource_files.append((src_path, rel_dir))
                print(f"    ✓ 添加: {src_path} -> {rel_dir}")

    # 2. 收集 src 文件夹（Python源代码）
    if os.path.exists('src'):
        print("  收集 src 文件夹...")
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    src_path = os.path.join(root, file)
                    rel_dir = os.path.relpath(root, '.')
                    resource_files.append((src_path, rel_dir))
                    print(f"    ✓ 添加: {src_path} -> {rel_dir}")

    # 3. 收集其他必要的配置文件
    additional_files = [
        'requirements.txt',
        '.env',
        'config.json',
    ]

    print("  收集配置文件...")
    for file in additional_files:
        if os.path.exists(file):
            resource_files.append((file, '.'))
            print(f"    ✓ 添加: {file}")

    # 4. 收集 docs 文件夹中的必要文档
    docs_files = ['README.md', 'user_manual.md']
    docs_folder = 'docs'

    if os.path.exists(docs_folder):
        print("  收集文档文件...")
        for doc_file in docs_files:
            src_path = os.path.join(docs_folder, doc_file)
            if os.path.exists(src_path):
                resource_files.append((src_path, docs_folder))
                print(f"    ✓ 添加: {src_path} -> {docs_folder}")

    print(f"✅ 总计收集到 {len(resource_files)} 个文件")
    return resource_files


def create_spec_file():
    """创建自定义的spec文件"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# 项目信息
app_name = "BezierEditor"
version = "{get_version()}"
description = "贝塞尔曲线编辑器"
author = "Your Name"

# 收集所有资源
datas = []
resources = [
    ('resources', 'resources'),
    ('src', 'src'),
]

# 添加额外的数据文件
for src, dst in resources:
    datas.append((src, dst))

# 隐藏控制台
console = False

# 程序入口
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pygame',
        'numpy',
        'pygame._sdl2',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# 生成单个可执行文件
pyz = PYZ(a.pure)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources/icon.ico'],
)

# 如果需要创建文件夹而不是单文件，使用下面的配置
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name=app_name,
# )
'''

    spec_file = "bezier_editor.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print(f"✅ 已创建 spec 文件: {spec_file}")
    return spec_file


def build_with_spec():
    """使用spec文件构建"""
    spec_file = "bezier_editor.spec"

    if not os.path.exists(spec_file):
        create_spec_file()

    cmd = ['pyinstaller', '--clean', '--noconfirm', spec_file]

    print("执行打包命令:", ' '.join(cmd))
    print("=" * 60)

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ 使用spec文件打包成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        return False


def build_with_command():
    """使用命令行参数构建"""
    version = get_version()
    app_name = f"BezierEditor_v{version}"

    # 构建资源文件参数
    resources = collect_resource_files()
    add_data_args = []

    for src, dst in resources:
        if platform.system() == 'Windows':
            add_data_args.append(f'--add-data={src};{dst}')
        else:
            add_data_args.append(f'--add-data={src}:{dst}')

    # 构建命令
    cmd = [
        'pyinstaller',
        '--name', app_name,
        '--onefile',  # 单文件模式
        '--windowed',  # 隐藏控制台
        '--clean',
        '--noconfirm',
        '--distpath', 'dist',  # 输出到dist目录
        '--workpath', 'build',  # 工作目录
    ]

    # 添加资源文件
    cmd.extend(add_data_args)

    # 添加图标
    icon_path = 'resources/icon.ico'
    if os.path.exists(icon_path):
        cmd.extend(['--icon', icon_path])
    else:
        print(f"⚠ 图标文件不存在: {icon_path}")

    # 添加隐藏导入
    cmd.extend([
        '--hidden-import', 'pygame',
        '--hidden-import', 'pygame._sdl2',
        '--hidden-import', 'numpy',
    ])

    # 添加主文件
    cmd.append('main.py')

    print("执行打包命令:")
    print(' '.join(cmd))
    print("=" * 60)

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ 打包成功！")
        print(f"程序位置: dist/{app_name}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        return False


def create_release_notes():
    """创建发布说明"""
    version = get_version()
    build_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    platform_info = platform.platform()

    release_notes = f'''# 贝塞尔曲线编辑器 {version} 发布说明

## 版本信息
- 版本号: {version}
- 构建日期: {build_date}
- 目标平台: {platform_info}
- 打包方式: PyInstaller单文件可执行程序

## 系统要求
- 操作系统: Windows 7/8/10/11, macOS 10.14+, Linux
- 内存: 至少2GB RAM
- 存储空间: 至少200MB可用空间

## 新功能
（根据CHANGELOG.md自动生成）

## 使用说明
1. 直接运行 {f"BezierEditor_v{version}.exe"} (Windows)
2. 无需安装Python或其他依赖
3. 所有资源文件已包含在可执行文件中

## 注意事项
- 首次运行可能需要一些时间解压资源
- 确保程序所在目录有写入权限
- 建议在独立文件夹中运行

## 文件结构
├── BezierEditor_v{version}.exe  # 主程序
├── README.md                    # 说明文档
└── user_manual.md              # 用户手册

## 技术支持
如有问题，请查看文档或联系开发者。

---
自动生成于 {build_date}
'''

    notes_file = os.path.join('dist', f'RELEASE_v{version}.md')
    with open(notes_file, 'w', encoding='utf-8') as f:
        f.write(release_notes)

    print(f"✅ 已创建发布说明: {notes_file}")
    return notes_file


def copy_documentation():
    """复制文档文件到dist目录"""
    version = get_version()
    dist_folder = 'dist'

    # 确保dist目录存在
    if not os.path.exists(dist_folder):
        os.makedirs(dist_folder)

    # 要复制的文档文件
    docs_to_copy = {
        'README.md': f'README_v{version}.md',
        'docs/user_manual.md': '用户手册.md',
        'docs/CHANGELOG.md': '更新日志.md',
    }

    for src, dst in docs_to_copy.items():
        if os.path.exists(src):
            try:
                dst_path = os.path.join(dist_folder, dst)
                shutil.copy2(src, dst_path)
                print(f"✅ 已复制文档: {src} -> {dst}")
            except Exception as e:
                print(f"❌ 复制文档失败 {src}: {e}")


def main():
    print("🚀 开始打包贝塞尔曲线编辑器...")
    print("=" * 60)

    version = get_version()
    print(f"当前版本: {version}")
    print(f"项目根目录: {current_dir}")
    print(f"操作系统: {platform.system()} {platform.release()}")

    # 1. 清理旧文件
    print("\n1. 清理旧构建文件...")
    clean_build_folders()

    # 2. 检查必要文件
    print("\n2. 检查必要文件...")
    required_files = ['main.py', 'resources']
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (缺失)")
            print(f"   请确保项目结构正确！")
            sys.exit(1)

    # 3. 选择构建方式
    print("\n3. 选择构建方式:")
    print("   [1] 使用命令行参数构建（推荐）")
    print("   [2] 使用spec文件构建")
    print("   [3] 两种方式都尝试")

    choice = input("   请选择 (1/2/3, 默认1): ").strip() or "1"

    success = False

    if choice in ["1", "3"]:
        print("\n🔨 使用命令行参数构建...")
        success = build_with_command()

        if not success and choice == "3":
            print("\n⚠ 命令行构建失败，尝试spec文件构建...")
            success = build_with_spec()
    elif choice == "2":
        print("\n🔨 使用spec文件构建...")
        success = build_with_spec()
    else:
        print("❌ 无效选择")
        sys.exit(1)

    if success:
        # 4. 创建发布文档
        print("\n4. 创建发布文档...")
        create_release_notes()
        copy_documentation()

        # 5. 显示结果
        print("\n" + "=" * 60)
        print("🎉 打包完成！")
        print("=" * 60)
        print(f"\n📂 输出目录: dist/")
        print(f"📄 主程序: BezierEditor_v{version}.exe")
        print(f"📚 文档: RELEASE_v{version}.md, 用户手册.md, 更新日志.md")

        print("\n📋 下一步:")
        print("  1. 测试 dist/ 目录下的可执行文件")
        print("  2. 使用 tools/package.py 创建安装包（可选）")
        print("  3. 在 docs/ 目录更新版本号")

        # 统计文件大小
        exe_file = os.path.join('dist', f'BezierEditor_v{version}.exe')
        if os.path.exists(exe_file):
            size_mb = os.path.getsize(exe_file) / (1024 * 1024)
            print(f"\n📊 文件大小: {size_mb:.2f} MB")
    else:
        print("\n❌ 打包失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()