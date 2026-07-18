from functools import lru_cache

from pydantic import field_validator
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
    b2_region: str = "us-east-005"
    b2_public_url_base: str = ""

    # Ed25519 signing (Mode 2 — hex-encoded 32-byte seed or PEM path)
    attest_signing_key_hex: str = ""
    attest_verify_key_hex: str = ""

    # Webhook for B2 event notifications → audit log
    b2_webhook_secret: str = ""

    # Public API base for locally persisted assets (no B2 keys)
    api_public_base_url: str = "http://localhost:8000"

    # Provider keys (Block 1 — add when ready)
    replicate_api_token: str = ""
    gmi_api_key: str = ""

    @field_validator("b2_public_url_base", mode="before")
    @classmethod
    def sanitize_b2_public_url_base(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        cleaned = value.strip()
        # Common copy-paste mistake: B2_PUBLIC_URL_BASE=https://...
        if cleaned.upper().startswith("B2_PUBLIC_URL_BASE="):
            cleaned = cleaned.split("=", 1)[1].strip()
        if cleaned and not cleaned.startswith(("http://", "https://")):
            return ""
        return cleaned

    @field_validator("b2_key_id", "b2_application_key", "b2_bucket", "gmi_api_key", mode="before")
    @classmethod
    def strip_secrets(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @property
    def b2_configured(self) -> bool:
        return bool(self.b2_bucket and self.b2_key_id and self.b2_application_key)

    @property
    def gmi_configured(self) -> bool:
        return bool(self.gmi_api_key)

    @property
    def genblaze_image_ready(self) -> bool:
        return self.b2_configured and bool(self.replicate_api_token)

    @property
    def gmi_pipeline_ready(self) -> bool:
        return (
            self.b2_configured
            and self.gmi_configured
            and bool(self.attest_signing_key_hex)
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
