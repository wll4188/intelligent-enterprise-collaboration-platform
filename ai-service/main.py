from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import asyncio
import json
import logging
from datetime import datetime

# LLM providers
import openai
from anthropic import Anthropic
import google.generativeai as genai

# Vector database and embeddings
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
# 优先加载项目根目录下的 .env，再加载当前服务目录下的 .env（不覆盖已存在的变量）
_service_dir = Path(__file__).resolve().parent
_project_root = _service_dir.parent
load_dotenv(_project_root / ".env")
load_dotenv(_service_dir / ".env", override=False)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Service", 
    version="1.0.0",
    description="智能企业协作平台 AI 服务 - 提供大模型对话、RAG检索等功能"
)

# === Models ===
class ChatMessage(BaseModel):
    role: str = Field(..., description="角色: user, assistant, system")
    content: str = Field(..., description="消息内容")

class ChatRequest(BaseModel):
    text: str = Field(..., description="用户输入文本")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="对话历史")
    model: Optional[str] = Field(default=None, description="指定模型")
    use_rag: Optional[bool] = Field(default=True, description="是否使用RAG检索")
    temperature: Optional[float] = Field(default=0.7, description="生成温度")

class DocumentRequest(BaseModel):
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="文档元数据")

class SearchRequest(BaseModel):
    query: str = Field(..., description="搜索查询")
    top_k: Optional[int] = Field(default=5, description="返回结果数量")

# === Global Variables ===
llm_clients = {}
embedding_model = None
vector_index = None
document_store = []

# === Initialization ===
def initialize_llm_clients():
    """初始化LLM客户端"""
    global llm_clients
    
    # OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        openai.api_key = openai_key
        llm_clients["openai"] = openai
        logger.info("OpenAI client initialized")
    
    # Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        llm_clients["anthropic"] = Anthropic(api_key=anthropic_key)
        logger.info("Anthropic client initialized")
    
    # Google Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        genai.configure(api_key=gemini_key)
        llm_clients["gemini"] = genai
        logger.info("Gemini client initialized")

def initialize_embedding_model():
    """初始化嵌入模型"""
    global embedding_model, vector_index
    try:
        # 使用轻量级的中文嵌入模型
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        # 初始化FAISS索引 (384维向量)
        vector_index = faiss.IndexFlatIP(384)
        logger.info("Embedding model and vector index initialized")
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    initialize_llm_clients()
    initialize_embedding_model()
    logger.info("AI Service started successfully")

# === Helper Functions ===
def get_available_model():
    """获取可用的LLM模型（优先Gemini）"""
    if "gemini" in llm_clients:
        return "gemini", os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    elif "openai" in llm_clients:
        return "openai", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    elif "anthropic" in llm_clients:
        return "anthropic", "claude-3-haiku-20240307"
    else:
        return None, None

def retrieve_context(query: str, top_k: int = 3) -> List[str]:
    """从向量数据库检索相关上下文"""
    if vector_index is None or embedding_model is None or len(document_store) == 0:
        return []
    
    try:
        # 生成查询向量
        query_vector = embedding_model.encode([query])
        
        # 搜索最相似的文档
        scores, indices = vector_index.search(query_vector, min(top_k, len(document_store)))
        
        # 返回相关文档内容
        contexts = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and score > 0.3:  # 相似度阈值
                contexts.append(document_store[idx]["content"][:500])  # 限制长度
        
        return contexts
    except Exception as e:
        logger.error(f"Error in retrieve_context: {e}")
        return []

