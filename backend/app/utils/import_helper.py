import importlib


def import_from_dotted_path(dotted_path: str):
    """
    Import a class from a dotted module path.
    E.g. "myapp.integrations.snowflake.SnowflakeIntegrationProvider"
    """
    module_path, _, class_name = dotted_path.rpartition(".")
    if not module_path:
        raise ValueError(f"Invalid dotted path: {dotted_path}")

    module = importlib.import_module(module_path)
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ImportError(f"Cannot import '{class_name}' from '{module_path}'")
