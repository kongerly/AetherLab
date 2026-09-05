"""Configuration validation tests independent of local dotenv files."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_environment_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Load and validate supported environment settings."""
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    settings = Settings(_env_file=None)
    assert settings.app_env == "test"
    assert settings.log_level == "WARNING"


@pytest.mark.parametrize(("name", "value"), [("APP_ENV", "invalid"), ("LOG_LEVEL", "invalid")])
def test_invalid_configuration(monkeypatch: pytest.MonkeyPatch, name: str, value: str) -> None:
    """Reject unsupported values before the application can start."""
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
