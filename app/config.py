from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./url_shortner.db"

    redis_url: str = "redis://localhost:6379"
    default_cache_expiry_seconds: int = 60 * 60

    secret_key: str = "random secret key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    rate_limit_per_minute: int = 60

    base_url: str = "http://localhost:8000"
    url_default_expiry_days: int = 30

    visit_threshold: int = 100
    expiration_warning_days: int = 7

    # class Config:
    #     ENV_FILE = ".env"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
