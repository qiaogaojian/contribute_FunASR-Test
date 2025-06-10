#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
"""

import sys
import subprocess
from pathlib import Path

def run_test(test_name):
    """运行指定的测试"""
    test_mapping = {
        "frontend": "test.test_frontend",
        "integration": "test.test_integrated_system",
        "optimization": "test.test_asr_optimization"
    }

    if test_name not in test_mapping:
        print(f"❌ 未知的测试: {test_name}")
        print("可用的测试:")
        for name, module in test_mapping.items():
            print(f"  {name}: {module}")
        return

    # 检查Python解释器
    python_exe = Path("./venv/python.exe")
    if not python_exe.exists():
        print("❌ 找不到虚拟环境解释器: ./venv/python.exe")
        return

    try:
        subprocess.run([
            str(python_exe), '-m', test_mapping[test_name]
        ])
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python run_tests.py <test_name>")
        print("")
        print("可用的测试:")
        print("  frontend      - 前端测试")
        print("  integration   - 集成测试")
        print("  optimization  - 优化效果测试")
        return
    
    test_name = sys.argv[1]
    run_test(test_name)

if __name__ == "__main__":
    main()
