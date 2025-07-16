#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
打包脚本 - 将ALE网络运维工具包打包成exe
"""

import os
import subprocess
import sys

def install_requirements():
    """安装打包所需的依赖"""
    print("安装打包依赖...")
    requirements = [
        "pyinstaller",
        "auto-py-to-exe"  # 可选：提供图形界面来配置打包
    ]
    
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✓ {req} 安装成功")
        except subprocess.CalledProcessError:
            print(f"✗ {req} 安装失败")

def create_spec_file():
    """创建PyInstaller配置文件"""

    # 控制台版本spec文件
    console_spec = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ale_inspection.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('template.xlsx', '.'),
        ('.env', '.'),
        ('README.md', '.'),
        ('README_CN.md', '.'),
    ],
    hiddenimports=[
        'openpyxl',
        'pandas',
        'netmiko',
        'paramiko',
        'email',
        'smtplib',
        'ftplib',
        'zipfile'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ALE网络运维工具包-控制台版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''



    with open('ale_console.spec', 'w', encoding='utf-8') as f:
        f.write(console_spec)

    print("✓ 配置文件创建完成:")
    print("  - ale_console.spec (控制台版)")

def build_exe():
    """执行打包"""
    print("开始打包控制台版本...")
    build_console()

def build_console():
    """打包控制台版本"""
    print("打包控制台版本...")
    try:
        subprocess.check_call(["pyinstaller", "ale_console.spec"])
        print("✓ 控制台版打包成功！")
        print("可执行文件: dist/ALE网络运维工具包-控制台版.exe")
    except subprocess.CalledProcessError:
        print("✗ 控制台版打包失败")

def main():
    """主函数"""
    print("ALE网络运维工具包 - 打包脚本")
    print("=" * 50)
    
    # 检查必要文件
    required_files = ['ale_inspection.py', 'template.xlsx', '.env']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("缺少必要文件:")
        for f in missing_files:
            print(f"  - {f}")
        return
    
    # 安装依赖
    install_requirements()
    
    # 创建配置文件
    create_spec_file()
    
    # 执行打包
    build_exe()
    
    print("\n打包完成！")
    print("使用说明:")
    print("1. 将生成的exe文件复制到目标机器")
    print("2. 确保template.xlsx和.env文件在同一目录")
    print("3. 双击运行exe文件或在命令行中执行")

if __name__ == '__main__':
    main()
