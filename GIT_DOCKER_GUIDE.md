# GitHub 发布与 Docker 维护指南

本指南将手把手教你如何将本项目上传到 GitHub，如何使用 Git 进行日常维护，以及如何构建和发布 Docker 镜像。

## 第一部分：上传项目到 GitHub

### 1. 准备工作

*   确保你已经注册了 [GitHub](https://github.com/) 账号。
*   确保你的电脑上安装了 [Git](https://git-scm.com/downloads)。

### 2. 在 GitHub 上创建新仓库

1.  登录 GitHub，点击右上角的 **+** 号，选择 **New repository**。
2.  **Repository name**: 输入项目名称，例如 `vertex2openai-adapter`。
3.  **Description**: (可选) 输入项目描述，例如 "OpenAI to Gemini Adapter for 1Panel"。
4.  **Public/Private**: 选择 **Public** (公开) 或 **Private** (私有)。
5.  **Initialize this repository with**: **不要**勾选任何选项（因为我们已经有现成的代码了）。
6.  点击 **Create repository**。
7.  创建成功后，你会看到一个页面，复制 **HTTPS** 或 **SSH** 的仓库地址（例如 `https://github.com/你的用户名/vertex2openai-adapter.git`）。

### 3. 初始化本地仓库并上传

在你的项目根目录（`d:\vertex2openai-559改\vertex2openai`）打开终端（CMD 或 PowerShell），依次执行以下命令：

```bash
# 1. 初始化 Git 仓库
git init

# 2. 添加所有文件到暂存区
# 注意：.gitignore 文件会自动忽略 .env 和 credentials/ 等敏感文件
git add .

# 3. 提交代码到本地仓库
git commit -m "Initial commit: Project setup with 1Panel support"

# 4. 将本地仓库关联到 GitHub 远程仓库
# 将下面的 URL 替换为你刚才复制的仓库地址
git remote add origin https://github.com/你的用户名/vertex2openai-adapter.git

# 5. 推送代码到 GitHub
# 如果是第一次使用，可能会弹出窗口让你登录 GitHub
git push -u origin main
```

执行完第 5 步后，刷新 GitHub 页面，你应该就能看到你的代码了。

---

## 第二部分：使用 Git 进行更新维护

当你修改了代码（例如修改了 `README.md` 或修复了 Bug）后，需要将更改同步到 GitHub。

### 1. 查看更改状态

```bash
git status
```
这会列出你修改过的文件。

### 2. 提交更改

```bash
# 添加所有修改过的文件
git add .

# 提交并写明修改内容
git commit -m "Update README and fix bug in config"
```

### 3. 推送到 GitHub

```bash
git push
```

### 4. 在服务器上更新（1Panel）

如果你已经在 1Panel 上通过 Git 部署了项目：

1.  进入 1Panel 面板。
2.  进入项目目录（在终端或文件管理中）。
3.  执行 `git pull` 拉取最新代码。
4.  在 **容器** -> **编排** 中找到应用，点击 **重建** (Rebuild) 以应用更改。

---

## 第三部分：构建 Docker 镜像 (可选)

通常情况下，1Panel 会根据 `docker-compose.yml` 和 `Dockerfile` 自动在服务器上构建镜像。但如果你想将镜像发布到 Docker Hub，让别人直接拉取镜像使用，可以按照以下步骤操作。

### 1. 注册 Docker Hub 账号

访问 [Docker Hub](https://hub.docker.com/) 注册账号。

### 2. 登录 Docker

在终端中执行：

```bash
docker login
```
输入你的 Docker Hub 用户名和密码。

### 3. 构建镜像

```bash
# 格式：docker build -t 你的DockerHub用户名/镜像名:标签 .
# 例如：
docker build -t yourusername/vertex2openai:latest .
```

### 4. 推送镜像到 Docker Hub

```bash
docker push yourusername/vertex2openai:latest
```

### 5. 使用预构建镜像

一旦你推送了镜像，其他人（或你在服务器上）就可以直接在 `docker-compose.yml` 中使用该镜像，而不需要每次都 build：

修改 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  vertex2openai:
    # 将 build: . 替换为 image:
    image: yourusername/vertex2openai:latest
    container_name: vertex2openai
    # ... 其他配置不变
```

这样，部署时就会直接下载你构建好的镜像，速度更快。

---

## 总结

*   **代码托管**：使用 Git + GitHub。
*   **日常开发**：修改代码 -> `git add` -> `git commit` -> `git push`。
*   **服务器部署**：在服务器上 `git pull` -> 重建容器。
*   **镜像分发**（进阶）：`docker build` -> `docker push` -> 修改 `docker-compose.yml` 使用 `image`。