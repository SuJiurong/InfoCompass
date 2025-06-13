#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoCompass 批量处理工具
专门用于批量处理.env中配置的所有频道
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import InfoCompass


async def batch_process():
    """批量处理所有配置的频道"""
    print("🧭 InfoCompass 批量处理工具")
    print("="*50)
    
    try:
        # 创建InfoCompass实例
        compass = InfoCompass()
        
        if not compass.channels:
            print("❌ 未在.env文件中配置频道列表")
            print("请在.env文件中设置 TELEGRAM_CHANNELS=@channel1,@channel2,@channel3")
            return
        
        print(f"📋 检测到 {len(compass.channels)} 个配置的频道:")
        for i, channel in enumerate(compass.channels, 1):
            print(f"  {i}. {channel}")
        
        print("\n⚙️  配置选项:")
        
        # 获取配置参数
        try:
            limit = int(input("消息数量限制 (默认100): ").strip() or "100")
        except ValueError:
            limit = 100
        
        try:
            days_back = int(input("获取几天前的消息 (默认1): ").strip() or "1")
        except ValueError:
            days_back = 1
        
        custom_prompt = input("自定义总结提示词 (可选，直接回车跳过): ").strip() or None
        
        print(f"\n🚀 开始批量处理 {len(compass.channels)} 个频道...")
        print(f"📊 参数: 消息限制={limit}, 天数={days_back}")
        if custom_prompt:
            print(f"🎯 自定义提示: {custom_prompt[:50]}...")
        
        confirm = input("\n确认开始处理？(Y/n): ").strip().lower()
        if confirm and confirm != 'y':
            print("❌ 处理已取消")
            return
        
        # 批量处理
        results = await compass.process_all_channels(
            limit=limit,
            days_back=days_back,
            custom_prompt=custom_prompt
        )
        
        # 显示结果统计
        successful = [ch for ch, result in results.items() if 'error' not in result]
        failed = [ch for ch, result in results.items() if 'error' in result]
        
        print(f"\n📊 处理完成统计:")
        print(f"✅ 成功处理: {len(successful)} 个频道")
        if successful:
            for channel in successful:
                print(f"   - {channel}")
        
        if failed:
            print(f"❌ 处理失败: {len(failed)} 个频道")
            for channel in failed:
                print(f"   - {channel}: {results[channel]['error']}")
        
        print(f"\n💾 所有文件已保存到 {compass.data_dir} 目录")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)


def main():
    """主函数"""
    try:
        asyncio.run(batch_process())
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
        sys.exit(0)


if __name__ == "__main__":
    main()
