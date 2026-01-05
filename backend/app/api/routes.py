import base64
from fastapi import APIRouter, HTTPException, Depends
from ..models.schemas import (
    ImageParseRequest,
    TextParseRequest,
    TransactionRequest,
    TransactionResponse,
    BalanceResponse,
    ParseResponse
)
from ..models.auth import LoginRequest, Token
from ..services.vlm_factory import get_vlm_service
from ..services.beancount_ops import BeancountService
from ..services.fava_service import FavaService
from ..services.prompts import get_image_parse_prompt, get_text_parse_prompt
from ..utils.auth import authenticate_user, create_access_token, verify_token

router = APIRouter(prefix="/api")

@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    if not authenticate_user(request.username, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": request.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/parse/image", response_model=ParseResponse)
async def parse_image(request: ImageParseRequest, username: str = Depends(verify_token)):
    try:
        image_data = base64.b64decode(request.image)
        vlm_service = get_vlm_service()
        result = await vlm_service.parse_image(image_data, get_image_parse_prompt())
        print("result:", result)
        return ParseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse image: {str(e)}")

@router.post("/parse/text", response_model=ParseResponse)
async def parse_text(request: TextParseRequest, username: str = Depends(verify_token)):
    try:
        vlm_service = get_vlm_service()
        result = await vlm_service.parse_text(request.text, get_text_parse_prompt())
        print("result:", result)
        return ParseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse text: {str(e)}")

@router.post("/transaction", response_model=TransactionResponse)
async def save_transaction(request: TransactionRequest, username: str = Depends(verify_token)):
    try:
        beancount_service = BeancountService()
        success = beancount_service.append_transaction(
            date=request.date,
            amount=request.amount,
            merchant=request.merchant,
            payment_method=request.payment_method,
            bank_name=request.bank_name,
            card_last_four=request.card_last_four,
            transaction_type=request.transaction_type,
            category=request.category,
            description=request.description
        )
        if success:
            return TransactionResponse(success=True, message="Transaction saved successfully")
        else:
            raise HTTPException(status_code=500, detail="Failed to save transaction")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save transaction: {str(e)}")

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(username: str = Depends(verify_token)):
    try:
        beancount_service = BeancountService()
        balances = beancount_service.get_balances()
        return BalanceResponse(balances=balances)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get balance: {str(e)}")

@router.get("/accounts")
async def get_accounts(username: str = Depends(verify_token)):
    try:
        beancount_service = BeancountService()
        accounts = beancount_service.get_accounts()
        return {"accounts": accounts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get accounts: {str(e)}")

@router.get("/config/accounts")
async def get_account_config(username: str = Depends(verify_token)):
    """
    获取账户配置，包括支付方式、分类等
    前端使用此配置来动态生成选项，确保与 accounts.beancount 严格对应
    """
    try:
        beancount_service = BeancountService()
        config = beancount_service.get_account_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get account config: {str(e)}")

@router.post("/fava/start")
async def start_fava(port: int = 5000, username: str = Depends(verify_token)):
    """启动Fava服务"""
    try:
        success = FavaService.start(port)
        if success:
            # 返回相对路径，让前端通过后端代理访问
            return {
                "success": True,
                "message": "Fava started successfully",
                "url": "/api/fava/proxy/"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start Fava")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Fava: {str(e)}")

@router.post("/fava/stop")
async def stop_fava(username: str = Depends(verify_token)):
    """停止Fava服务"""
    try:
        success = FavaService.stop()
        if success:
            return {"success": True, "message": "Fava stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop Fava")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop Fava: {str(e)}")

@router.get("/fava/status")
async def get_fava_status(username: str = Depends(verify_token)):
    """获取Fava服务状态"""
    try:
        is_running = FavaService.is_running()
        return {
            "running": is_running,
            "url": "/api/fava/proxy/" if is_running else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Fava status: {str(e)}")

