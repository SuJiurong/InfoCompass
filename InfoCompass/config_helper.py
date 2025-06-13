#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoCompass 配置助手
帮助用户快速配置API凭据
"""

import os
import sys


def create_env_file():
    """创建并配置.env文件"""
    print("🧭 InfoCompass 配置助手")
    print("="*50)
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        response = input("⚠️  .env文件已存在，是否覆盖? (y/N): ").strip().lower()
        if response != 'y':
            print("配置取消")
            return
    
    print("\n请提供以下API凭据:")
    print("📱 Telegram API 凭据获取: https://my.telegram.org/apps")
    print("🤖 Gemini API 密钥获取: https://aistudio.google.com/app/apikey")
    print()
    
    # 收集配置信息
    config = {}
    
    # Telegram配置
    config['TELEGRAM_API_ID'] = input("Telegram API ID: ").strip()
    config['TELEGRAM_API_HASH'] = input("Telegram API Hash: ").strip()
    config['TELEGRAM_PHONE'] = input("手机号码 (包含国家代码，如+86): ").strip()
    
    # Gemini配置
    config['GEMINI_API_KEY'] = input("Gemini API Key: ").strip()
    
    # 验证必需字段
    required_fields = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE', 'GEMINI_API_KEY']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        print(f"❌ 以下字段不能为空: {', '.join(missing_fields)}")
        return
    
    # 写入.env文件
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# InfoCompass 环境配置\n")
            f.write("# 由配置助手自动生成\n\n")
            
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        
        print(f"\n✅ 配置文件已创建: {env_file}")
        print("🚀 现在可以运行 InfoCompass 了！")
        
    except Exception as e:
        print(f"❌ 创建配置文件失败: {str(e)}")


def main():
    """主函数"""
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    main()
