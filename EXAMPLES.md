# InfoCompass 使用示例

## 基本使用流程

### 1. 设置环境

```bash
# Windows
setup.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

### 2. 配置API密钥和频道

编辑 `.env` 文件：
```env
TELEGRAM_API_ID=1234567
TELEGRAM_API_HASH=abcdef123456789
TELEGRAM_PHONE=+1234567890
TELEGRAM_CHANNELS=@giffgaff_siyu,@tech_news,@crypto_updates
GEMINI_API_KEY=your_gemini_key_here
```

注意：对于公开频道，`TELEGRAM_PHONE` 可以留空。

### 3. 运行示例

#### 批量处理所有配置的频道
```bash
# 使用交互式模式，选择批量处理
python InfoCompass/main.py

# 使用命令行批量处理
python InfoCompass/cli.py --all-channels -l 100 -d 3
```

#### 获取单个频道消息
```bash
python InfoCompass/cli.py @channel_name -l 50 -d 1
```

#### 获取新闻频道消息
```bash
python InfoCompass/cli.py @news_channel -l 50 -d 1
```

#### 获取技术频道消息并自定义总结
```bash
python InfoCompass/cli.py @tech_channel --limit 100 --days 3 --prompt "请重点关注新技术发布和产品更新"
```

#### 分析加密货币频道
```bash
python InfoCompass/cli.py @crypto_channel -l 200 -d 7 -p "分析市场趋势和价格变动，提取关键投资信息"
```

## 输出示例

### 消息文件 (JSON)
```json
[
  {
    "id": 12345,
    "date": "2025-06-13T10:30:00",
    "text": "重要消息内容...",
    "views": 1500,
    "forwards": 25,
    "replies": 5,
    "has_media": false,
    "media_type": null
  }
]
```

### 总结文件 (Markdown)
```markdown
# channel_name 频道消息总结

生成时间: 2025-06-13 14:30:00

---

## 主要话题总结
- 话题1: 相关讨论内容
- 话题2: 重要事件分析

## 关键信息点
- 信息点1
- 信息点2

## 重要事件/新闻
- 事件1: 详细描述
- 事件2: 影响分析

## 总体趋势分析
整体趋势和预测...
```

## 常用命令

```bash
# 批量处理所有配置的频道
python InfoCompass/cli.py --all-channels

# 批量处理，自定义参数
python InfoCompass/cli.py --all-channels -l 200 -d 7 --prompt "重点关注技术趋势"

# 交互式模式
python InfoCompass/main.py

# 快速获取最新消息
python InfoCompass/cli.py @channel_name

# 获取一周消息
python InfoCompass/cli.py @channel_name -d 7 -l 500

# 技术分析模式
python InfoCompass/cli.py @tech_channel -p "重点分析技术趋势和产品发布"

# 新闻摘要模式  
python InfoCompass/cli.py @news_channel -p "按重要性排序新闻，分析影响"

# 投资分析模式
python InfoCompass/cli.py @finance_channel -p "分析市场机会和风险提示"

# 无需登录模式（仅限公开频道）
python InfoCompass/cli.py @public_channel --no-login
```

## 提示词模板

### 技术分析
```
"请重点关注以下内容：1) 新技术发布和产品更新 2) 行业发展趋势 3) 技术突破和创新 4) 公司动态和合作"
```

### 新闻总结
```  
"请按重要性排序新闻事件，分析其潜在影响，并识别值得关注的发展趋势"
```

### 市场分析
```
"请分析市场趋势、价格变动、投资机会和风险提示，提供简洁的市场概览"
```

### 学术研究
```
"请总结学术动态、研究进展、论文发布和学术会议信息，突出重要的科研成果"
```
