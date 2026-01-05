from pydantic import BaseModel
from typing import Optional, Dict

class ImageParseRequest(BaseModel):
    image: str  # base64 encoded image

class TextParseRequest(BaseModel):
    text: str

class ParseResponse(BaseModel):
    date: str
    amount: float
    merchant: str
    payment_method: str
    bank_name: str = ""
    card_last_four: str = ""
    transaction_type: str
    category: str
    description: str

class TransactionRequest(BaseModel):
    date: str
    amount: float
    merchant: str
    payment_method: str
    bank_name: str = ""
    card_last_four: str = ""
    transaction_type: str
    category: Optional[str] = ""
    description: Optional[str] = ""

class TransactionResponse(BaseModel):
    success: bool
    message: str

class BalanceResponse(BaseModel):
    balances: Dict[str, float]
