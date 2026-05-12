"""
Configuration module for Gate.io P2P Monitor.
Loads environment variables and provides centralized settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram Configuration
    telegram_bot_token: str = Field(default="", description="Telegram Bot API Token from @BotFather")
    telegram_chat_id: str = Field(default="", description="Telegram Chat ID for notifications")

    # Default Monitor Settings (overridable via API)
    default_trader_name: str = Field(default="", description="Your Gate.io trader name")
    default_min_quantity: float = Field(default=100.0, description="Minimum quantity to monitor")

    # Polling Configuration
    polling_interval: int = Field(default=10, ge=5, description="Polling interval in seconds (min 5)")

    # Server Configuration
    port: int = Field(default=8000)
    host: str = Field(default="0.0.0.0")

    # Environment
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # Gate.io API
    gateio_api_base: str = Field(default="https://api.gateio.ws/api/v4")
    gateio_p2p_ads_endpoint: str = Field(default="/p2p/merchant/books/ads_list")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()
