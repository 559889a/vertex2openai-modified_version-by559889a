# Windows 运行指南（不使用 Docker）

本指南将帮助你在 Windows 系统上直接运行此项目，无需 Docker 或 WSL。

## 前置要求

1. **Python 3.8 或更高版本**
   - 下载地址：https://www.python.org/downloads/
   - 安装时请勾选 "Add Python to PATH"

2. **Google Cloud 凭证**（选择一种）：
   - Vertex AI Express API Key（推荐用于快速测试）
   - 或 Google Cloud 服务账号 JSON 密钥文件

## 步骤 1：安装 Python 依赖

打开命令提示符（cmd）或 PowerShell，进入项目目录：

```bash
cd d:\vertex2openai
```

安装依赖：

```bash
pip install -r app\requirements.txt
```

如果遇到网络问题，可以使用国内镜像：

```bash
pip install -r app\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 步骤 2：配置环境变量

项目根目录已经创建了 `.env` 文件，你需要根据自己的情况修改：

### 方式 1：使用 Vertex AI Express API Key（推荐）

编辑 `.env` 文件，填入你的 Express API Key：

```env
API_KEY=123456
VERTEX_EXPRESS_API_KEY=你的_Express_API_Key
```

### 方式 2：使用服务账号 JSON 内容

编辑 `.env` 文件：

```env
API_KEY=123456
GOOGLE_CREDENTIALS_JSON={"type": "service_account", "project_id": "...", ...}
```

### 方式 3：使用服务账号 JSON 文件

1. 在项目根目录创建 `credentials` 文件夹：
   ```bash
   mkdir credentials
   ```

2. 将你的服务账号 JSON 文件复制到 `credentials` 文件夹中

3. 编辑 `.env` 文件，取消注释并修改：
   ```env
   API_KEY=123456
   CREDENTIALS_DIR=./credentials
   ```

### 可选配置

如果需要，你还可以在 `.env` 中设置：

```env
# GCP 项目 ID（通常会自动从凭证中获取）
GCP_PROJECT_ID=你的项目ID

# GCP 区域
GCP_LOCATION=us-central1

# 启用轮询模式（当有多个服务账号时）
ROUNDROBIN=true
```

## 步骤 3：设置环境变量（Windows）

### 方法 A：使用 python-dotenv（推荐）

安装 python-dotenv：

```bash
pip install python-dotenv
```

创建启动脚本 `start.py`（项目根目录）：

```python
from dotenv import load_dotenv
import os
import uvicorn

# 加载 .env 文件
load_dotenv()

# 验证必需的环境变量
if not os.getenv('API_KEY'):
    print("错误：未设置 API_KEY 环境变量")
    exit(1)

# 启动应用
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8050,
        reload=True
    )
```

### 方法 B：手动设置环境变量（临时）

在命令提示符中（每次运行前需要设置）：

```cmd
set API_KEY=123456
set VERTEX_EXPRESS_API_KEY=你的_Express_API_Key
```

或在 PowerShell 中：

```powershell
$env:API_KEY="123456"
$env:VERTEX_EXPRESS_API_KEY="你的_Express_API_Key"
```

## 步骤 4：运行服务

### 如果使用方法 A（推荐）：

```bash
python start.py
```

### 如果使用方法 B：

先设置环境变量（见上），然后：

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8050 --reload
```

或直接从项目根目录运行：

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8050 --reload
```

## 步骤 5：验证服务

服务启动后，在浏览器中访问：

```
http://localhost:8050
```

你应该能看到：

```json
{
  "status": "ok",
  "message": "OpenAI to Gemini Adapter is running."
}
```

## 测试 API

### 查看可用模型

```bash
curl http://localhost:8050/v1/models -H "Authorization: Bearer 123456"
```

### 发送聊天请求

```bash
curl -X POST http://localhost:8050/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer 123456" ^
  -d "{\"model\": \"gemini-1.5-flash-latest\", \"messages\": [{\"role\": \"user\", \"content\": \"你好\"}]}"
```

**注意**：Windows cmd 使用 `^` 作为行继续符，PowerShell 使用 `` ` ``

## 常见问题

### 1. 端口被占用

如果 8050 端口被占用，可以修改端口：

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8051 --reload
```

### 2. 找不到模块

确保在项目根目录运行，或者设置 PYTHONPATH：

```bash
set PYTHONPATH=d:\vertex2openai
```

### 3. 凭证无法加载

- 检查 `.env` 文件是否在项目根目录
- 检查 JSON 文件格式是否正确
- 确认 Vertex AI API 已在 GCP 项目中启用

### 4. 网络代理

如果需要使用代理，在 `.env` 中添加：

```env
PROXY_URL=http://proxy.example.com:8080
```

## 停止服务

在运行窗口按 `Ctrl + C` 停止服务。

## 生产环境部署

对于生产环境，建议：

1. 使用 `gunicorn` 或 `waitress` 作为 WSGI 服务器
2. 配置 Windows 服务或使用任务计划程序自动启动
3. 设置反向代理（如 IIS、Nginx for Windows）
4. 使用更安全的 API_KEY
5. 定期检查日志和更新依赖

## 下一步

- 查看 [README.md](README.md) 了解更多功能
- 参考 [API 文档](README.md#api-usage) 学习如何使用