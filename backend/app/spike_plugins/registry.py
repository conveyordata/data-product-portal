"""
ADR-0024 Option 2b: discovered by explicit name, not automatic entry-point
discovery. This list stands in for the real setting/env var an image author
would maintain -- nothing gets imported that isn't named here.
"""

import importlib

from app.spike_plugins.interface import SpikeAssetPlugin

SPIKE_PLUGIN_MODULES: list[str] = [
    "app.spike_plugins.s3:SpikeS3Plugin",
    "app.spike_plugins.glue:SpikeGluePlugin",
]


def load_spike_plugins() -> dict[str, type[SpikeAssetPlugin]]:
    registry: dict[str, type[SpikeAssetPlugin]] = {}
    for entry in SPIKE_PLUGIN_MODULES:
        module_path, _, class_name = entry.partition(":")
        module = importlib.import_module(module_path)
        plugin_cls = getattr(module, class_name)
        registry[plugin_cls.key] = plugin_cls
    return registry
