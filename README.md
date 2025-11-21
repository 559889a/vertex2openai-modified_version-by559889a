---
title: OpenAI to Gemini Adapter
emoji: 🔄☁️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# OpenAI to Gemini Adapter

> **Note:** This project is a modified version of the original [vertex2openai](https://github.com/gzzhongqi/vertex2openai) by gzzhongqi.
>
> **Key Modifications in this Fork:**
> *   **Enhanced Security:** Removed hardcoded passwords and enforced environment variable configuration for API keys.
> *   **Deployment Flexibility:** Added support for custom ports via `APP_PORT` environment variable.
> *   **Automated Builds:** Integrated GitHub Actions for automatic Docker image building and publishing to GitHub Container Registry (GHCR).
> *   **Health Check:** Added `/health` endpoint for container orchestration health monitoring.
> *   **Model Updates:** Updated default model lists to include the latest Gemini models (Gemini 2.0, 2.5, 3.0).

This service acts as a compatibility layer, providing an OpenAI-compatible API interface that translates requests to Google's Vertex AI Gemini models. This allows you to leverage the power of Gemini models (including Gemini 1.5 Pro and Flash) using tools and applications originally built for the OpenAI API.

## Deployment Guide

### 1. Using Pre-built Docker Image (Recommended)

This repository automatically builds and publishes Docker images to the GitHub Container Registry. You can deploy directly using this image without building it yourself.

**Image URL:** `ghcr.io/YOUR_GITHUB_USERNAME/vertex2openai-adapter:latest`
*(Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username)*

#### Docker Compose Example

Create a `docker-compose.yml` file on your server:

```yaml
version: '3.8'

services:
  vertex2openai:
    image: ghcr.io/YOUR_GITHUB_USERNAME/vertex2openai-adapter:latest
    container_name: vertex2openai
    restart: unless-stopped
    ports:
      - "${APP_PORT:-8050}:7860"
    volumes:
      - ./credentials:/app/credentials
    env_file:
      - .env
```

### 2. Configuration

Configuration is managed entirely through environment variables. You should create a `.env` file in the same directory as your `docker-compose.yml`.

**Create a `.env` file:**

```bash
# --- Essential Configuration ---

# Port to expose on the host (default: 8050)
APP_PORT=8050

# API Key to protect this adapter service (REQUIRED)
# You must set this to a strong password. Clients will use this key to authenticate.
API_KEY=your_secure_password_here

# --- Authentication (Choose One Method) ---

# Method 1: Vertex AI Express API Key (Simplest)
VERTEX_EXPRESS_API_KEY=your_vertex_express_key

# Method 2: Google Cloud Service Account JSON Content
# Paste the full content of your JSON key file here.
GOOGLE_CREDENTIALS_JSON=

# Method 3: Service Account File
# Leave GOOGLE_CREDENTIALS_JSON empty and place your .json file in the ./credentials directory.
# CREDENTIALS_DIR is set to /app/credentials by default in the container.

# --- Optional Settings ---

# Enable round-robin rotation if multiple credentials are provided
ROUNDROBIN=false

# Proxy settings (if your server needs a proxy to access Google APIs)
# PROXY_URL=http://proxy.example.com:8080
```

### 3. Health Check

The service provides a health check endpoint at `/health`. You can use this for uptime monitoring or container orchestration health probes.

*   **Endpoint:** `GET /health`
*   **Response:** `{"status": "healthy", "timestamp": 1234567890.123}`

## API Usage

### Endpoints

-   `GET /v1/models`: Lists models accessible via the configured credentials/Vertex project.
-   `POST /v1/chat/completions`: The main endpoint for generating text, mimicking the OpenAI chat completions API.
-   `GET /health`: Health check endpoint.

### Authentication

All requests to the adapter require an API key passed in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```
Replace `YOUR_API_KEY` with the value you set for the `API_KEY` environment variable.

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.
