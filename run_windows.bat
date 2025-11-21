@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo    Vertex2OpenAI - Windows 启动脚本
echo ============================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装或未添加到 PATH 环境变量
    echo 请安装 Python 3.11+ 并确保添加到 PATH
    pause
    exit /b 1
)

echo [信息] 检测到 Python:
python --version
echo.

REM 设置项目根目录
set "PROJECT_ROOT=%~dp0"
set "APP_DIR=%PROJECT_ROOT%app"
set "CREDENTIALS_DIR=%PROJECT_ROOT%credentials"

REM 创建 credentials 目录（如果不存在）
if not exist "%CREDENTIALS_DIR%" (
    echo [信息] 创建 credentials 目录...
    mkdir "%CREDENTIALS_DIR%"
)

REM 检查是否存在 .env 文件，如果不存在则从示例创建
if not exist "%PROJECT_ROOT%.env" (
    echo [信息] .env 文件不存在，从 .env.example 创建...
    copy "%PROJECT_ROOT%.env.example" "%PROJECT_ROOT%.env" >nul
    echo [警告] 请编辑 .env 文件配置你的 API_KEY 和其他设置
    echo.
)

REM 加载 .env 文件中的环境变量
echo [信息] 加载 .env 配置...
for /f "usebackq tokens=1,* delims==" %%a in ("%PROJECT_ROOT%.env") do (
    set "line=%%a"
    REM 跳过注释行和空行
    if not "!line:~0,1!"=="#" (
        if not "%%a"=="" (
            set "%%a=%%b"
        )
    )
)

REM 覆盖 CREDENTIALS_DIR 为 Windows 路径
set "CREDENTIALS_DIR=%PROJECT_ROOT%credentials"

echo [信息] 配置信息:
echo   - 项目目录: %PROJECT_ROOT%
echo   - 应用目录: %APP_DIR%
echo   - 凭证目录: %CREDENTIALS_DIR%
echo   - 端口: %APP_PORT%
echo.

REM 检查虚拟环境是否存在
if not exist "%PROJECT_ROOT%venv" (
    echo [信息] 创建 Python 虚拟环境...
    python -m venv "%PROJECT_ROOT%venv"
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo [信息] 激活虚拟环境...
call "%PROJECT_ROOT%venv\Scripts\activate.bat"

REM 安装依赖
echo [信息] 检查并安装依赖...
pip install -r "%APP_DIR%\requirements.txt" -q
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)
echo [信息] 依赖安装完成
echo.

REM 设置默认端口
if "%APP_PORT%"=="" set "APP_PORT=8050"

echo ============================================
echo    启动服务器 (端口: %APP_PORT%)
echo ============================================
echo.
echo [提示] 按 Ctrl+C 停止服务器
echo.

REM 切换到 app 目录并启动服务器
cd /d "%APP_DIR%"
python -m uvicorn main:app --host 0.0.0.0 --port %APP_PORT% --reload

pause