from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Runtime settings required by the pipeline and agent loop."""

    # Gemini API (via OpenAI-compatible endpoint)
    gemini_api_key: str
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_model: str = "gemini-3-flash-preview"

    # API Server (future use)
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False

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

    # Feature Flags
    enable_verification: bool = True
    enable_quality_checks: bool = True

    # Limits
    max_issues_per_run: int = 20
    max_code_length: int = 10_000
    rate_limit_per_minute: int = 10

    # Pydantic v2 config
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # now this is SAFE
    )


settings = Settings()
