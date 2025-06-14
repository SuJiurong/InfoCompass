#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoCompass - 信息罗盘
获取Telegram频道消息并使用Gemini API进行总结
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import google.generativeai as genai
from dotenv import load_dotenv
import aiofiles

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('infocompass.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class InfoCompass:
    """InfoCompass主类 - 信息获取和总结工具"""
    
    def __init__(self):
        """初始化InfoCompass"""
        # Telegram配置
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone_number = os.getenv('TELEGRAM_PHONE')
        
        # 频道配置
        channels_str = os.getenv('TELEGRAM_CHANNELS', '')
        self.channels = [ch.strip() for ch in channels_str.split(',') if ch.strip()]
        
        # Gemini配置
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # 验证配置
        self._validate_config()
        
        # 初始化客户端
        self.telegram_client = TelegramClient('infocompass_session', self.api_id, self.api_hash)
          # 配置Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # 数据存储目录
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _validate_config(self):
        """验证配置参数"""
        required_vars = {
            'TELEGRAM_API_ID': self.api_id,
            'TELEGRAM_API_HASH': self.api_hash,
            'GEMINI_API_KEY': self.gemini_api_key
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            logger.error(f"缺少必需的环境变量: {', '.join(missing_vars)}")
            print("\n请在项目根目录创建 .env 文件，并设置以下变量:")
            print("TELEGRAM_API_ID=your_api_id")
            print("TELEGRAM_API_HASH=your_api_hash")
            print("TELEGRAM_PHONE=your_phone_number (可选，用于私有频道)")
            print("TELEGRAM_CHANNELS=@channel1,@channel2,@channel3")
            print("GEMINI_API_KEY=your_gemini_api_key")
            print("\n获取Telegram API凭据: https://my.telegram.org/apps")
            print("获取Gemini API密钥: https://aistudio.google.com/app/apikey")
            sys.exit(1)
        
        # 检查频道配置
        if not self.channels:            logger.warning("未配置任何频道，将使用交互模式")
        else:
            logger.info(f"已配置 {len(self.channels)} 个频道: {', '.join(self.channels)}")
    
    async def get_channel_messages(self, channel_username: str, limit: int = 100, days_back: int = 1) -> List[Dict]:
        """
        获取Telegram频道消息
        
        Args:
            channel_username: 频道用户名 (例如: @channel_name)
            limit: 获取消息数量限制
            days_back: 获取多少天前的消息
        
        Returns:
            消息列表
        """
        messages = []
        
        try:
            # 对于公开频道，尝试不登录连接
            try:
                # 检查会话文件
                session_file = 'infocompass_session.session'
                if os.path.exists(session_file):
                    logger.info(f"会话文件存在: {session_file}, 大小: {os.path.getsize(session_file)} 字节")
                else:
                    logger.info(f"会话文件不存在: {session_file}")

                # 使用with语句确保客户端会正确启动和关闭
                if not self.telegram_client.is_connected():
                    logger.info("尝试连接到Telegram...")
                    await self.telegram_client.connect()
                    logger.info("已连接到Telegram客户端")
                else:
                    logger.info("Telegram客户端已经连接")

                # 检查是否已经授权
                is_authorized = await self.telegram_client.is_user_authorized()
                logger.info(f"客户端授权状态: {'已授权' if is_authorized else '未授权'}")

                if not is_authorized:
                    logger.info("需要登录Telegram...")
                    if self.phone_number:
                        # 发送验证码
                        await self.telegram_client.send_code_request(self.phone_number)
                        logger.info(f"验证码已发送到 {self.phone_number}")

                        # 等待用户输入验证码
                        verification_code = input("请输入收到的验证码: ")

                        try:
                            # 尝试使用验证码登录
                            await self.telegram_client.sign_in(self.phone_number, verification_code)
                            logger.info("登录成功！")

                            # 再次检查授权状态
                            is_authorized = await self.telegram_client.is_user_authorized()
                            logger.info(f"登录后授权状态: {'已授权' if is_authorized else '仍未授权'}")
                        except Exception as sign_in_error:
                            # 如果是两步验证，需要密码
                            if "2FA" in str(sign_in_error) or "password" in str(sign_in_error).lower():
                                password = input("请输入两步验证密码: ")
                                await self.telegram_client.sign_in(password=password)
                                logger.info("两步验证登录成功！")

                                # 再次检查授权状态
                                is_authorized = await self.telegram_client.is_user_authorized()
                                logger.info(f"两步验证后授权状态: {'已授权' if is_authorized else '仍未授权'}")
                            else:
                                raise sign_in_error
                    else:
                        logger.warning("无法连接到Telegram，未提供电话号码")
                        raise Exception("登录需要电话号码，请在环境变量中设置 TELEGRAM_PHONE")
                else:
                    logger.info("已连接到Telegram (已授权)")
            except Exception as e:
                logger.error(f"连接Telegram时发生错误: {str(e)}")
                raise e

            logger.info(f"开始获取频道 {channel_username} 的消息")
            
            # 计算时间范围
            since_date = datetime.now() - timedelta(days=days_back)
            
            # 获取频道实体
            try:
                channel = await self.telegram_client.get_entity(channel_username)
            except Exception as e:
                logger.error(f"无法访问频道 {channel_username}: {str(e)}")
                logger.info("提示：确保频道名称正确且为公开频道，或您有访问权限")
                return []

            messages_count = 0
            # 获取消息
            async for message in self.telegram_client.iter_messages(
                channel, 
                limit=limit,
                offset_date=since_date
            ):
                if message.message:  # 只处理有文本内容的消息
                    message_data = {
                        'id': message.id,
                        'date': message.date.isoformat(),
                        'text': message.message,
                        'views': getattr(message, 'views', 0),
                        'forwards': getattr(message, 'forwards', 0),
                        'replies': getattr(message.replies, 'replies', 0) if message.replies else 0,
                        'has_media': bool(message.media),
                        'media_type': self._get_media_type(message.media) if message.media else None
                    }
                    messages.append(message_data)

                    messages_count += 1
                    if messages_count % 10 == 0:  # 每获取10条消息后暂停
                        await asyncio.sleep(1)
            
            logger.info(f"成功获取 {len(messages)} 条消息")
            return messages
            
        except Exception as e:
            logger.error(f"获取消息时发生错误: {str(e)}")
            raise
        finally:
            # 我们不在这里断开连接，因为可能需要处理多个频道
            pass

    def _get_media_type(self, media) -> str:
        """获取媒体类型"""
        if isinstance(media, MessageMediaPhoto):
            return 'photo'
        elif isinstance(media, MessageMediaDocument):
            return 'document'
        else:
            return 'other'
    
    async def save_messages(self, messages: List[Dict], channel_name: str) -> str:
        """
        保存消息到本地文件
        
        Args:
            messages: 消息列表
            channel_name: 频道名称
        
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{channel_name}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(messages, ensure_ascii=False, indent=2))
            
            logger.info(f"消息已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存消息时发生错误: {str(e)}")
            raise
    
    async def summarize_with_gemini(self, messages: List[Dict], custom_prompt: str = None) -> str:
        """
        使用Gemini API总结消息
        
        Args:
            messages: 消息列表
            custom_prompt: 自定义提示词
        
        Returns:
            总结文本
        """
        try:
            # 合并所有消息文本
            combined_text = "\n\n".join([
                f"消息{i+1} ({msg['date']}):\n{msg['text']}"
                for i, msg in enumerate(messages)
                if msg.get('text')
            ])
            
            # 构建提示词
            if custom_prompt:
                prompt = custom_prompt + "\n\n" + combined_text
            else:
                prompt = f"""
请对以下Telegram频道消息进行总结分析：

任务要求：
1. 提取主要话题和关键信息
2. 分析消息趋势和重点内容
3. 识别重要的新闻、事件或讨论点
4. 提供简洁明了的总结

消息内容：
{combined_text}

请用中文回答，格式化输出，包含：
- 主要话题总结
- 关键信息点
- 重要事件/新闻
- 总体趋势分析
"""
            
            # 调用Gemini API
            logger.info("正在使用Gemini API生成总结...")
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, 
                prompt
            )
            
            summary = response.text
            logger.info("总结生成完成")
            
            return summary
            
        except Exception as e:
            logger.error(f"使用Gemini总结时发生错误: {str(e)}")
            raise
    
    async def save_summary(self, summary: str, channel_name: str) -> str:
        """
        保存总结到本地文件
        
        Args:
            summary: 总结内容
            channel_name: 频道名称
        
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{channel_name}_summary_{timestamp}.md"
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(f"# {channel_name} 频道消息总结\n\n")
                await f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                await f.write("---\n\n")
                await f.write(summary)
            
            logger.info(f"总结已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存总结时发生错误: {str(e)}")
            raise
    
    async def process_channel(self, channel_username: str, limit: int = 100, 
                            days_back: int = 1, custom_prompt: str = None) -> Dict[str, str]:
        """
        处理频道消息的完整流程
        
        Args:
            channel_username: 频道用户名
            limit: 消息数量限制
            days_back: 获取天数
            custom_prompt: 自定义总结提示词
        
        Returns:
            包含文件路径的字典
        """
        try:
            # 清理频道名称作为文件名
            channel_name = channel_username.replace('@', '').replace('/', '_')
            
            # 1. 获取消息
            print(f"📱 正在获取频道 {channel_username} 的消息...")
            messages = await self.get_channel_messages(channel_username, limit, days_back)
            
            if not messages:
                print("❌ 未获取到任何消息")
                return {}
            
            print(f"✅ 成功获取 {len(messages)} 条消息")
            
            # 2. 保存消息
            print("💾 正在保存消息到本地...")
            messages_file = await self.save_messages(messages, channel_name)
            
            # 3. 生成总结
            print("🤖 正在使用Gemini生成总结...")
            summary = await self.summarize_with_gemini(messages, custom_prompt)
            
            # 4. 保存总结
            print("📝 正在保存总结...")
            summary_file = await self.save_summary(summary, channel_name)
            
            print("🎉 处理完成！")
            print(f"📄 消息文件: {messages_file}")
            print(f"📋 总结文件: {summary_file}")
            
            # 显示总结预览
            print("\n" + "="*50)
            print("📊 总结预览:")
            print("="*50)
            print(summary[:500] + "..." if len(summary) > 500 else summary)
            
            return {
                'messages_file': messages_file,
                'summary_file': summary_file,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"处理频道时发生错误: {str(e)}")
            print(f"❌ 处理失败: {str(e)}")
            raise

    async def process_all_channels(self, limit: int = 100, days_back: int = 1, 
                                 custom_prompt: str = None) -> Dict[str, Dict]:
        """
        批量处理所有配置的频道
        
        Args:
            limit: 消息数量限制
            days_back: 获取天数
            custom_prompt: 自定义总结提示词
        
        Returns:
            所有频道的处理结果
        """
        if not self.channels:
            logger.error("未配置任何频道")
            return {}
        
        results = {}
        total_channels = len(self.channels)
        
        print(f"🚀 开始批量处理 {total_channels} 个频道...")
        
        for i, channel in enumerate(self.channels, 1):
            print(f"\n📺 [{i}/{total_channels}] 处理频道: {channel}")
            print("-" * 50)
            
            try:
                result = await self.process_channel(
                    channel_username=channel,
                    limit=limit,
                    days_back=days_back,
                    custom_prompt=custom_prompt
                )
                results[channel] = result
                print(f"✅ 频道 {channel} 处理完成")
                
            except Exception as e:
                logger.error(f"处理频道 {channel} 时发生错误: {str(e)}")
                results[channel] = {'error': str(e)}
                print(f"❌ 频道 {channel} 处理失败: {str(e)}")
        
        print(f"\n🎉 批量处理完成！")
        print(f"✅ 成功: {len([r for r in results.values() if 'error' not in r])} 个频道")
        print(f"❌ 失败: {len([r for r in results.values() if 'error' in r])} 个频道")
        
        return results

    # ...existing code...
    

async def main():
    """主函数"""
    print("🧭 InfoCompass - 信息罗盘")
    print("Filter noise. Distill essence. Pierce the fog.")
    print("="*50)
    
    compass = None
    try:
        # 创建InfoCompass实例
        compass = InfoCompass()
        
        # 检查是否有配置的频道
        if compass.channels:
            print(f"📋 检测到 {len(compass.channels)} 个配置的频道:")
            for i, channel in enumerate(compass.channels, 1):
                print(f"  {i}. {channel}")
            
            print("\n选择处理模式:")
            print("1. 批量处理所有配置频道")
            print("2. 选择单个频道处理") 
            print("3. 手动输入频道")
            
            choice = input("\n请选择 (1-3, 默认1): ").strip() or "1"
            
            if choice == "1":
                # 批量处理模式
                print("\n🚀 批量处理模式")
                
                try:
                    limit = int(input("消息数量限制 (默认100): ").strip() or "100")
                except ValueError:
                    limit = 100
                
                try:
                    days_back = int(input("获取几天前的消息 (默认1): ").strip() or "1")
                except ValueError:
                    days_back = 1
                
                custom_prompt = input("自定义总结提示词 (可选，直接回车跳过): ").strip() or None

                print("\n🚀 开始批量处理...")
                results = await compass.process_all_channels(
                    limit=limit,
                    days_back=days_back,
                    custom_prompt=custom_prompt
                )

                print(f"\n✅ 批量处理完成！文件已保存到 {compass.data_dir} 目录")
                return

            elif choice == "2":
                # 选择单个频道
                print("\n请选择要处理的频道:")
                for i, channel in enumerate(compass.channels, 1):
                    print(f"{i}. {channel}")

                try:
                    selection = int(input(f"\n请选择 (1-{len(compass.channels)}): ").strip())
                    if 1 <= selection <= len(compass.channels):
                        channel = compass.channels[selection - 1]
                    else:
                        print("❌ 无效选择")
                        return
                except ValueError:
                    print("❌ 无效输入")
                    return

            else:
                # 手动输入模式
                channel = input("请输入Telegram频道用户名 (例如: @channelname): ").strip()
                if not channel:
                    print("❌ 频道名称不能为空")
                    return

                if not channel.startswith('@'):
                    channel = '@' + channel
        else:
            # 交互式输入模式
            channel = input("请输入Telegram频道用户名 (例如: @channelname): ").strip()
            if not channel:
                print("❌ 频道名称不能为空")
                return

            if not channel.startswith('@'):
                channel = '@' + channel

        # 单频道处理的参数输入
        try:
            limit = int(input("消息数量限制 (默认100): ").strip() or "100")
        except ValueError:
            limit = 100

        try:
            days_back = int(input("获取几天前的消息 (默认1): ").strip() or "1")
        except ValueError:
            days_back = 1

        custom_prompt = input("自定义总结提示词 (可选，直接回车跳过): ").strip() or None

        print("\n🚀 开始处理...")

        # 处理频道
        result = await compass.process_channel(
            channel_username=channel,
            limit=limit,
            days_back=days_back,
            custom_prompt=custom_prompt
        )

        if result:
            print(f"\n✅ 处理完成！文件已保存到 {compass.data_dir} 目录")

    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        logger.error(f"主程序错误: {str(e)}")
    finally:
        # 确保在程序结束时断开Telegram客户端连接
        if compass and compass.telegram_client and compass.telegram_client.is_connected():
            logger.info("正在断开Telegram客户端连接...")
            await compass.telegram_client.disconnect()
            logger.info("Telegram客户端已断开连接")


if __name__ == "__main__":
    asyncio.run(main())


