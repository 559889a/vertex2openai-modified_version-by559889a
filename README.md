---
title: OpenAI to Gemini Adapter
emoji: 🔄☁️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---
[中文文档](README_zh.md) | [English](README.md)


# OpenAI to Gemini Adapter

> **Note:** This project is a heavily modified version of the original [vertex2openai](https://github.com/gzzhongqi/vertex2openai) by gzzhongqi.
>
> **Major Feature Updates & Modifications:**
> *   **Gemini Native Format Support:** Added full support for Gemini's native API format, including built-in Google Search grounding and visual capabilities.
> *   **Enhanced Vision Support:** OpenAI-compatible endpoints now support visual inputs (image analysis).
> *   **Thinking Models:** Introduced `gemini-3-pro-preview-high` and `gemini-3-pro-preview-low` alias models, corresponding to different reasoning depths (thinking levels).
> *   **Prompt Engineering:** Completely overhauled prompt processing logic for better compatibility.
> *   **Security & Deployment:** Removed hardcoded secrets, added `APP_PORT` configuration, and integrated GitHub Actions for automated Docker builds.
> *   **Health Monitoring:** Added `/health` endpoint.

This service acts as a compatibility layer, providing an OpenAI-compatible API interface that translates requests to Google's Vertex AI Gemini models. This allows you to leverage the power of Gemini models (including Gemini 1.5 Pro, Flash, and the new Gemini 3.0 series) using tools and applications originally built for the OpenAI API.

## Known Issues & Limitations

*   **OpenAI Format Search:** Calling search tools via the OpenAI-compatible format is currently unstable or non-functional.
*   **Gemini Format Context:** When using the Gemini native format, web page context retrieval may fail.
*   **Chain of Thought (CoT):** The Gemini native format currently has issues returning the full Chain of Thought (CoT) reasoning process.
*   **Gemini 3.0 Pro:** It appears that `gemini-3-pro` models may not consistently return reasoning chains via the API (based on current Google documentation/behavior).
*   **Image Generation:** Image generation models have not been fully tested; stability is not guaranteed.

## Deployment Guide

### 1. Using Pre-built Docker Image (Recommended)

This repository automatically builds and publishes Docker images to the GitHub Container Registry. You can deploy directly using this image without building it yourself.

**Image URL:** `ghcr.io/559889a/vertex2openai-modified_version-by559889a:latest`

#### Docker Compose Example

Create a `docker-compose.yml` file on your server:

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
-   `POST /gemini/v1beta/models/{model}:generateContent`: Gemini native API endpoint.
-   `POST /gemini/v1beta/models/{model}:streamGenerateContent`: Gemini native streaming API endpoint.
-   `GET /health`: Health check endpoint.

### Authentication

All requests to the adapter require an API key passed in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```
Replace `YOUR_API_KEY` with the value you set for the `API_KEY` environment variable.

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.
