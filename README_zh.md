---
title: OpenAI to Gemini Adapter
emoji: 🔄☁️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# OpenAI to Gemini Adapter

> **注意：** 本项目是基于 gzzhongqi 的 [vertex2openai](https://github.com/gzzhongqi/vertex2openai) 进行大幅修改的版本。
>
> **主要功能更新与修改：**
> *   **Gemini 原生格式支持：** 全面支持 Gemini 的原生 API 格式，包括内置的 Google 搜索增强（Grounding）和视觉能力。
> *   **增强的视觉支持：** OpenAI 兼容接口现在也支持视觉输入（图像分析）。
> *   **思考模型（Thinking Models）：** 引入了 `gemini-3-pro-preview-high` 和 `gemini-3-pro-preview-low` 两个别名模型，分别对应不同的思考深度（Thinking Level）。
> *   **提示词工程重构：** 完全重写了提示词（Prompt）处理逻辑，以获得更好的兼容性。
> *   **安全与部署：** 移除了硬编码的密钥，添加了 `APP_PORT` 配置，并集成了 GitHub Actions 实现 Docker 镜像自动构建。
> *   **健康监控：** 添加了 `/health` 端点。

本项目作为一个兼容层，提供与 OpenAI 兼容的 API 接口，将请求转换为 Google Vertex AI Gemini 模型的调用。这使你能够使用原本为 OpenAI API 构建的工具和应用来体验 Gemini 模型（包括 Gemini 1.5 Pro, Flash 以及最新的 Gemini 3.0 系列）的强大功能。

## 已知问题与限制

*   **OpenAI 格式搜索：** 通过 OpenAI 兼容格式调用搜索工具目前不稳定或无法工作。
*   **Gemini 格式上下文：** 使用 Gemini 原生格式时，网页上下文检索（Context Retrieval）可能会失败。
*   **思维链（CoT）：** Gemini 原生格式目前在返回完整的思维链（Chain of Thought）推理过程方面存在问题。
*   **Gemini 3.0 Pro：** 根据目前的观察，`gemini-3-pro` 模型可能本身就不会通过 API 返回推理链。
*   **图像生成：** 图像生成模型尚未经过充分测试，稳定性无法保证。

## 部署指南

### 1. 使用预构建的 Docker 镜像（推荐）

本仓库会自动构建 Docker 镜像并发布到 GitHub Container Registry。你可以直接使用该镜像进行部署，无需自己构建。

**镜像地址：** `ghcr.io/559889a/vertex2openai-modified_version-by559889a:latest`

#### Docker Compose 示例

在服务器上创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  vertex2openai:
    image: ghcr.io/559889a/vertex2openai-modified_version-by559889a:latest
    container_name: vertex2openai
    restart: unless-stopped
    ports:
      - "${APP_PORT:-8050}:7860"
    volumes:
      - ./credentials:/app/credentials
    env_file:
      - .env
```

### 2. 配置说明

所有配置均通过环境变量管理。请在 `docker-compose.yml` 同级目录下创建一个 `.env` 文件。

**创建 `.env` 文件：**

```bash
# --- 基础配置 ---

# 宿主机暴露端口 (默认: 8050)
APP_PORT=8050

# API 密钥 (必填)
# 用于保护此适配器服务，客户端需使用此密钥进行认证。请设置一个强密码。
API_KEY=your_secure_password_here

# --- 认证方式 (二选一) ---

# 方式 1: Vertex AI Express API Key (最简单)
VERTEX_EXPRESS_API_KEY=your_vertex_express_key

# 方式 2: Google Cloud 服务账号 JSON 内容
# 将 JSON 密钥文件的完整内容粘贴到这里。
GOOGLE_CREDENTIALS_JSON=

# 方式 3: 服务账号文件
# 保持 GOOGLE_CREDENTIALS_JSON 为空，并将 .json 文件放入 ./credentials 目录。
# 容器内默认读取 /app/credentials 目录。

# --- 可选设置 ---

# 如果提供多个凭证，是否启用轮询模式
ROUNDROBIN=false

# 代理设置 (如果服务器需要代理才能访问 Google API)
# PROXY_URL=http://proxy.example.com:8080
```

### 3. 健康检查

服务提供了 `/health` 端点用于健康检查。你可以将其用于正常运行时间监控或容器编排的健康探针。

*   **端点：** `GET /health`
*   **响应：** `{"status": "healthy", "timestamp": 1234567890.123}`

## API 使用

### 端点列表

-   `GET /v1/models`: 列出当前配置下可用的模型。
-   `POST /v1/chat/completions`: 生成文本的主要端点，模拟 OpenAI Chat Completions API。
-   `POST /gemini/v1beta/models/{model}:generateContent`: Gemini 原生 API 端点。
-   `POST /gemini/v1beta/models/{model}:streamGenerateContent`: Gemini 原生流式 API 端点。
-   `GET /health`: 健康检查端点。

### 认证

所有请求都需要在 `Authorization` 头部携带 API Key：

```
Authorization: Bearer YOUR_API_KEY
```
请将 `YOUR_API_KEY` 替换为你在环境变量 `API_KEY` 中设置的值。

## 许可证

本项目采用 MIT 许可证。详情请参阅 [`LICENSE`](LICENSE) 文件。