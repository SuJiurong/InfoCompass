@echo off
echo 🧭 InfoCompass 设置向导
echo ===============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ 检测到Python
python --version

echo.
echo 📦 创建虚拟环境...
if exist "venv\" (
    echo 虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    echo ✅ 虚拟环境创建完成
)

echo.
echo 🔄 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo ⚙️  配置API密钥...
if not exist ".env" (
    copy .env.example .env
    echo ✅ 已创建配置文件 .env
    echo.
    echo ⚠️  请编辑 .env 文件，填入您的API密钥：
    echo    - TELEGRAM_API_ID: Telegram API ID
    echo    - TELEGRAM_API_HASH: Telegram API Hash  
    echo    - TELEGRAM_PHONE: 您的手机号码
    echo    - GEMINI_API_KEY: Google Gemini API密钥
    echo.
    set /p open_env="是否现在打开配置文件进行编辑？(Y/n): "
    if /i "%open_env%"=="Y" (
        notepad .env
    )
    if /i "%open_env%"=="" (
        notepad .env
    )
) else (
    echo ✅ 配置文件已存在
)

echo.
echo 🎉 设置完成！
echo 使用 start.bat 启动应用程序
echo.
pause