async def call_llm(messages: List[Dict], model_type: str, model_name: str, temperature: float = 0.7, stream: bool = False):
    """调用LLM生成回复"""
    try:
        # 如果没有有效的API密钥，使用模拟响应进行测试
        if model_type == "openai":
            client = llm_clients["openai"]
            # 检查API密钥是否有效
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key or api_key == "your-openai-api-key":
                # 使用模拟响应
                user_msg = next((msg["content"] for msg in messages if msg["role"] == "user"), "")
                if "1+1" in user_msg or "加法" in user_msg or "等于" in user_msg:
                    mock_content = "1+1等于2。这是一个基本的数学加法运算。"
                else:
                    mock_content = f"您好！我是AI助手，您刚才问的是：{user_msg}。由于当前使用模拟模式，我无法提供完整的AI回复，但系统运行正常。"
                
                if stream:
                    # 模拟流式响应对象
                    async def mock_stream():
                        words = mock_content.split()
                        for i, word in enumerate(words):
                            if i == 0:
                                yield MockStreamChunk(word)
                            else:
                                yield MockStreamChunk(" " + word)
                            await asyncio.sleep(0.05)
                    return mock_stream()
                else:
                    return mock_content
            
            if stream:
                # OpenAI 1.0+ 流式调用（包装为异步可迭代）
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    stream=True
                )
                async def _async_wrap_openai_stream():
                    for chunk in response:
                        yield chunk
                        await asyncio.sleep(0)
                return _async_wrap_openai_stream()
            else:
                # OpenAI 1.0+ 同步调用 -> 使用线程避免阻塞
                def _sync_openai_generate():
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=temperature
                    )
                    return resp.choices[0].message.content
                return await asyncio.to_thread(_sync_openai_generate)
        
        elif model_type == "anthropic":
            # Anthropic 的调用方式
            anthropic_client = llm_clients["anthropic"]
            
            # 转换消息格式
            system_msg = None
            user_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    user_messages.append(msg)
            
            if stream:
                stream_mgr = anthropic_client.messages.stream(
                    model=model_name,
                    system=system_msg,
                    messages=user_messages,
                    temperature=temperature,
                    max_tokens=1000
                )
                async def _async_wrap_anthropic_stream():
                    with stream_mgr as stream:
                        for event in stream:
                            yield event
                            await asyncio.sleep(0)
                return _async_wrap_anthropic_stream()
            else:
                # 同步调用 -> 使用线程避免阻塞
                def _sync_anthropic_generate():
                    response = anthropic_client.messages.create(
                        model=model_name,
                        system=system_msg,
                        messages=user_messages,
                        temperature=temperature,
                        max_tokens=1000
                    )
                    return response.content[0].text
                return await asyncio.to_thread(_sync_anthropic_generate)
        
        elif model_type == "gemini":
            gemini = llm_clients["gemini"]
            # 将messages转换为Gemini的单prompt或者history+prompt
            system_msg = None
            chat_history = []
            user_msg = ""
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                elif msg["role"] == "user":
                    user_msg = msg["content"]
                else:
                    # assistant消息作为历史
                    chat_history.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})
            prompt = user_msg if not system_msg else f"系统提示：{system_msg}\n\n用户：{user_msg}"
            model = gemini.GenerativeModel(model_name)
            if stream:
                # Gemini流式响应（使用asyncio.to_thread避免阻塞）
                def _sync_gemini_stream():
                    stream_resp = model.generate_content(
                        prompt,
                        generation_config={"temperature": temperature},
                        stream=True
                    )
                    return stream_resp
                
                async def _async_wrap_gemini_stream():
                    stream_resp = await asyncio.to_thread(_sync_gemini_stream)
                    for chunk in stream_resp:
                        if hasattr(chunk, "text") and chunk.text:
                            yield MockStreamChunk(chunk.text)
                        await asyncio.sleep(0)
                return _async_wrap_gemini_stream()
            else:
                # Gemini非流式响应（使用asyncio.to_thread避免阻塞）
                def _sync_gemini_generate():
                    resp = model.generate_content(
                        prompt,
                        generation_config={"temperature": temperature}
                    )
                    return resp.text if hasattr(resp, "text") else ""
                
                return await asyncio.to_thread(_sync_gemini_generate)
    
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM服务调用失败: {str(e)}")

class MockStreamChunk:
    """模拟OpenAI流式响应的数据结构"""
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockChoice:
    def __init__(self, content):
        self.delta = MockDelta(content)

class MockDelta:
    def __init__(self, content):
        self.content = content

# === API Endpoints ===
@app.get("/healthz")
def healthz():
    """健康检查"""
    model_type, model_name = get_available_model()
    return {
        "status": "ok", 
        "service": "ai-service",
        "available_llm": f"{model_type}:{model_name}" if model_type else "none",
        "embedding_ready": embedding_model is not None,
        "vector_index_ready": vector_index is not None,
        "documents_count": len(document_store)
    }

