import pytest
from pydantic import ValidationError

from ai_project_skeleton.config import Settings


def test_default_settings():
    settings = Settings()

    assert settings.timeout_seconds == 10.0
    assert settings.max_retries == 3


def test_environment_variables(monkeypatch):
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "20")
    monkeypatch.setenv("AI_MAX_RETRIES", "5")

    settings = Settings()

    assert settings.timeout_seconds == 20.0
    assert settings.max_retries == 5


def test_invalid_timeout():
    with pytest.raises(ValidationError):
        Settings(timeout_seconds=-5)


def test_secret_is_hidden():
    settings = Settings(api_key="my-secret-key")

    assert "my-secret-key" not in str(settings.api_key)
