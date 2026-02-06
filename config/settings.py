# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Gemini API (via OpenAI SDK)
    gemini_api_key: str
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_model: str = "gemini-3-flash-preview"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/review_agent.log"
    
    # Generation Settings
    detection_temperature: float = 0.3
    detection_max_tokens: int = 2048
    explanation_temperature: float = 0.4
    explanation_max_tokens: int = 1024
    verification_temperature: float = 0.2
    verification_max_tokens: int = 1024
    
    # Features
    enable_verification: bool = True
    enable_quality_checks: bool = True
    max_issues_per_run: int = 20
    max_code_length: int = 10000
    
    # Rate Limiting
    rate_limit_per_minute: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Load settings
settings = Settings()