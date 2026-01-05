from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import httpx
from .api.routes import router
from .config import settings
from .services.fava_service import FavaService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：启动Fava服务
    print("Starting Fava service...")
    FavaService.start(port=5000)
    yield
    # 关闭时：停止Fava服务
    print("Stopping Fava service...")
    FavaService.stop()

app = FastAPI(
    title="Beancount Accounting Agent API",
    description="API for intelligent accounting with VLM-powered bill recognition",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Beancount Accounting Agent API",
        "version": "1.0.0",
        "vlm_provider": settings.VLM_PROVIDER
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.api_route("/api/fava/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def fava_proxy(path: str, request: Request):
    """Fava 服务代理"""
    if not FavaService.is_running():
        return {"error": "Fava service is not running"}, 503
    
    fava_url = f"http://localhost:5000/{path}"
    
    async with httpx.AsyncClient() as client:
        # 转发请求
        headers = dict(request.headers)
        headers.pop("host", None)
        
        response = await client.request(
            method=request.method,
            url=fava_url,
            headers=headers,
            params=request.query_params,
            content=await request.body(),
        )
        
        # 返回响应
        return StreamingResponse(
            response.aiter_bytes(),
            status_code=response.status_code,
            headers=dict(response.headers),
        )