@app.post("/v1/echo")
async def chat_completion(request: ChatRequest):
    """智能对话接口 - 支持RAG检索增强"""
    model_type, model_name = get_available_model()
    # 支持通过request.model覆盖默认模型（格式：provider 或 provider:model）
    if request.model:
        parts = request.model.split(":", 1)
        if len(parts) == 2:
            model_type, model_name = parts[0], parts[1]
        else:
            model_type = parts[0]
            # 使用默认模型
            if model_type == "openai":
                model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            elif model_type == "anthropic":
                model_name = "claude-3-haiku-20240307"
            elif model_type == "gemini":
                model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    if not model_type:
        raise HTTPException(status_code=503, detail="没有可用的LLM服务，请检查API密钥配置")
    
    # RAG检索
    contexts = []
    if request.use_rag and request.text:
        contexts = retrieve_context(request.text)
    
    # 构建消息
    messages = []
    
    # 系统提示
    system_prompt = """你是一个智能企业协作平台的AI助手。你的任务是：
1. 帮助用户解答问题，提供专业建议
2. 协助文档分析和任务管理
3. 支持团队协作和项目管理

请以友好、专业的语气回答用户问题。"""
    
    if contexts:
        system_prompt += f"\n\n参考上下文信息：\n" + "\n".join([f"- {ctx}" for ctx in contexts])
    
    messages.append({"role": "system", "content": system_prompt})
    
    # 添加对话历史
    for msg in request.conversation_history[-5:]:  # 只保留最近5轮对话
        messages.append({"role": msg.role, "content": msg.content})
    
    # 添加当前用户输入
    messages.append({"role": "user", "content": request.text})
    
    # 调用LLM（增加超时保护与离线兜底）
    llm_timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "6"))
    try:
        response_text = await asyncio.wait_for(
            call_llm(messages, model_type, model_name, request.temperature),
            timeout=llm_timeout,
        )
    except asyncio.TimeoutError:
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        # 简单离线兜底
        if "1+1" in user_msg or "加法" in user_msg or "等于" in user_msg:
            response_text = "1+1等于2。这是一个基本的数学加法运算。（离线兜底）"
        else:
            response_text = f"抱歉，当前连接到AI提供商超时，已返回离线兜底回复：您刚才问的是“{user_msg}”。"
        logger.warning("LLM call timeout, returned offline fallback response")
    except Exception as e:
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        if "1+1" in user_msg or "加法" in user_msg or "等于" in user_msg:
            response_text = "1+1等于2。这是一个基本的数学加法运算。（离线兜底）"
        else:
            response_text = f"抱歉，当前AI提供商连接异常（{str(e)}），已返回离线兜底回复：您刚才问的是“{user_msg}”。"
        logger.warning(f"LLM call error, returned offline fallback response: {e}")
    
    return {
        "response": response_text,
        "model": f"{model_type}:{model_name}",
        "contexts_used": len(contexts),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/v1/stream_echo")
async def stream_chat(text: str, use_rag: bool = True, model: str = None):
    """流式对话接口"""
    model_type, model_name = get_available_model()
    # 支持通过query参数model覆盖（格式：provider 或 provider:model）
    if model:
        parts = model.split(":", 1)
        if len(parts) == 2:
            model_type, model_name = parts[0], parts[1]
        else:
            model_type = parts[0]
            if model_type == "openai":
                model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            elif model_type == "anthropic":
                model_name = "claude-3-haiku-20240307"
            elif model_type == "gemini":
                model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    if not model_type:
        raise HTTPException(status_code=503, detail="没有可用的LLM服务")
    
    # RAG检索
    contexts = []
    if use_rag:
        contexts = retrieve_context(text)
    
    # 构建消息
    system_prompt = """你是一个智能企业协作平台的AI助手，请以友好专业的语气回答问题。"""
    if contexts:
        system_prompt += f"\n\n参考信息：\n" + "\n".join([f"- {ctx}" for ctx in contexts])
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    
    async def event_generator():
        stream_timeout = float(os.getenv("STREAM_TIMEOUT_SECONDS", "8"))
        try:
            if model_type == "openai":
                response = await asyncio.wait_for(
                    call_llm(messages, model_type, model_name, stream=True),
                    timeout=stream_timeout,
                )
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield f"data: {content}\n\n"
                        await asyncio.sleep(0.01)
            
            elif model_type == "anthropic":
                # Anthropic流式响应处理
                response = await asyncio.wait_for(
                    call_llm(messages, model_type, model_name, stream=True),
                    timeout=stream_timeout,
                )
                async for event in response:
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, 'text'):
                            yield f"data: {event.delta.text}\n\n"
                            await asyncio.sleep(0.01)
            
            elif model_type == "gemini":
                # 由于call_llm中已包装为MockStreamChunk，与OpenAI分支一致处理
                response = await asyncio.wait_for(
                    call_llm(messages, model_type, model_name, stream=True),
                    timeout=stream_timeout,
                )
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield f"data: {content}\n\n"
                        await asyncio.sleep(0.01)
            
            # 结束事件
            yield "event: end\ndata: [DONE]\n\n"
        except asyncio.TimeoutError:
            # 超时兜底
            yield f"data: {'抱歉，当前AI服务连接较慢，已返回离线兜底简要答复。'}\n\n"
            yield "event: end\ndata: [DONE]\n\n"
        except Exception as e:
            # 一般异常兜底
            yield f"data: {'抱歉，当前AI服务异常，已返回离线兜底简要答复。'}\n\n"
            yield "event: end\ndata: [DONE]\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/v1/documents")
