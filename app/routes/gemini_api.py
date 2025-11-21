import base64
import json
import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Request, Path, Query, HTTPException, Header
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from google.genai import types
from google import genai

from auth import get_api_key, validate_api_key
from api_helpers import create_openai_error_response
from project_id_discovery import discover_project_id
from config import API_KEY

router = APIRouter(prefix="/gemini/v1beta", tags=["Gemini Native API"])


async def get_gemini_api_key(
    key: Optional[str] = Query(None, description="API key"),
    x_goog_api_key: Optional[str] = Header(None, alias="x-goog-api-key"),
    authorization: Optional[str] = Header(None)
) -> str:
    """支持 Gemini 风格的 API key 认证"""
    api_key = None
    
    # 优先检查 URL 参数 key
    if key:
        api_key = key
    # 其次检查 x-goog-api-key 头部
    elif x_goog_api_key:
        api_key = x_goog_api_key
    # 最后检查 Authorization 头部
    elif authorization and authorization.startswith("Bearer "):
        api_key = authorization.replace("Bearer ", "")
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Use ?key=YOUR_KEY, x-goog-api-key header, or Authorization: Bearer YOUR_KEY"
        )
    
    if not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


# Gemini 原生请求模型
class GeminiPart(BaseModel):
    text: Optional[str] = None
    inline_data: Optional[Dict[str, Any]] = None
    function_call: Optional[Dict[str, Any]] = None
    function_response: Optional[Dict[str, Any]] = None


class GeminiContent(BaseModel):
    role: Optional[str] = None
    parts: List[Dict[str, Any]]


class GeminiGenerationConfig(BaseModel):
    temperature: Optional[float] = None
    topP: Optional[float] = None
    topK: Optional[int] = None
    maxOutputTokens: Optional[int] = None
    stopSequences: Optional[List[str]] = None
    candidateCount: Optional[int] = None
    seed: Optional[int] = None
    responseMimeType: Optional[str] = None
    responseSchema: Optional[Dict[str, Any]] = None
    presencePenalty: Optional[float] = None
    frequencyPenalty: Optional[float] = None


class GeminiSafetySettings(BaseModel):
    category: str
    threshold: str


class GeminiToolConfig(BaseModel):
    functionCallingConfig: Optional[Dict[str, Any]] = None


class GeminiRequest(BaseModel):
    contents: List[GeminiContent]
    systemInstruction: Optional[GeminiContent] = None
    generationConfig: Optional[GeminiGenerationConfig] = None
    safetySettings: Optional[List[GeminiSafetySettings]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    toolConfig: Optional[GeminiToolConfig] = None
    cachedContent: Optional[str] = None

    class Config:
        extra = "allow"


def build_generation_config(request: GeminiRequest) -> Dict[str, Any]:
    """构建 Gemini SDK 的配置字典"""
    config: Dict[str, Any] = {}
    
    if request.generationConfig:
        gc = request.generationConfig
        if gc.temperature is not None:
            config["temperature"] = gc.temperature
        if gc.topP is not None:
            config["top_p"] = gc.topP
        if gc.topK is not None:
            config["top_k"] = gc.topK
        if gc.maxOutputTokens is not None:
            config["max_output_tokens"] = gc.maxOutputTokens
        if gc.stopSequences:
            config["stop_sequences"] = gc.stopSequences
        if gc.candidateCount is not None:
            config["candidate_count"] = gc.candidateCount
        if gc.seed is not None:
            config["seed"] = gc.seed
        if gc.responseMimeType:
            config["response_mime_type"] = gc.responseMimeType
        if gc.responseSchema:
            config["response_schema"] = gc.responseSchema
    
    # 安全设置
    if request.safetySettings:
        config["safety_settings"] = [
            types.SafetySetting(category=s.category, threshold=s.threshold)
            for s in request.safetySettings
        ]
    else:
        # 默认安全设置
        safety_threshold = "BLOCK_NONE"
        config["safety_settings"] = [
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold=safety_threshold),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold=safety_threshold),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold=safety_threshold),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold=safety_threshold),
            types.SafetySetting(category="HARM_CATEGORY_CIVIC_INTEGRITY", threshold=safety_threshold),
        ]
    
    # System instruction
    if request.systemInstruction:
        parts_text = []
        for part in request.systemInstruction.parts:
            if "text" in part:
                parts_text.append(part["text"])
        if parts_text:
            config["system_instruction"] = "\n".join(parts_text)
    
    # Tools
    if request.tools:
        config["tools"] = request.tools
    
    # Tool config
    if request.toolConfig and request.toolConfig.functionCallingConfig:
        config["tool_config"] = {
            "function_calling_config": request.toolConfig.functionCallingConfig
        }
    
    return config


