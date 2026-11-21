import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Khareed"
    app_env: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "127.0.0.1"

    # Claude / Anthropic API
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"

    # Database: PostgreSQL (Port 5432) with automatic driver selection
    # Format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/khareed"

    # Currency conversion rates to PKR
    usd_to_pkr_rate: float = 278.50
    fx_rate_date: str = "2026-11-21"

    # Notification settings
    notification_channel: str = "console"
    notification_webhook_url: str = ""
    alert_email_from: str = "alerts@khareed.pk"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
