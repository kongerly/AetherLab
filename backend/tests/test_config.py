"""不依赖本地 dotenv 文件的配置校验测试。"""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_environment_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证受支持的环境配置能够正确加载。"""
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    settings = Settings(_env_file=None)
    assert settings.app_env == "test"
    assert settings.log_level == "WARNING"


@pytest.mark.parametrize(("name", "value"), [("APP_ENV", "invalid"), ("LOG_LEVEL", "invalid")])
def test_invalid_configuration(monkeypatch: pytest.MonkeyPatch, name: str, value: str) -> None:
    """验证应用启动前会拒绝不受支持的配置值。"""
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
