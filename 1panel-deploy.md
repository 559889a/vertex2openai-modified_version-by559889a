# 1Panel 部署指南

本指南将帮助你在 1Panel 面板上部署 OpenAI to Gemini Adapter。

## 前置准备

1. 确保你已经安装了 1Panel 面板。
2. 确保你的服务器已经安装了 Docker 和 Docker Compose（1Panel 通常会自动安装）。
3. 准备好你的 Google Cloud 凭证（Service Account JSON 文件或 Vertex Express API Key）。

## 部署步骤

### 1. 创建项目目录

在 1Panel 的文件管理中，创建一个新的目录，例如 `/opt/1panel/apps/vertex2openai`。

### 2. 上传文件

将以下文件上传到刚刚创建的目录中：

*   `docker-compose.yml`
*   `.env.example` (重命名为 `.env`)
*   `Dockerfile`
*   `app/` 目录 (包含所有源代码)
*   `requirements.txt` (如果有的话，通常在 app/requirements.txt)

**注意：** 如果你使用 git 拉取代码，可以直接在服务器终端进入该目录并执行 `git clone`。

### 3. 配置环境变量

编辑 `.env` 文件，填入你的配置信息：

```env
# 端口设置 (默认 8050)
APP_PORT=8050

# API 密钥 (用于保护此服务，请修改为强密码)
API_KEY=your_secure_password

# --- 认证方式 (二选一) ---

# 方式 1: Vertex Express API Key
VERTEX_EXPRESS_API_KEY=your_vertex_express_key

# 方式 2: Google Cloud Service Account JSON
# 将你的 JSON 文件内容完整粘贴到这里
GOOGLE_CREDENTIALS_JSON=

# --- 其他设置 ---
CREDENTIALS_DIR=/app/credentials
ROUNDROBIN=false
```

### 4. 创建应用 (使用 Docker Compose)

1.  打开 1Panel 面板，进入 **容器** -> **编排**。
2.  点击 **创建编排**。
3.  **名称**：填写 `vertex2openai` (或你喜欢的名字)。
4.  **路径**：选择你刚才创建的目录 (例如 `/opt/1panel/apps/vertex2openai`)。
5.  1Panel 会自动读取该目录下的 `docker-compose.yml` 文件。
6.  点击 **确认** 或 **创建**。

### 5. 验证部署

等待容器启动完成后，你可以通过浏览器访问 `http://你的服务器IP:8050` 来验证服务是否正常运行。

*   访问 `http://你的服务器IP:8050/` 应该看到 `{"status": "ok", ...}`。
*   访问 `http://你的服务器IP:8050/v1/models` (需要带上 `Authorization: Bearer 你的API_KEY` header) 查看可用模型。

## 反向代理 (可选，推荐)

为了通过域名访问并启用 HTTPS，建议配置反向代理：

1.  进入 1Panel **网站** -> **创建网站** -> **反向代理**。
2.  **主域名**：填写你的域名 (例如 `api.example.com`)。
3.  **代理地址**：`http://127.0.0.1:8050`。
4.  创建完成后，进入网站设置，配置 HTTPS 证书。

## 更新维护

### 通过 Git 更新

如果你是通过 Git 克隆的项目：

1.  进入项目目录：`cd /opt/1panel/apps/vertex2openai`
2.  拉取最新代码：`git pull`
3.  在 1Panel 编排页面，找到该应用，点击 **重建** (Rebuild)。

### 手动更新

1.  上传新的代码文件覆盖旧文件。
2.  在 1Panel 编排页面，找到该应用，点击 **重建**。