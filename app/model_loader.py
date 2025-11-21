import httpx
import asyncio
import json
from typing import List, Dict, Optional, Any

from google import genai
from google.genai import types

import config as app_config

_model_cache: Optional[Dict[str, List[str]]] = None
_native_model_cache: Optional[List[str]] = None
_cache_lock = asyncio.Lock()

# 默认支持的 Gemini 模型列表（当 API 不可用时使用）
DEFAULT_GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-lite-001",
    "gemini-2.0-flash-001",
    "gemini-2.5-flash",
    "gemini-2.5-flash-preview-04-17",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-flash-preview-native-audio-dialog",
    "gemini-2.5-pro",
    "gemini-2.5-pro-preview-05-06",
    "gemini-2.5-pro-preview-06-05",
    "gemini-3-pro-preview",
    "gemini-3-pro-image-generation-preview",
]

# 别名模型配置 - 自动注入 thinking 配置
ALIAS_MODELS = {
    "gemini-3-pro-preview-high": {
        "base_model": "gemini-3-pro-preview",
        "thinking_level": "high",
        "description": "Gemini 3 Pro with high thinking level (maximum reasoning depth)"
    },
    "gemini-3-pro-preview-low": {
        "base_model": "gemini-3-pro-preview",
        "thinking_level": "low",
        "description": "Gemini 3 Pro with low thinking level (minimal latency)"
    }
}


def get_alias_models() -> dict:
    """返回别名模型配置"""
    return ALIAS_MODELS


async def fetch_native_models_with_credentials(credential_manager, express_key_manager) -> List[str]:
    """
    使用凭证从 Vertex AI API 获取模型列表，返回模型 ID 列表
    Express API Key 不支持 models.list()，所以优先使用 SA 凭证
    """
    models = []
    
    # 优先尝试使用 SA 凭证（因为 Express Key 不支持 models.list）
    if credential_manager and credential_manager.get_total_credentials() > 0:
        credentials, project_id = credential_manager.get_credentials()
        if credentials and project_id:
            try:
                client = genai.Client(
                    vertexai=True,
                    credentials=credentials,
                    project=project_id,
                    location="global"
                )
                for model in client.models.list():
                    model_name = model.name if hasattr(model, 'name') else str(model)
                    if model_name.startswith("models/"):
                        model_name = model_name[7:]
                    if "gemini" in model_name.lower():
                        models.append(model_name)
                print(f"Fetched {len(models)} models using SA credentials")
                return list(set(models))
            except Exception as e:
                print(f"WARNING: Failed to fetch models with SA credentials: {e}")
    
    # Express API Key 不支持 models.list()，使用默认模型列表
    if express_key_manager and express_key_manager.get_total_keys() > 0:
        print(f"INFO: Express API Key does not support models.list(), using default model list ({len(DEFAULT_GEMINI_MODELS)} models)")
        return DEFAULT_GEMINI_MODELS.copy()
    
    # 如果都没有，返回默认列表
    print(f"INFO: No credentials available, using default model list")
    return DEFAULT_GEMINI_MODELS.copy()


async def fetch_and_parse_models_config() -> Optional[Dict[str, List[str]]]:
    """
    Fetches the model configuration JSON from the URL specified in app_config.
    Parses it and returns a dictionary with 'vertex_models' and 'vertex_express_models'.
    Returns None if fetching or parsing fails.
    """
    if not app_config.MODELS_CONFIG_URL:
        print("INFO: MODELS_CONFIG_URL is not set, will use native API to fetch models.")
        return None

    print(f"Fetching model configuration from: {app_config.MODELS_CONFIG_URL}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(app_config.MODELS_CONFIG_URL)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and \
               "vertex_models" in data and isinstance(data["vertex_models"], list) and \
               "vertex_express_models" in data and isinstance(data["vertex_express_models"], list):
                print("Successfully fetched and parsed model configuration.")
                return {
                    "vertex_models": data["vertex_models"],
                    "vertex_express_models": data["vertex_express_models"]
                }
            else:
                print(f"ERROR: Fetched model configuration has an invalid structure: {data}")
                return None
    except httpx.RequestError as e:
        print(f"ERROR: HTTP request failed while fetching model configuration: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to decode JSON from model configuration: {e}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while fetching/parsing model configuration: {e}")
        return None


async def get_models_config() -> Dict[str, List[str]]:
    """
    Returns the cached model configuration.
    If not cached, fetches and caches it.
    Returns a default empty structure if fetching fails.
    """
    global _model_cache
    async with _cache_lock:
        if _model_cache is None:
            print("Model cache is empty. Fetching configuration...")
            _model_cache = await fetch_and_parse_models_config()
            if _model_cache is None:
                print("WARNING: Using default empty model configuration due to fetch/parse failure.")
                _model_cache = {"vertex_models": [], "vertex_express_models": []}
    return _model_cache


async def get_vertex_models() -> List[str]:
    config = await get_models_config()
    return config.get("vertex_models", [])


async def get_vertex_express_models() -> List[str]:
    config = await get_models_config()
    return config.get("vertex_express_models", [])


async def get_native_models(credential_manager=None, express_key_manager=None) -> List[str]:
    """
    从 Vertex AI API 原生获取模型列表
    优先使用缓存，如果缓存为空则从 API 获取
    """
    global _native_model_cache
    async with _cache_lock:
        if _native_model_cache is None:
            _native_model_cache = await fetch_native_models_with_credentials(
                credential_manager, express_key_manager
            )
    return _native_model_cache or []


async def refresh_native_models_cache(credential_manager=None, express_key_manager=None) -> bool:
    """
    强制刷新原生模型列表缓存
    """
    global _native_model_cache
    async with _cache_lock:
        _native_model_cache = await fetch_native_models_with_credentials(
            credential_manager, express_key_manager
        )
        return len(_native_model_cache) > 0


async def refresh_models_config_cache() -> bool:
    """
    Forces a refresh of the model configuration cache.
    Returns True if successful, False otherwise.
    """
    global _model_cache
    print("Attempting to refresh model configuration cache...")
    async with _cache_lock:
        new_config = await fetch_and_parse_models_config()
        if new_config is not None:
            _model_cache = new_config
            print("Model configuration cache refreshed successfully.")
            return True
        else:
            print("ERROR: Failed to refresh model configuration cache.")
            return False