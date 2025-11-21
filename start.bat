@echo off
chcp 65001 > nul
echo ============================================================
echo OpenAI to Gemini Adapter - 启动服务
echo ============================================================
echo.

REM 检查 Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 Python
    echo 请先运行 install.bat 安装依赖
    pause
    exit /b 1
)

REM 检查 .env 文件
if not exist .env (
    echo 错误：未找到 .env 配置文件
    echo 请先编辑 .env 文件并配置你的 API 密钥
    echo 详情请参考 WINDOWS_SETUP.md
    pause
    exit /b 1
)

REM 代理设置（如需使用代理请取消下行注释）
set PROXY_URL=http://127.0.0.1:7897

echo 正在启动服务...
echo 代理: %PROXY_URL%
echo.
python start.py

pause