def build_contents(request: GeminiRequest) -> List[types.Content]:
    """构建 Gemini SDK 的 contents 列表"""
    contents = []
    for content in request.contents:
        parts = []
        for part in content.parts:
            if "text" in part:
                parts.append(types.Part.from_text(text=part["text"]))
            elif "inlineData" in part or "inline_data" in part:
                data = part.get("inlineData") or part.get("inline_data")
                if data:
                    parts.append(types.Part.from_bytes(
                        data=data.get("data", ""),
                        mime_type=data.get("mimeType", data.get("mime_type", "application/octet-stream"))
                    ))
            elif "functionCall" in part or "function_call" in part:
                fc = part.get("functionCall") or part.get("function_call")
                if fc:
                    parts.append(types.Part.from_function_call(
                        name=fc.get("name", ""),
                        args=fc.get("args", {})
                    ))
            elif "functionResponse" in part or "function_response" in part:
                fr = part.get("functionResponse") or part.get("function_response")
                if fr:
                    parts.append(types.Part.from_function_response(
                        name=fr.get("name", ""),
                        response=fr.get("response", {})
                    ))
        
        role = content.role or "user"
        contents.append(types.Content(role=role, parts=parts))
    
    return contents


def convert_bytes_to_base64(obj: Any) -> Any:
    """递归将 bytes 转为 base64 编码字符串"""
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, dict):
        return {k: convert_bytes_to_base64(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_bytes_to_base64(item) for item in obj]
    return obj


def convert_response_to_gemini_format(response: Any, model_name: str) -> Dict[str, Any]:
    """将 SDK 响应转换为 Gemini API 原生格式 - 使用 SDK 自带的序列化"""
    try:
        # 尝试使用 SDK 的 model_dump 或 to_dict 方法
        if hasattr(response, "model_dump"):
            result = response.model_dump(exclude_none=True)
            return convert_bytes_to_base64(result)
        elif hasattr(response, "to_dict"):
            result = response.to_dict()
            return convert_bytes_to_base64(result)
        elif hasattr(response, "_pb"):
            # Protobuf 响应
            from google.protobuf.json_format import MessageToDict
            result = MessageToDict(response._pb, preserving_proto_field_name=False)
            return convert_bytes_to_base64(result)
    except Exception as e:
        print(f"WARNING: SDK serialization failed: {e}, using manual conversion")
    
    # 回退到手动转换
    result = {
        "candidates": [],
        "usageMetadata": {}
    }
    
    if hasattr(response, "candidates") and response.candidates:
        for candidate in response.candidates:
            cand_dict = {
                "content": {
                    "role": "model",
                    "parts": []
                },
                "finishReason": "STOP"
            }
            
            if hasattr(candidate, "finish_reason") and candidate.finish_reason:
                finish_reason = str(candidate.finish_reason)
                if "." in finish_reason:
                    finish_reason = finish_reason.split(".")[-1]
                cand_dict["finishReason"] = finish_reason
            
            if hasattr(candidate, "content") and candidate.content:
                if hasattr(candidate.content, "role"):
                    cand_dict["content"]["role"] = candidate.content.role or "model"
                
                if hasattr(candidate.content, "parts") and candidate.content.parts:
                    for part in candidate.content.parts:
                        part_dict = {}
                        
                        # 尝试使用 part 的原生序列化
                        if hasattr(part, "model_dump"):
                            try:
                                part_dict = part.model_dump(exclude_none=True)
                            except:
                                pass
                        
                        # 如果原生序列化失败或为空，手动处理
                        if not part_dict:
                            if hasattr(part, "text") and part.text is not None:
                                part_dict["text"] = part.text
                            if hasattr(part, "thought") and part.thought:
                                part_dict["thought"] = True
                            if hasattr(part, "thought_signature") and part.thought_signature:
                                # bytes 需要转为 base64 编码
                                sig = part.thought_signature
                                if isinstance(sig, bytes):
                                    part_dict["thoughtSignature"] = base64.b64encode(sig).decode('utf-8')
                                else:
                                    part_dict["thoughtSignature"] = sig
                            if hasattr(part, "function_call") and part.function_call:
                                fc = part.function_call
                                part_dict["functionCall"] = {
                                    "name": fc.name if hasattr(fc, "name") else "",
                                    "args": dict(fc.args) if hasattr(fc, "args") and fc.args else {}
                                }
                            if hasattr(part, "inline_data") and part.inline_data:
                                part_dict["inlineData"] = {
                                    "mimeType": part.inline_data.mime_type,
                                    "data": part.inline_data.data
                                }
                        
                        if part_dict:
                            cand_dict["content"]["parts"].append(part_dict)
            
            # Safety ratings
            if hasattr(candidate, "safety_ratings") and candidate.safety_ratings:
                cand_dict["safetyRatings"] = [
                    {
                        "category": str(sr.category).split(".")[-1] if "." in str(sr.category) else str(sr.category),
                        "probability": str(sr.probability).split(".")[-1] if hasattr(sr, "probability") and "." in str(sr.probability) else "NEGLIGIBLE"
                    }
                    for sr in candidate.safety_ratings
                ]
            
            result["candidates"].append(cand_dict)
    
    # Usage metadata
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        um = response.usage_metadata
        result["usageMetadata"] = {
            "promptTokenCount": getattr(um, "prompt_token_count", 0),
            "candidatesTokenCount": getattr(um, "candidates_token_count", 0),
            "totalTokenCount": getattr(um, "total_token_count", 0)
        }
        if hasattr(um, "thoughts_token_count") and um.thoughts_token_count:
            result["usageMetadata"]["thoughtsTokenCount"] = um.thoughts_token_count
    
    if hasattr(response, "model_version") and response.model_version:
        result["modelVersion"] = response.model_version
    
    return result


async def get_gemini_client(
    fastapi_request: Request,
    model_name: str
) -> tuple[Any, str]:
    """获取 Gemini 客户端 - 智能选择认证方式"""
    credential_manager = fastapi_request.app.state.credential_manager
    express_key_manager = fastapi_request.app.state.express_key_manager
    
    EXPRESS_PREFIX = "[EXPRESS] "
    is_express_explicit = model_name.startswith(EXPRESS_PREFIX)
    
    if is_express_explicit:
        actual_model = model_name[len(EXPRESS_PREFIX):]
    else:
        actual_model = model_name
    
    has_sa_creds = credential_manager.get_total_credentials() > 0
    has_express_key = express_key_manager.get_total_keys() > 0
    
    # 决定使用哪种认证方式
    # 1. 明确指定 EXPRESS 前缀 -> 使用 Express Key
    # 2. 未指定前缀 -> 优先 SA，如果没有则回退到 Express
    use_express = is_express_explicit or (not has_sa_creds and has_express_key)
    
    if use_express:
        if not has_express_key:
            raise ValueError("Express API key required but not configured")
        
        key_tuple = express_key_manager.get_express_api_key()
        if not key_tuple:
            raise ValueError("No Express API key available")
        
        _, key_val = key_tuple
        
        if "gemini-2.5-pro" in actual_model or "gemini-2.5-flash" in actual_model or "gemini-3" in actual_model:
            project_id = await discover_project_id(key_val)
            base_url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global"
            client = genai.Client(
                vertexai=True,
                api_key=key_val,
                http_options=types.HttpOptions(base_url=base_url)
            )
            client._api_client._http_options.api_version = None
        else:
            client = genai.Client(vertexai=True, api_key=key_val)
        
        print(f"INFO: Using Express API key for model: {actual_model}")
        return client, actual_model
    else:
        # 使用 SA 凭证
        if not has_sa_creds:
            raise ValueError("No authentication available (no SA credentials or Express API keys)")
        
        credentials, project_id = credential_manager.get_credentials()
        
        if not credentials or not project_id:
            raise ValueError("No SA credentials available")
        
        client = genai.Client(
            vertexai=True,
            credentials=credentials,
            project=project_id,
            location="global"
        )
        
        print(f"INFO: Using SA credentials for model: {actual_model}")
        return client, actual_model


@router.post("/models/{model}:generateContent")
async def generate_content(
    fastapi_request: Request,
    model: str = Path(..., description="Model name"),
    alt: Optional[str] = Query(None, description="Response format"),
    api_key: str = Depends(get_gemini_api_key)
):
    """Gemini generateContent 端点 - 非流式"""
    try:
        body = await fastapi_request.json()
        request = GeminiRequest(**body)
        
        client, actual_model = await get_gemini_client(fastapi_request, model)
        
        gen_config = build_generation_config(request)
        contents = build_contents(request)
        
        print(f"INFO: Gemini native generateContent for model: {actual_model}")
        
        response = await client.aio.models.generate_content(
            model=actual_model,
            contents=contents,
            config=gen_config
        )
        
        result = convert_response_to_gemini_format(response, actual_model)
        return JSONResponse(content=result)
        
    except ValueError as ve:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": 400, "message": str(ve), "status": "INVALID_ARGUMENT"}}
        )
    except Exception as e:
        print(f"ERROR: Gemini generateContent failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": 500, "message": str(e), "status": "INTERNAL"}}
        )


