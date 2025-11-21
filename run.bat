@echo off
chcp 65001 > nul
echo ============================================================
echo 正在启动 OpenAI to Gemini Adapter
echo ============================================================
echo.
echo 服务地址: http://localhost:8050
echo API密钥: 请查看 .env 文件
echo.
echo 按 Ctrl+C 停止服务
echo.

python start.py