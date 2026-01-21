"""
ByteDent API Configuration
==========================
CTO Best Practice: Centralized configuration with environment variable support,
validation, and sensible defaults for all deployment environments.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden via environment variables.
    Example: APP_NAME=MyApp or BYTEDENT_LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
    """

    # ===========================================
    # APPLICATION SETTINGS
    # ===========================================
    app_name: str = Field(default="ByteDent Dental AI API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")  # development, staging, production

    # ===========================================
    # API SETTINGS
    # ===========================================
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="WORKERS")  # Keep at 1 for model loading

    # ===========================================
    # CORS SETTINGS
    # ===========================================
    cors_origins: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # ===========================================
    # RATE LIMITING
    # ===========================================
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=60, env="RATE_LIMIT_REQUESTS")  # requests per minute
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # window in seconds

    # ===========================================
    # MODEL SETTINGS
    # ===========================================
    llm_model: str = Field(
        default="Qwen/Qwen2.5-3B-Instruct",
        validation_alias="BYTEDENT_LLM_MODEL"
    )
    embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        env="BYTEDENT_EMBEDDING_MODEL"
    )
    use_8bit_quantization: bool = Field(default=True, env="USE_8BIT_QUANTIZATION")
    device: str = Field(default="auto", env="DEVICE")  # auto, cuda, cpu

    # ===========================================
    # RAG SETTINGS
    # ===========================================
    chunk_size_tokens: int = Field(default=400, env="CHUNK_SIZE_TOKENS")
    chunk_overlap_tokens: int = Field(default=80, env="CHUNK_OVERLAP_TOKENS")
    retrieval_top_k: int = Field(default=5, env="RETRIEVAL_TOP_K")
    min_similarity_threshold: float = Field(default=0.25, env="MIN_SIMILARITY_THRESHOLD")
    handoff_similarity_threshold: float = Field(default=0.30, env="HANDOFF_SIMILARITY_THRESHOLD")

    # ===========================================
    # GENERATION SETTINGS
    # ===========================================
    max_new_tokens: int = Field(default=512, env="MAX_NEW_TOKENS")
    temperature: float = Field(default=0.1, env="TEMPERATURE")
    top_p: float = Field(default=0.9, env="TOP_P")

    # ===========================================
    # LOGGING SETTINGS
    # ===========================================
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text

    # ===========================================
    # SECURITY SETTINGS
    # ===========================================
    api_key_enabled: bool = Field(default=False, env="API_KEY_ENABLED")
    api_key: Optional[str] = Field(default=None, env="API_KEY")

    # ===========================================
    # HANDOFF KEYWORDS
    # ===========================================
    @property
    def uncertainty_keywords(self) -> List[str]:
        return [
            "i'm not sure", "i don't know", "unclear", "not enough information",
            "cannot determine", "insufficient context", "i apologize",
            "consult your dentist", "seek professional advice", "cannot diagnose"
        ]

    @property
    def handoff_required_topics(self) -> List[str]:
        return [
            "pricing", "price", "cost", "quote", "subscription",
            "my scan", "my image", "my diagnosis", "my treatment",
            "specific patient", "patient name", "medical advice",
            "prescription", "medication", "legal", "malpractice",
            "insurance claim", "billing", "refund"
        ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    CTO Note: Using lru_cache ensures settings are only loaded once,
    improving performance and ensuring consistency across the application.
    """
    return Settings()


# Export settings instance for convenience
settings = get_settings()
