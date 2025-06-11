#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR配置切换工具入口脚本
"""

import sys
import subprocess
from pathlib import Path

def main():
    """主函数"""
    try:
        # 检查Python解释器
        python_exe = Path("./venv/python.exe")
        if not python_exe.exists():
            print("❌ 找不到虚拟环境解释器: ./venv/python.exe")
            return

        # 使用虚拟环境解释器运行配置切换工具
        if len(sys.argv) > 1:
            # 命令行参数模式
            config_name = sys.argv[1]
            subprocess.run([
                str(python_exe), '-m', 'src.config.config_switcher', config_name
            ])
        else:
            # 交互模式
            subprocess.run([
                str(python_exe), '-m', 'src.config.config_switcher'
            ])
    except Exception as e:
        print(f"❌ 配置切换失败: {e}")

if __name__ == "__main__":
    main()
