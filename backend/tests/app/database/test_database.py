from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, make_url, pool

from app.database import database
from app.settings import Settings, settings


class FakeAzureCredential:
    def __init__(self, token: str):
        self.token = token
        self.scopes: list[str] = []

    def get_token(self, scope: str) -> SimpleNamespace:
        self.scopes.append(scope)
        return SimpleNamespace(token=self.token)


def _engine_with_password(password: str):
    return create_engine(
        make_url(database.get_url()).set(password=password), poolclass=pool.NullPool
    )


def test_apply_auth__azure_mode_logs_in_with_a_fresh_token_per_connection(
    monkeypatch,
):
    credential = FakeAzureCredential(settings.POSTGRES_PASSWORD)
    monkeypatch.setattr(settings, "POSTGRES_AUTH_MODE", "azure")
    monkeypatch.setattr(database, "_azure_credential", lambda: credential)
    engine = _engine_with_password("not-the-password")

    database.apply_auth(engine)
    for _ in range(2):
        with engine.connect() as connection:
            assert connection.exec_driver_sql("select 1").scalar() == 1

    assert credential.scopes == [database.AZURE_POSTGRES_SCOPE] * 2


def test_apply_auth__password_mode_uses_the_password_from_the_url(monkeypatch):
    engine = _engine_with_password(settings.POSTGRES_PASSWORD)
    monkeypatch.setattr(settings, "POSTGRES_PASSWORD", "not-the-password")

    database.apply_auth(engine)
    with engine.connect() as connection:
        assert connection.exec_driver_sql("select 1").scalar() == 1


def test_require_password_in_password_mode__rejects_a_missing_password():
    with pytest.raises(ValidationError, match="POSTGRES_PASSWORD is required"):
        Settings(POSTGRES_AUTH_MODE="password", POSTGRES_PASSWORD=None)


def test_require_password_in_password_mode__accepts_an_empty_password():
    assert Settings(POSTGRES_AUTH_MODE="password", POSTGRES_PASSWORD="")


def test_require_password_in_password_mode__azure_mode_needs_no_password():
    assert Settings(POSTGRES_AUTH_MODE="azure", POSTGRES_PASSWORD=None)
