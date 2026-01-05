from fastapi import FastAPI, Request, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from contextlib import asynccontextmanager
import httpx
from jose import JWTError, jwt
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

def verify_fava_token(token: str) -> bool:
    """验证 Fava 访问 token"""
    if not token:
        return False
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return True
    except JWTError:
        return False

@app.api_route("/fava/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def fava_proxy_auth(path: str, request: Request, fava_token: str = Cookie(None)):
    """带认证的 Fava 代理"""
    # 验证 token
    if not verify_fava_token(fava_token):
        # 未认证，重定向到登录页
        return RedirectResponse(url="/login?redirect=/fava/", status_code=302)
    
    if not FavaService.is_running():
        raise HTTPException(status_code=503, detail="Fava service is not running")
    
    fava_url = f"http://localhost:5000/fava/{path}"
    if request.query_params:
        fava_url += f"?{request.query_params}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ["host", "cookie"]}
        
        response = await client.request(
            method=request.method,
            url=fava_url,
            headers=headers,
            content=await request.body(),
        )
        
        excluded_headers = ["content-encoding", "transfer-encoding", "content-length"]
        resp_headers = {k: v for k, v in response.headers.items() if k.lower() not in excluded_headers}
        
        return StreamingResponse(
            iter([response.content]),
            status_code=response.status_code,
            headers=resp_headers,
        )
