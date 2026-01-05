import os
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    VLM_PROVIDER: Literal["openai", "claude"] = "openai"
    VLM_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_BASE_URL: str | None = None
    CLAUDE_MODEL: str = "claude-opus-4-5-20251101"

    # 主账本路径（用于读取余额和账户）
    BEANCOUNT_MAIN_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "main.beancount")
    # 交易文件路径（用于写入新交易）
    BEANCOUNT_TRANSACTION_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "2026", "transactions.beancount")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