@router.post("/models/{model}:streamGenerateContent")
async def stream_generate_content(
    fastapi_request: Request,
    model: str = Path(..., description="Model name"),
    alt: Optional[str] = Query(None, description="Response format (sse for streaming)"),
    api_key: str = Depends(get_gemini_api_key)
):
    """Gemini streamGenerateContent 端点 - 流式"""
    try:
        body = await fastapi_request.json()
        request = GeminiRequest(**body)
        
        client, actual_model = await get_gemini_client(fastapi_request, model)
        
        gen_config = build_generation_config(request)
        contents = build_contents(request)
        
        print(f"INFO: Gemini native streamGenerateContent for model: {actual_model}")
        
        async def stream_generator():
            try:
                stream = await client.aio.models.generate_content_stream(
                    model=actual_model,
                    contents=contents,
                    config=gen_config
                )
                
                chunk_count = 0
                async for chunk in stream:
                    chunk_count += 1
                    # 调试：打印原始响应结构
                    if chunk_count == 1:
                        print(f"DEBUG: First chunk type: {type(chunk)}")
                        print(f"DEBUG: First chunk dir: {[a for a in dir(chunk) if not a.startswith('_')]}")
                        if hasattr(chunk, 'candidates') and chunk.candidates:
                            print(f"DEBUG: candidates count: {len(chunk.candidates)}")
                            if chunk.candidates[0]:
                                cand = chunk.candidates[0]
                                print(f"DEBUG: candidate dir: {[a for a in dir(cand) if not a.startswith('_')]}")
                                if hasattr(cand, 'content') and cand.content:
                                    print(f"DEBUG: content dir: {[a for a in dir(cand.content) if not a.startswith('_')]}")
                                    if hasattr(cand.content, 'parts') and cand.content.parts:
                                        print(f"DEBUG: parts count: {len(cand.content.parts)}")
                                        for i, p in enumerate(cand.content.parts):
                                            print(f"DEBUG: part[{i}] dir: {[a for a in dir(p) if not a.startswith('_')]}")
                                            print(f"DEBUG: part[{i}] raw: {p}")
                    
                    chunk_data = convert_response_to_gemini_format(chunk, actual_model)
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                
                print(f"DEBUG: Stream completed, total chunks: {chunk_count}")
                
            except Exception as e:
                print(f"ERROR: Stream error: {e}")
                import traceback
                traceback.print_exc()
                error_data = {"error": {"code": 500, "message": str(e), "status": "INTERNAL"}}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream"
        )
        
    except ValueError as ve:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": 400, "message": str(ve), "status": "INVALID_ARGUMENT"}}
        )
    except Exception as e:
        print(f"ERROR: Gemini streamGenerateContent failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": 500, "message": str(e), "status": "INTERNAL"}}
        )


