#!/bin/bash

echo "🧭 InfoCompass - 信息罗盘"
echo "==============================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到Python3，请先安装Python 3.7+"
    exit 1
fi

# 检查是否安装了依赖
if [ ! -d "venv" ]; then
    echo "📦 首次运行，正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚙️  配置文件不存在，启动配置助手..."
    python InfoCompass/config_helper.py
    echo ""
fi

# 运行主程序
echo "🚀 启动InfoCompass..."
python InfoCompass/main.py

echo ""
echo "👋 InfoCompass已退出"
