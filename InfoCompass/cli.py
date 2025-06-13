#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoCompass CLI 工具
提供命令行接口来运行InfoCompass
"""

import argparse
import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import InfoCompass


async def run_cli():
    """运行CLI版本"""
    parser = argparse.ArgumentParser(
        description="InfoCompass - 获取Telegram频道消息并使用Gemini生成总结",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python cli.py @channelname
  python cli.py @channelname -l 50 -d 3
  python cli.py @channelname --limit 200 --days 7 --prompt "请重点关注技术相关内容"

获取API凭据:
  Telegram: https://my.telegram.org/apps
  Gemini: https://aistudio.google.com/app/apikey
        """
    )    
    parser.add_argument(
        'channel',
        nargs='?',
        help='Telegram频道用户名 (例如: @channelname)，使用 --all-channels 时可省略'
    )
    
    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=100,
        help='获取消息数量限制 (默认: 100)'
    )
    
    parser.add_argument(
        '-d', '--days',
        type=int,
        default=1,
        help='获取多少天前的消息 (默认: 1)'    )
    
    parser.add_argument(
        '-p', '--prompt',
        type=str,
        help='自定义总结提示词'
    )
    
    parser.add_argument(
        '--all-channels',
        action='store_true',
        help='批量处理.env中配置的所有频道'
    )
    
    parser.add_argument(
        '--no-login',
        action='store_true',
        help='尝试不登录获取公开频道消息'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='运行配置助手'
    )
    
    args = parser.parse_args()
      # 如果请求配置助手
    if args.config:
        from config_helper import create_env_file
        create_env_file()
        return
    
    # 创建InfoCompass实例
    compass = InfoCompass()
    
    # 如果请求批量处理所有频道
    if args.all_channels:
        if not compass.channels:
            print("❌ 未在.env文件中配置频道列表")
            print("请在.env文件中设置 TELEGRAM_CHANNELS=@channel1,@channel2")
            return
            
        print("🧭 InfoCompass CLI - 批量处理模式")
        print("="*50)
        print(f"配置的频道: {', '.join(compass.channels)}")
        print("="*50)
        
        results = await compass.process_all_channels(
            limit=args.limit,
            days_back=args.days,
            custom_prompt=args.prompt
        )
        
        print(f"\n✅ 批量处理完成！文件已保存到 {compass.data_dir} 目录")
        return
      # 单频道处理模式
    if not args.channel:
        print("❌ 请指定频道名称或使用 --all-channels 批量处理")
        return
    
    # 验证频道名称
    channel = args.channel.strip()
    if not channel.startswith('@'):
        channel = '@' + channel
    
    print("🧭 InfoCompass CLI")
    print("="*50)
    print(f"频道: {channel}")
    print(f"消息限制: {args.limit}")
    print(f"天数范围: {args.days}")
    if args.prompt:
        print(f"自定义提示: {args.prompt[:50]}...")
    print("="*50)
    
    try:
        # 处理频道
        result = await compass.process_channel(
            channel_username=channel,
            limit=args.limit,
            days_back=args.days,
            custom_prompt=args.prompt
        )
        
        if result:
            print(f"\n✅ 处理完成！文件已保存到 {compass.data_dir} 目录")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)


def main():
    """主函数"""
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
        sys.exit(0)


if __name__ == "__main__":
    main()
