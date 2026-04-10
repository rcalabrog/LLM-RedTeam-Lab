from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_API_PREFIX,
    DEFAULT_APP_ENV,
    DEFAULT_APP_NAME,
    DEFAULT_COMPARISON_MODEL,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_LLM_GENERATION_MAX_TOKENS,
    DEFAULT_LLM_GENERATION_TEMPERATURE,
    DEFAULT_LLM_REQUEST_TIMEOUT_SECONDS,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAIN_MODEL,
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_SQLITE_DB_PATH,
    DEFAULT_TARGET,
)

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = Field(default=DEFAULT_APP_NAME, alias="APP_NAME")
    app_env: str = Field(default=DEFAULT_APP_ENV, alias="APP_ENV")
    api_prefix: str = Field(default=DEFAULT_API_PREFIX, alias="API_PREFIX")
    ollama_base_url: str = Field(
        default=DEFAULT_OLLAMA_BASE_URL,
        alias="OLLAMA_BASE_URL",
    )
    default_main_model: str = Field(
        default=DEFAULT_MAIN_MODEL,
        alias="DEFAULT_MAIN_MODEL",
    )
    default_comparison_model: str = Field(
        default=DEFAULT_COMPARISON_MODEL,
        alias="DEFAULT_COMPARISON_MODEL",
    )
    llm_provider: str = Field(default=DEFAULT_LLM_PROVIDER, alias="LLM_PROVIDER")
    llm_request_timeout_seconds: float = Field(
        default=DEFAULT_LLM_REQUEST_TIMEOUT_SECONDS,
        alias="LLM_REQUEST_TIMEOUT_SECONDS",
        gt=0,
    )
    llm_generation_temperature: float = Field(
        default=DEFAULT_LLM_GENERATION_TEMPERATURE,
        alias="LLM_GENERATION_TEMPERATURE",
        ge=0.0,
        le=2.0,
    )
    llm_generation_max_tokens: int = Field(
        default=DEFAULT_LLM_GENERATION_MAX_TOKENS,
        alias="LLM_GENERATION_MAX_TOKENS",
        gt=0,
    )
    sqlite_db_path: str = Field(
        default=DEFAULT_SQLITE_DB_PATH,
        alias="SQLITE_DB_PATH",
    )
    default_target: str = Field(default=DEFAULT_TARGET, alias="DEFAULT_TARGET")
    log_level: str = Field(default=DEFAULT_LOG_LEVEL, alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
