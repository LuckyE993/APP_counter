from .vlm_base import VLMService
from .vlm_openai import OpenAIVLMService
from .vlm_claude import ClaudeVLMService
from ..config import settings

def get_vlm_service() -> VLMService:
    if settings.VLM_PROVIDER == "openai":
        return OpenAIVLMService()
    elif settings.VLM_PROVIDER == "claude":
        return ClaudeVLMService()
    else:
        raise ValueError(f"Unsupported VLM provider: {settings.VLM_PROVIDER}")
