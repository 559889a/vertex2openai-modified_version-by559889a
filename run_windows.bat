@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo    Vertex2OpenAI - Windows 一键启动脚本
echo ================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.11+
    echo        下载地址: https://www.python.org/downloads/
    echo        安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [✓] 检测到 Python:
python --version
echo.

REM 设置项目路径
set "PROJECT_ROOT=%~dp0"
set "APP_DIR=%PROJECT_ROOT%app"
set "CREDENTIALS_DIR=%PROJECT_ROOT%credentials"

REM 创建必要目录
if not exist "%CREDENTIALS_DIR%" (
    echo [信息] 创建 credentials 目录...
    mkdir "%CREDENTIALS_DIR%"
)

REM 检查并创建 .env 配置文件
if not exist "%PROJECT_ROOT%.env" (
    if exist "%PROJECT_ROOT%.env.example" (
        echo [信息] 首次运行，创建 .env 配置文件...
        copy "%PROJECT_ROOT%.env.example" "%PROJECT_ROOT%.env" >nul
        echo.
        echo [警告] =========================================
        echo        请先编辑 .env 文件设置 API_KEY！
        echo        配置完成后重新运行此脚本。
        echo        =========================================
        echo.
        notepad "%PROJECT_ROOT%.env"
        pause
        exit /b 0
    ) else (
        echo [错误] 未找到 .env 和 .env.example 文件
        pause
        exit /b 1
    )
)

REM 加载环境变量
echo [信息] 加载配置文件...
for /f "usebackq tokens=1,* delims==" %%a in ("%PROJECT_ROOT%.env") do (
    set "line=%%a"
    if not "!line:~0,1!"=="#" if not "%%a"=="" set "%%a=%%b"
)

REM 设置默认端口
if "%APP_PORT%"=="" set "APP_PORT=8050"

REM 创建或更新虚拟环境
if not exist "%PROJECT_ROOT%venv" (
    echo [信息] 首次运行，创建 Python 虚拟环境...
    python -m venv "%PROJECT_ROOT%venv"
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [✓] 虚拟环境创建成功
)

REM 激活虚拟环境
call "%PROJECT_ROOT%venv\Scripts\activate.bat"

REM 安装/更新依赖
echo [信息] 检查并安装依赖包...
pip install --upgrade pip >nul 2>&1
pip install -r "%APP_DIR%\requirements.txt" --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)
echo [✓] 依赖检查完成
echo.

REM 显示配置信息
echo [配置信息]
echo   项目目录: %PROJECT_ROOT%
echo   凭证目录: %CREDENTIALS_DIR%
echo   监听端口: %APP_PORT%
echo.

echo ================================================
echo    服务器启动中... (端口: %APP_PORT%)
echo ================================================
echo.
echo [提示] 服务器地址: http://localhost:%APP_PORT%
echo        健康检查: http://localhost:%APP_PORT%/health
echo        按 Ctrl+C 可停止服务器
echo.

REM 启动服务器
cd /d "%APP_DIR%"
python -m uvicorn main:app --host 0.0.0.0 --port %APP_PORT% --reload

REM 服务器停止后暂停
echo.
echo 服务器已停止
pause