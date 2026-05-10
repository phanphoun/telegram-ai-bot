import os
from typing import Optional

class Settings:
    """Application configuration settings loaded from environment variables"""
    
    TELEGRAM_BOT_TOKEN: str = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    GEMINI_API_KEY: str = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL: str = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash-lite')
    GEMINI_API_URL: str = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent"
    
    # File paths
    PROFILE_CSV_PATH: str = os.environ.get('PROFILE_CSV_PATH', 'data/profiles/phoun.csv')
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Response settings
    MAX_MESSAGE_LENGTH: int = 4000
    ENABLE_IMAGE_GENERATION: bool = True
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings are present"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    @classmethod
    def is_development(cls) -> bool:
        return os.environ.get('ENV', 'production').lower() == 'development'
