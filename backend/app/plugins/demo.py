"""Spike self-check: proves the whole loop end to end.

Not a pytest suite (this is a throwaway spike module, not shipped code) -
just an assert-based script, run via `python -m app.plugins.demo` against a
real database with the example plugin installed and migrated. See
SPIKE_NOTES.md.
"""

from sdk.plugins.context import PluginContext

from app.database.database import SessionLocal
from app.plugins.loader import discover_plugins
from app.plugins.runtime import call_plugin


def main() -> None:
    plugins = discover_plugins()
    assert plugins, "no plugins discovered via entry points"
    plugin_cls = next(p for p in plugins if p.key == "azure-blob")

    icon = plugin_cls.get_icon()
    assert icon.startswith(b"<svg"), (
        "icon should be real SVG bytes read from the package"
    )

    context = PluginContext(technical_asset_name="demo-blob-asset", domain="acme")

    # 1. validation failure is caught cleanly, not raised
    bad_result = call_plugin("azure-blob", "validate", plugin_cls.validate, {}, context)
    assert not bad_result.ok
    assert bad_result.error
    assert "container_name" not in bad_result.error

    # 2. a plugin that raises an unexpected exception doesn't crash the caller
    def boom(*_a, **_kw):
        raise RuntimeError("simulated plugin bug")

    crash_result = call_plugin("azure-blob", "validate", boom, {}, context)
    assert not crash_result.ok

    # 3. happy path: validate, persist into the plugin's own table, render
    values = {"container_name": "my-container", "path": "raw/events"}
    ok_result = call_plugin(
        "azure-blob", "validate", plugin_cls.validate, values, context
    )
    assert ok_result.ok

    session = SessionLocal()
    try:
        row = plugin_cls.model(**values)
        session.add(row)
        session.flush()
        session.commit()
    finally:
        session.close()

    rendered = call_plugin(
        "azure-blob", "render_result", plugin_cls.render_result, values, context
    )
    url = call_plugin("azure-blob", "get_url", plugin_cls.get_url, values, context)
    assert rendered.ok
    assert url.ok


if __name__ == "__main__":
    main()
