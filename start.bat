@echo off
echo 🧭 InfoCompass - 信息罗盘
echo ===============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查是否安装了依赖
if not exist "venv\" (
    echo 📦 首次运行，正在创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM 检查配置文件
if not exist ".env" (
    echo ⚙️  配置文件不存在，启动配置助手...
    python InfoCompass\config_helper.py
    echo.
)

REM 运行主程序
echo 🚀 启动InfoCompass...
python InfoCompass\main.py

pause
