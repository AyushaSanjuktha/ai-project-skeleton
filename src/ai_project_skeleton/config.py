from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: SecretStr | None = None
    api_base_url: str = "https://api.example.com"
    timeout_seconds: float = Field(default=10.0, gt=0)
    max_retries: int = Field(default=3, ge=0)

    model_config = SettingsConfigDict(env_prefix="AI_", env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()
