import os

import pytest

from marvin.settings import Settings


def test_database_url_default():
    settings = Settings()
    assert settings.database_url is not None
    assert settings.database_url.endswith("/.marvin/marvin.db")


@pytest.mark.parametrize(
    "env_var_value, expected",
    [
        (
            "sqlite+aiosqlite:///" + os.path.expanduser("~/.marvin/test.db"),
            "sqlite+aiosqlite:///" + os.path.expanduser("~/.marvin/test.db"),
        ),
        (
            "postgresql+asyncpg://user:password@host:port/database",
            "postgresql+asyncpg://user:password@host:port/database",
        ),
    ],
)
def test_database_url_set_from_env_var(
    monkeypatch: pytest.MonkeyPatch,
    env_var_value: str,
    expected: str,
):
    monkeypatch.setenv("MARVIN_DATABASE_URL", env_var_value)
    settings = Settings()
    assert settings.database_url == expected
