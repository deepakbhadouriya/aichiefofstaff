from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AFRA_", extra="ignore")

    app_name: str = "A-FRA API"
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    dashboard_port: int = 3000
    database_url: str = "postgresql+psycopg://afra:afra@localhost:5432/afra"
    redis_url: str = "redis://localhost:6379/0"
    openai_model: str = "gpt-4.1-mini"
    log_level: str = "INFO"
    default_tenant: str = "demo-tenant"
    default_profile_id: str = "demo_user"
    realtime_sync_interval_seconds: int = 30
    runtime_store_path: str = ".runtime/runtime_store.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
