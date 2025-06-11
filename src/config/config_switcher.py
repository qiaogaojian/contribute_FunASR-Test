#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR配置切换工具
快速切换不同的语音识别配置
"""

import os
import sys
from src.config.asr_config import list_configs, get_config

def modify_asr_config(config_name):
    """修改ASR脚本中的配置"""
    asr_file_path = "src/asr/streaming_paraformer.py"
    
    if not os.path.exists(asr_file_path):
        print(f"错误: 找不到ASR文件 {asr_file_path}")
        return False
    
    # 读取文件内容
    with open(asr_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找配置行
    config_line_start = 'CONFIG_NAME = "'
    config_line_end = '"  # 可选:'
    
    start_pos = content.find(config_line_start)
    if start_pos == -1:
        print("错误: 找不到配置行")
        return False
    
    end_pos = content.find(config_line_end, start_pos)
    if end_pos == -1:
        print("错误: 配置行格式不正确")
        return False
    
    # 替换配置
    new_config_line = f'CONFIG_NAME = "{config_name}"  # 可选:'
    new_content = content[:start_pos] + new_config_line + content[end_pos + len(config_line_end):]
    
    # 写回文件
    with open(asr_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 配置已切换为: {config_name}")
    return True

def show_current_config():
    """显示当前配置"""
    asr_file_path = "src/asr/streaming_paraformer.py"
    
    if not os.path.exists(asr_file_path):
        print(f"错误: 找不到ASR文件 {asr_file_path}")
        return None
    
    with open(asr_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    config_line_start = 'CONFIG_NAME = "'
    config_line_end = '"'
    
    start_pos = content.find(config_line_start)
    if start_pos == -1:
        return None
    
    start_pos += len(config_line_start)
    end_pos = content.find(config_line_end, start_pos)
    if end_pos == -1:
        return None
    
    return content[start_pos:end_pos]

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 FunASR 配置切换工具")
    print("=" * 60)
    
    # 显示当前配置
    current_config = show_current_config()
    if current_config:
        config_info = get_config(current_config)
        print(f"当前配置: {current_config}")
        print(f"配置说明: {config_info.get('description', '无说明')}")
    else:
        print("无法获取当前配置")
    
    print("\n" + "=" * 60)
    
    # 显示所有可用配置
    print("可用配置:")
    list_configs()
    
    print("\n" + "=" * 60)
    
    # 用户选择
    while True:
        choice = input("\n请选择配置 (输入配置名称，或 'q' 退出): ").strip().lower()
        
        if choice == 'q':
            print("退出配置工具")
            break
        
        # 验证配置是否存在
        try:
            config_info = get_config(choice)
            if config_info:
                print(f"\n选择的配置: {choice}")
                print(f"配置说明: {config_info.get('description', '无说明')}")
                print(f"VAD配置: {config_info['vad_config']}")
                print(f"Chunk大小: {config_info['chunk_size']}")
                print(f"预测间隔: {config_info['prediction_interval']}")
                
                confirm = input("\n确认切换到此配置? (y/n): ").strip().lower()
                if confirm in ['y', 'yes', '是']:
                    if modify_asr_config(choice):
                        print("\n🎉 配置切换成功!")
                        print("请重新启动ASR服务以应用新配置")
                        break
                    else:
                        print("❌ 配置切换失败")
                else:
                    print("取消切换")
            else:
                print(f"❌ 无效的配置名称: {choice}")
        except Exception as e:
            print(f"❌ 错误: {e}")

def quick_switch(config_name):
    """快速切换配置（命令行参数）"""
    if modify_asr_config(config_name):
        config_info = get_config(config_name)
        print(f"配置说明: {config_info.get('description', '无说明')}")
        print("请重新启动ASR服务以应用新配置")
    else:
        print("配置切换失败")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 命令行参数模式
        config_name = sys.argv[1]
        print(f"快速切换到配置: {config_name}")
        quick_switch(config_name)
    else:
        # 交互模式
        main()
