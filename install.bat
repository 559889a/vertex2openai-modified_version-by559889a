@echo off
chcp 65001 > nul
echo ============================================================
echo OpenAI to Gemini Adapter - Windows 安装脚本
echo ============================================================
echo.

REM 检查 Python 是否安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 Python
    echo 请从 https://www.python.org/downloads/ 下载并安装 Python 3.8+
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/3] Python 已安装
python --version

echo.
echo [2/3] 正在安装 Python 依赖包...
echo.

REM 升级 pip
python -m pip install --upgrade pip

REM 安装项目依赖
python -m pip install -r app\requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo 安装失败！如果遇到网络问题，请尝试使用国内镜像：
    echo python -m pip install -r app\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause
    exit /b 1
)

REM 安装 python-dotenv
python -m pip install python-dotenv

echo.
echo [3/3] 检查 .env 配置文件...

if not exist .env (
    echo.
    echo 警告：未找到 .env 文件
    echo .env 文件已经创建，但你需要配置它
    echo.
    echo 请编辑 .env 文件并设置：
    echo   1. API_KEY（必填）
    echo   2. VERTEX_EXPRESS_API_KEY 或其他凭证方式
    echo.
    echo 详细说明请参考 WINDOWS_SETUP.md
) else (
    echo ✓ .env 文件已存在
)

echo.
echo ============================================================
echo 安装完成！
echo ============================================================
echo.
echo 下一步：
echo   1. 编辑 .env 文件，填入你的 API 密钥和凭证
echo   2. 运行 start.bat 启动服务
echo   3. 或查看 WINDOWS_SETUP.md 了解更多选项
echo.
pause