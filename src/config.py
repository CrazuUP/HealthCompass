from pydantic_settings import BaseSettings
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # MAX Bot Configuration
    max_bot_token: str = "test_bot_token_123"
    max_api_url: str = "https://api.max.ru/v1"
    webhook_url: str = "https://localhost:8000/webhook"
    webhook_secret: Optional[str] = None

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite:///./health_compass.db"

    # Debug
    debug: bool = True
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings():
    """Функция для получения настроек с обработкой ошибок"""
    try:
        env_path = ".env"
        if not os.path.exists(env_path):
            logger.warning(f"⚠️ .env file not found at {os.path.abspath(env_path)}")
            logger.info("🔄 Using default settings for development")

        settings = Settings()
        logger.info("✅ Settings loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"❌ Error loading settings: {e}")
        logger.info("🔄 Falling back to default settings")
        return Settings()


settings = get_settings()