from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ATTEST"
    debug: bool = False
    demo_mode: bool = True

    # Single workspace for hackathon (tenant_id still prefixed everywhere)
    tenant_id: str = "demo-workspace"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # Database
    database_url: str = "sqlite+aiosqlite:///./attest.db"

    # B2 / S3
    b2_key_id: str = ""
    b2_application_key: str = ""
    b2_bucket: str = ""
    b2_region: str = "us-west-004"
    b2_public_url_base: str = ""

    # Ed25519 signing (Mode 2 — hex-encoded 32-byte seed or PEM path)
    attest_signing_key_hex: str = ""
    attest_verify_key_hex: str = ""

    # Webhook for B2 event notifications → audit log
    b2_webhook_secret: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
