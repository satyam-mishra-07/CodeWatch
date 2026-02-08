from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings required by the pipeline and agent loop."""

    # Gemini API (via OpenAI-compatible endpoint)
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_model: str = "gemini-3-flash-preview"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/review_agent.log"

    # Tool generation settings
    detection_temperature: float = 0.3
    detection_max_tokens: int = 2048
    explanation_temperature: float = 0.4
    explanation_max_tokens: int = 1024
    verification_temperature: float = 0.2
    verification_max_tokens: int = 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
