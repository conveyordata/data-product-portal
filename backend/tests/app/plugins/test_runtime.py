import pytest
from fastapi import HTTPException

from app.plugins.runtime import call_plugin


def test_call_plugin__returns_the_value_on_success():
    assert call_plugin("SomePlugin", "get_url", lambda value: value * 2, 21) == 42


def test_call_plugin__turns_an_unexpected_exception_into_a_clean_error():
    def boom():
        raise RuntimeError("the plugin is broken")

    with pytest.raises(HTTPException) as exc_info:
        call_plugin("SomePlugin", "get_url", boom)

    assert exc_info.value.status_code == 500
    assert "the plugin is broken" not in exc_info.value.detail
    assert "SomePlugin" in exc_info.value.detail


def test_call_plugin__logs_the_stack_trace(monkeypatch):
    logged = []
    monkeypatch.setattr(
        "app.plugins.runtime.logger.exception", lambda message: logged.append(message)
    )

    def boom():
        raise RuntimeError("the plugin is broken")

    with pytest.raises(HTTPException):
        call_plugin("SomePlugin", "get_url", boom)

    # logger.exception attaches the traceback itself.
    assert logged == ["Plugin 'SomePlugin' raised in 'get_url'"]


def test_call_plugin__lets_not_implemented_through():
    """A plugin says "I don't offer this" with NotImplementedError; callers turn
    that into a 501, so it must not become a 500."""

    def not_implemented():
        raise NotImplementedError

    with pytest.raises(NotImplementedError):
        call_plugin("SomePlugin", "get_url", not_implemented)


def test_call_plugin__lets_a_deliberate_http_exception_through():
    def bad_request():
        raise HTTPException(status_code=400, detail="environment is required")

    with pytest.raises(HTTPException) as exc_info:
        call_plugin("SomePlugin", "get_url", bad_request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "environment is required"
