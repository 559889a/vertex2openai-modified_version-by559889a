import time
from fastapi import APIRouter, Depends, Request
from typing import List, Dict, Any
from auth import get_api_key
from model_loader import get_native_models, refresh_native_models_cache, get_alias_models

router = APIRouter()

@router.get("/v1/models")
async def list_models(fastapi_request: Request, api_key: str = Depends(get_api_key)):
    """返回简洁的模型列表，与 Gemini 端口共用"""
    credential_manager = fastapi_request.app.state.credential_manager
    express_key_manager = fastapi_request.app.state.express_key_manager

    # 获取原生模型列表
    native_models = await get_native_models(credential_manager, express_key_manager)
    
    if not native_models:
        await refresh_native_models_cache(credential_manager, express_key_manager)
        native_models = await get_native_models(credential_manager, express_key_manager)
    
    current_time = int(time.time())
    
    # 直接返回基础模型列表，不添加任何前后缀
    model_list: List[Dict[str, Any]] = []
    for model_id in sorted(set(native_models)):
        model_list.append({
            "id": model_id,
            "object": "model",
            "created": current_time,
            "owned_by": "google",
            "permission": [],
            "root": model_id,
            "parent": None
        })
    
    # 添加别名模型
    alias_models = get_alias_models()
    for alias_name, alias_config in alias_models.items():
        model_list.append({
            "id": alias_name,
            "object": "model",
            "created": current_time,
            "owned_by": "google",
            "permission": [],
            "root": alias_config["base_model"],
            "parent": alias_config["base_model"]
        })

    return {"object": "list", "data": model_list}
