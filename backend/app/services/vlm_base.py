from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class TransactionData(BaseModel):
    date: str
    amount: float
    merchant: str
    payment_method: str
    bank_name: str = ""
    card_last_four: str = ""
    transaction_type: str  # "expense" or "income"
    category: str = ""
    description: str = ""

class VLMService(ABC):
    @abstractmethod
    async def parse_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def parse_text(self, text: str, prompt: str) -> Dict[str, Any]:
        pass
