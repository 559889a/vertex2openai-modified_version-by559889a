---
title: OpenAI to Gemini Adapter
emoji: 🔄☁️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8050
---

# OpenAI to Gemini Adapter

> **注意：** 本项目是基于 gzzhongqi 的 [vertex2openai](https://github.com/gzzhongqi/vertex2openai) 进行大幅修改的版本。
>
> **主要功能更新与修改：**
> *   **图像生成模型支持：** 现已支持 Gemini 图像生成模型，包括 `gemini-3-pro-image-preview`（大香蕉🍌）和 `gemini-2.5-flash-image`（小香蕉🍌）。
> *   **Gemini 原生格式支持：** 全面支持 Gemini 的原生 API 格式，包括内置的 Google 搜索增强（Grounding）和视觉能力。
> *   **增强的视觉支持：** OpenAI 兼容接口现在也支持视觉输入（图像分析）。
> *   **思考模型（Thinking Models）：** 引入了 `gemini-3-pro-preview-high` 和 `gemini-3-pro-preview-low` 两个别名模型，分别对应不同的思考深度（Thinking Level）。
> *   **Windows 一键启动：** 优化了 Windows 启动脚本（`run_windows.bat`），支持在 Windows 平台一键启动。
> *   **提示词工程重构：** 完全重写了提示词（Prompt）处理逻辑，以获得更好的兼容性。
> *   **安全与部署：** 移除了硬编码的密钥，添加了 `APP_PORT` 配置，并集成了 GitHub Actions 实现 Docker 镜像自动构建。
> *   **健康监控：** 添加了 `/health` 端点。

本项目作为一个兼容层，提供与 OpenAI 兼容的 API 接口，将请求转换为 Google Vertex AI Gemini 模型的调用。这使你能够使用原本为 OpenAI API 构建的工具和应用来体验 Gemini 模型（包括 Gemini 2.0 Flash、Gemini 2.5 Flash/Pro 以及最新的 Gemini 3.0 Pro 系列）的强大功能。

> **认证方式重要说明：**
> 本项目的主要开发和优化工作均针对 **Vertex Express API Key** 模式进行。使用服务账号 JSON 凭证的认证方式**未经过充分测试**，其可用性**未知**。建议使用 Vertex Express API Key 以获得最佳体验。

## 已知问题与限制

### 🔴 重要问题：Linux 平台限制
*   **Linux 自动重试功能异常：** 自动重试机制在 Linux 系统上存在问题。当 API 调用失败时，服务可能无法按预期自动重试。此问题不影响 Windows 平台，Windows 上自动重试功能运行正常。**Linux 用户遇到请求失败时，请手动重试。**

### 其他已知问题
*   **OpenAI 格式搜索：** 通过 OpenAI 兼容格式调用搜索工具目前不稳定或无法工作。
*   **Gemini 格式上下文：** 使用 Gemini 原生格式时，网页上下文检索（Context Retrieval）可能会失败。
*   **思维链（CoT）：** Gemini 原生格式目前在返回完整的思维链（Chain of Thought）推理过程方面存在问题。
*   **Gemini 3.0 Pro：** 根据目前的观察，`gemini-3-pro` 模型可能本身就不会通过 API 返回推理链。
*   **图像生成：** 图像生成模型为新增功能。已使用 Cherry Studio 在 OpenAI 兼容端口和 Gemini 原生端口上测试通过。部分边缘场景可能仍存在问题。

## 部署指南

### 1. Windows 一键启动（Windows 用户最简单）

对于 Windows 用户，我们提供了一键启动脚本，可自动配置环境并启动服务。

**系统要求：**
- Python 3.11 或更高版本
- Windows 10 或更高版本

**使用步骤：**
1. 下载或克隆本仓库到本地
2. 双击运行 `run_windows.bat`
3. 首次运行时，脚本会：
   - 从 `.env.example` 创建 `.env` 配置文件
   - 自动打开配置文件供你编辑
   - 创建 Python 虚拟环境
   - 自动安装所有依赖
4. 编辑 `.env` 文件，设置 `API_KEY` 和认证凭证
5. 再次运行 `run_windows.bat` 启动服务

服务将在 `http://localhost:8050`（或你配置的 `APP_PORT`）上运行。

### 2. 使用预构建的 Docker 镜像（推荐用于 Linux/服务器）

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
      - "${APP_PORT:-8050}:8050"
    volumes:
      - ./credentials:/app/credentials
    env_file:
      - .env
```

### 3. 配置说明

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

# --- GCP 配置 (可选，但推荐用于 Express 模式) ---
# GCP_PROJECT_ID=your-gcp-project-id
# GCP_LOCATION=us-central1

# --- 可选设置 ---

# 如果提供多个凭证，是否启用轮询模式
ROUNDROBIN=false

# 代理设置 (如果服务器需要代理才能访问 Google API)
# PROXY_URL=http://proxy.example.com:8080
```

### 4. 健康检查

## 支持的模型列表

### 基础模型（12个）

当前支持以下 Gemini 模型：

1. **gemini-2.0-flash** - 快速响应模型
2. **gemini-2.0-flash-001** - 快速响应模型（001 版本）
3. **gemini-2.0-flash-lite** - 轻量级快速模型
4. **gemini-2.0-flash-lite-001** - 轻量级快速模型（001 版本）
5. **gemini-2.5-flash** - 增强型快速模型
6. **gemini-2.5-flash-image** 🆕🍌 - 小香蕉图像生成模型
7. **gemini-2.5-flash-image-preview** 🆕🍌 - 小香蕉图像预览版
8. **gemini-2.5-flash-lite-preview-09-2025** 🆕 - 2025年9月轻量预览版
9. **gemini-2.5-flash-preview-09-2025** 🆕 - 2025年9月预览版
10. **gemini-2.5-pro** - Pro 模型
11. **gemini-3-pro-image-preview** 🆕🍌 - 大香蕉图像生成模型
12. **gemini-3-pro-preview** - 最新预览模型

### 别名模型（2个）

预配置思考深度的特殊模型：

- **gemini-3-pro-preview-high** - 高思考深度（最大推理深度）
- **gemini-3-pro-preview-low** - 低思考深度（最小延迟）

**说明：** 🆕 标记表示本次更新新增的模型。🍌 标记表示具备图像生成能力。

**测试状态：** 图像生成模型已使用 Cherry Studio 在 OpenAI 兼容端口和 Gemini 原生端口上测试通过。

## 更新日志

详细的版本历史和更新内容请查看 [CHANGELOG.md](CHANGELOG.md)。

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