@router.get("/models")
async def list_models(
    fastapi_request: Request,
    api_key: str = Depends(get_gemini_api_key)
):
    """列出可用的 Gemini 模型"""
    try:
        from model_loader import get_native_models, refresh_native_models_cache
        
        credential_manager = fastapi_request.app.state.credential_manager
        express_key_manager = fastapi_request.app.state.express_key_manager
        
        native_models = await get_native_models(credential_manager, express_key_manager)
        
        # 如果缓存为空，尝试刷新
        if not native_models:
            await refresh_native_models_cache(credential_manager, express_key_manager)
            native_models = await get_native_models(credential_manager, express_key_manager)
        
        models = []
        for model_id in native_models:
            models.append({
                "name": f"models/{model_id}",
                "displayName": model_id,
                "description": f"Gemini model: {model_id}",
                "supportedGenerationMethods": ["generateContent", "streamGenerateContent"]
            })
        
        return JSONResponse(content={"models": models})
        
    except Exception as e:
        print(f"ERROR: List models failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": 500, "message": str(e), "status": "INTERNAL"}}
        )


@router.get("/models/{model}")
async def get_model(
    model: str = Path(..., description="Model name"),
    api_key: str = Depends(get_gemini_api_key)
):
    """获取模型信息"""
    return JSONResponse(content={
        "name": f"models/{model}",
        "displayName": model,
        "description": f"Gemini model: {model}",
        "supportedGenerationMethods": ["generateContent", "streamGenerateContent"]
    })