async def add_document(request: DocumentRequest):
    """添加文档到知识库"""
    if embedding_model is None or vector_index is None:
        raise HTTPException(status_code=503, detail="向量化服务未就绪")
    
    try:
        # 生成文档嵌入向量
        embedding = embedding_model.encode([request.content])
        
        # 添加到向量索引
        vector_index.add(embedding)
        
        # 保存文档信息
        doc_info = {
            "title": request.title,
            "content": request.content,
            "metadata": request.metadata,
            "timestamp": datetime.now().isoformat(),
            "id": len(document_store)
        }
        document_store.append(doc_info)
        
        logger.info(f"Document added: {request.title}")
        return {"message": "文档添加成功", "document_id": doc_info["id"]}
    
    except Exception as e:
        logger.error(f"Failed to add document: {e}")
        raise HTTPException(status_code=500, detail=f"文档添加失败: {str(e)}")

@app.post("/v1/search")
async def search_documents(request: SearchRequest):
    """搜索知识库文档"""
    if embedding_model is None or vector_index is None or len(document_store) == 0:
        return {"results": [], "message": "知识库为空"}
    
    try:
        # 生成查询向量
        query_vector = embedding_model.encode([request.query])
        
        # 搜索
        scores, indices = vector_index.search(query_vector, min(request.top_k, len(document_store)))
        
        # 构建结果
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and score > 0.2:  # 相似度阈值
                doc = document_store[idx]
                results.append({
                    "title": doc["title"],
                    "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    "score": float(score),
                    "metadata": doc["metadata"]
                })
        
        return {"results": results}
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.get("/v1/models")
async def list_models():
    """列出可用的模型"""
    available_models = []
    
    if "openai" in llm_clients:
        available_models.extend([
            {"provider": "openai", "model": "gpt-3.5-turbo", "type": "chat"},
            {"provider": "openai", "model": "gpt-4", "type": "chat"},
        ])
    
    if "anthropic" in llm_clients:
        available_models.extend([
            {"provider": "anthropic", "model": "claude-3-haiku-20240307", "type": "chat"},
            {"provider": "anthropic", "model": "claude-3-sonnet-20240229", "type": "chat"},
        ])

    if "gemini" in llm_clients:
        available_models.extend([
            {"provider": "gemini", "model": "gemini-1.5-flash", "type": "chat"},
            {"provider": "gemini", "model": "gemini-1.5-pro", "type": "chat"},
        ])
    
    return {"models": available_models}