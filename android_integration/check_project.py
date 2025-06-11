#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android 项目配置检查脚本
检查项目文件完整性和配置正确性
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (缺失)")
        return False

def check_directory_exists(dir_path, description):
    """检查目录是否存在"""
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} (缺失)")
        return False

def check_android_project():
    """检查 Android 项目完整性"""
    print("🔍 检查 Android 项目配置...")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    all_good = True
    
    # 检查核心项目文件
    core_files = [
        ("app/build.gradle", "应用构建配置"),
        ("app/src/main/AndroidManifest.xml", "应用清单文件"),
        ("build.gradle", "项目构建配置"),
        ("settings.gradle", "项目设置"),
        ("gradle.properties", "Gradle 属性"),
    ]
    
    print("\n📁 核心项目文件:")
    for file_path, desc in core_files:
        full_path = base_path / file_path
        if not check_file_exists(full_path, desc):
            all_good = False
    
    # 检查 Java 源文件
    java_files = [
        ("app/src/main/java/com/example/asrclient/MainActivity.java", "主活动（基础版）"),
        ("app/src/main/java/com/example/asrclient/MainActivityImproved.java", "主活动（改进版）"),
        ("app/src/main/java/com/example/asrclient/ASRManager.java", "ASR 管理器"),
        ("app/src/main/java/com/example/asrclient/ASRWebSocketClient.java", "WebSocket 客户端"),
        ("app/src/main/java/com/example/asrclient/AudioRecordManager.java", "音频录制管理器"),
    ]
    
    print("\n☕ Java 源文件:")
    for file_path, desc in java_files:
        full_path = base_path / file_path
        if not check_file_exists(full_path, desc):
            all_good = False
    
    # 检查布局文件
    layout_files = [
        ("app/src/main/res/layout/activity_main.xml", "主布局（基础版）"),
        ("app/src/main/res/layout/activity_main_improved.xml", "主布局（改进版）"),
    ]
    
    print("\n🎨 布局文件:")
    for file_path, desc in layout_files:
        full_path = base_path / file_path
        if not check_file_exists(full_path, desc):
            all_good = False
    
    # 检查资源文件
    resource_files = [
        ("app/src/main/res/values/strings.xml", "字符串资源"),
        ("app/src/main/res/values/colors.xml", "颜色资源"),
        ("app/src/main/res/values/themes.xml", "主题配置"),
        ("app/src/main/res/values/styles.xml", "样式资源"),
    ]
    
    print("\n🎯 资源文件:")
    for file_path, desc in resource_files:
        full_path = base_path / file_path
        if not check_file_exists(full_path, desc):
            all_good = False
    
    # 检查图标文件
    drawable_files = [
        ("app/src/main/res/drawable/ic_mic.xml", "麦克风图标"),
        ("app/src/main/res/drawable/ic_mic_off.xml", "麦克风关闭图标"),
        ("app/src/main/res/drawable/ic_clear.xml", "清空图标"),
        ("app/src/main/res/drawable/status_background.xml", "状态背景"),
        ("app/src/main/res/drawable/results_background.xml", "结果背景"),
    ]
    
    print("\n🖼️ 图标文件:")
    for file_path, desc in drawable_files:
        full_path = base_path / file_path
        if not check_file_exists(full_path, desc):
            all_good = False
    
    # 检查文档文件
    doc_files = [
        ("README.md", "项目说明"),
        ("USAGE_GUIDE.md", "使用指南"),
    ]
    
    print("\n📚 文档文件:")
    for file_path, desc in doc_files:
        full_path = base_path / file_path
        if not check_file_exists(full_path, desc):
            all_good = False
    
    # 检查目录结构
    directories = [
        ("app/src/main/java/com/example/asrclient", "Java 源码目录"),
        ("app/src/main/res/layout", "布局目录"),
        ("app/src/main/res/values", "资源值目录"),
        ("app/src/main/res/drawable", "图标目录"),
        ("gradle/wrapper", "Gradle 包装器目录"),
    ]
    
    print("\n📂 目录结构:")
    for dir_path, desc in directories:
        full_path = base_path / dir_path
        if not check_directory_exists(full_path, desc):
            all_good = False
    
    # 总结
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 项目配置检查完成！所有文件都存在。")
        print("\n📋 下一步操作:")
        print("1. 在 Android Studio 中打开项目")
        print("2. 修改 ASRManager.java 中的服务器地址")
        print("3. 选择使用的主活动（MainActivity 或 MainActivityImproved）")
        print("4. 编译并运行应用")
        return True
    else:
        print("⚠️ 项目配置检查发现问题！请检查缺失的文件。")
        return False

def check_server_connection():
    """检查服务器连接"""
    print("\n🌐 检查服务器连接...")
    try:
        import requests
        
        # 这里可以添加服务器健康检查
        server_url = "http://192.168.1.100:8000/health"
        print(f"尝试连接服务器: {server_url}")
        
        response = requests.get(server_url, timeout=5)
        if response.status_code == 200:
            print("✅ 服务器连接正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️ 未安装 requests 库，跳过服务器连接检查")
        return None
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        print("💡 请确保:")
        print("   - FastAPI 服务器正在运行")
        print("   - 服务器地址和端口正确")
        print("   - 网络连接正常")
        return False

def main():
    """主函数"""
    print("🚀 Android ASR 客户端项目检查工具")
    print("=" * 50)
    
    # 检查项目配置
    project_ok = check_android_project()
    
    # 检查服务器连接（可选）
    if project_ok:
        server_ok = check_server_connection()
        
        if server_ok is True:
            print("\n🎯 所有检查通过！项目已准备就绪。")
        elif server_ok is False:
            print("\n⚠️ 项目文件正常，但服务器连接有问题。")
        else:
            print("\n✅ 项目文件检查通过。")
    
    print("\n📖 更多信息请查看 USAGE_GUIDE.md")

if __name__ == "__main__":
    main()
