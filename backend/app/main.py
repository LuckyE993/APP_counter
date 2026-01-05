from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
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
