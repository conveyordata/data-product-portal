from unittest.mock import MagicMock

from app.mcp import mcp as mcp_module


def test_glue_enabled__true_when_setting_enabled(monkeypatch):
    monkeypatch.setattr(mcp_module, "glue_tools", MagicMock(is_enabled=lambda: True))

    assert mcp_module.glue_enabled() is True


def test_glue_enabled__false_when_setting_disabled(monkeypatch):
    monkeypatch.setattr(mcp_module, "glue_tools", MagicMock(is_enabled=lambda: False))

    assert mcp_module.glue_enabled() is False


def test_glue_enabled__false_when_glue_tools_failed_to_import(monkeypatch):
    monkeypatch.setattr(mcp_module, "glue_tools", None)

    assert mcp_module.glue_enabled() is False


def test_glue_instructions__included_when_enabled(monkeypatch):
    fake = MagicMock(is_enabled=lambda: True, MCP_INSTRUCTIONS="glue instructions")
    monkeypatch.setattr(mcp_module, "glue_tools", fake)

    assert mcp_module.glue_instructions() == "glue instructions"


def test_glue_instructions__empty_when_disabled(monkeypatch):
    fake = MagicMock(is_enabled=lambda: False, MCP_INSTRUCTIONS="glue instructions")
    monkeypatch.setattr(mcp_module, "glue_tools", fake)

    assert mcp_module.glue_instructions() == ""


def test_glue_instructions__empty_when_glue_tools_failed_to_import(monkeypatch):
    monkeypatch.setattr(mcp_module, "glue_tools", None)

    assert mcp_module.glue_instructions() == ""


def test_register_glue__registers_tools_when_enabled(monkeypatch):
    fake = MagicMock(is_enabled=lambda: True)
    monkeypatch.setattr(mcp_module, "glue_tools", fake)

    mcp_module.register_glue(mcp=object())

    fake.register_tools.assert_called_once()


def test_register_glue__skips_when_disabled(monkeypatch):
    fake = MagicMock(is_enabled=lambda: False)
    monkeypatch.setattr(mcp_module, "glue_tools", fake)

    mcp_module.register_glue(mcp=object())

    fake.register_tools.assert_not_called()


def test_register_glue__skips_when_glue_tools_failed_to_import(monkeypatch):
    monkeypatch.setattr(mcp_module, "glue_tools", None)

    mcp_module.register_glue(mcp=object())  # must not raise
