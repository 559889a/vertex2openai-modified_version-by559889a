---
title: OpenAI to Gemini Adapter
emoji: 🔄☁️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8050
---
[中文文档](README_zh.md) | [English](README.md)


# OpenAI to Gemini Adapter

> **Note:** This project is a heavily modified version of the original [vertex2openai](https://github.com/gzzhongqi/vertex2openai) by gzzhongqi.
>
> **Major Feature Updates & Modifications:**
> *   **Image Generation Models:** Now supports Gemini image generation models including `gemini-3-pro-image-preview` (Big Banana 🍌) and `gemini-2.5-flash-image` (Small Banana 🍌).
> *   **Gemini Native Format Support:** Added full support for Gemini's native API format, including built-in Google Search grounding and visual capabilities.
> *   **Enhanced Vision Support:** OpenAI-compatible endpoints now support visual inputs (image analysis).
> *   **Thinking Models:** Introduced `gemini-3-pro-preview-high` and `gemini-3-pro-preview-low` alias models, corresponding to different reasoning depths (thinking levels).
> *   **Windows One-Click Launch:** Optimized Windows startup script (`run_windows.bat`) for easy deployment on Windows platforms.
> *   **Prompt Engineering:** Completely overhauled prompt processing logic for better compatibility.
> *   **Security & Deployment:** Removed hardcoded secrets, added `APP_PORT` configuration, and integrated GitHub Actions for automated Docker builds.
> *   **Health Monitoring:** Added `/health` endpoint.

This service acts as a compatibility layer, providing an OpenAI-compatible API interface that translates requests to Google's Vertex AI Gemini models. This allows you to leverage the power of Gemini models (including Gemini 2.0 Flash, Gemini 2.5 Flash/Pro, and the latest Gemini 3.0 Pro series) using tools and applications originally built for the OpenAI API.

> **Important Note on Authentication Methods:**
> This project has been primarily developed and optimized for **Vertex Express API Key** mode. The Service Account JSON credential authentication has **not been thoroughly tested** and its reliability is **unknown**. We recommend using Vertex Express API Key for the best experience.

## Known Issues & Limitations

### 🔴 Critical Issue: Linux Platform Limitation
*   **Auto-Retry Failure on Linux:** The automatic retry mechanism is currently broken on Linux systems. When API calls fail, the service may not automatically retry as expected. This issue does not affect Windows platforms, where auto-retry works normally. **Linux users should manually retry failed requests.**

### Other Known Issues
*   **OpenAI Format Search:** Calling search tools via the OpenAI-compatible format is currently unstable or non-functional.
*   **Gemini Format Context:** When using the Gemini native format, web page context retrieval may fail.
*   **Chain of Thought (CoT):** The Gemini native format currently has issues returning the full Chain of Thought (CoT) reasoning process.
*   **Gemini 3.0 Pro:** It appears that `gemini-3-pro` models may not consistently return reasoning chains via the API (based on current Google documentation/behavior).
*   **Image Generation:** Image generation models are newly added. Tested with Cherry Studio on both OpenAI-compatible and Gemini native endpoints. Some edge cases may still have issues.

## Deployment Guide

### 1. Windows One-Click Launch (Easiest for Windows Users)

For Windows users, we provide a one-click startup script that automatically sets up the environment and launches the service.

**Requirements:**
- Python 3.11 or higher
- Windows 10 or later

**Steps:**
1. Download or clone this repository
2. Double-click `run_windows.bat`
3. On first run, the script will:
   - Create a `.env` file from `.env.example`
   - Open the `.env` file for you to configure
   - Set up a Python virtual environment
   - Install all dependencies automatically
4. Edit the `.env` file to set your `API_KEY` and authentication credentials
5. Run `run_windows.bat` again to start the service

The service will be available at `http://localhost:8050` (or your configured `APP_PORT`).

### 2. Using Pre-built Docker Image (Recommended for Linux/Server)

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
      - "${APP_PORT:-8050}:8050"
    volumes:
      - ./credentials:/app/credentials
    env_file:
      - .env
```

### 3. Configuration

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

# --- GCP Configuration (Optional but recommended for Express Mode) ---
# GCP_PROJECT_ID=your-gcp-project-id
# GCP_LOCATION=us-central1

# --- Optional Settings ---

# Enable round-robin rotation if multiple credentials are provided
ROUNDROBIN=false

# Proxy settings (if your server needs a proxy to access Google APIs)
# PROXY_URL=http://proxy.example.com:8080
```

### 4. Health Check

## Supported Models

### Base Models (12 models)

The following Gemini models are currently supported:

1. **gemini-2.0-flash** - Fast response model
2. **gemini-2.0-flash-001** - Fast response model (version 001)
3. **gemini-2.0-flash-lite** - Lightweight fast model
4. **gemini-2.0-flash-lite-001** - Lightweight fast model (version 001)
5. **gemini-2.5-flash** - Enhanced fast model
6. **gemini-2.5-flash-image** 🆕🍌 - Small Banana image generation model
7. **gemini-2.5-flash-image-preview** 🆕🍌 - Small Banana image preview
8. **gemini-2.5-flash-lite-preview-09-2025** 🆕 - September 2025 lite preview
9. **gemini-2.5-flash-preview-09-2025** 🆕 - September 2025 preview
10. **gemini-2.5-pro** - Pro model
11. **gemini-3-pro-image-preview** 🆕🍌 - Big Banana image generation model
12. **gemini-3-pro-preview** - Latest preview model

### Alias Models (2 models)

Special models with pre-configured thinking levels:

- **gemini-3-pro-preview-high** - High thinking level (maximum reasoning depth)
- **gemini-3-pro-preview-low** - Low thinking level (minimal latency)

**Note:** 🆕 indicates newly added models in this release. 🍌 indicates image generation capabilities.

**Testing Status:** Image generation models have been tested with Cherry Studio on both OpenAI-compatible and Gemini native endpoints.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and updates.

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
