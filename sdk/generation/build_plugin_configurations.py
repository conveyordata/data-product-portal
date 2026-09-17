import ast
from dataclasses import dataclass
from pathlib import Path

TECHNICAL_ASSET_CONFIGURATION_DIR = (
    Path(__file__).parent.parent.parent
    / "backend"
    / "app"
    / "technical_asset_configuration"
)
PLUGINS_OUT_DIR = Path(__file__).parent.parent / "sdk" / "plugins"

ENUM_IMPORT_MODULE = "app.technical_asset_configuration.enums"


@dataclass
class Field:
    name: str
    annotation: str
    default: str | None


def _find_assignment(tree: ast.Module, name: str) -> str:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            return ast.literal_eval(node.value)
    raise ValueError(f"Could not find assignment to {name}")


def _plugin_class(tree: ast.Module) -> ast.ClassDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and any(
            isinstance(base, ast.Name) and base.id == "TechnicalAssetPlugin"
            for base in node.bases
        ):
            return node
    raise ValueError("No TechnicalAssetPlugin subclass found")


def _has_configuration(plugin_class: ast.ClassDef) -> bool:
    return any(
        isinstance(node, ast.ClassDef) and node.name == "Meta"
        for node in plugin_class.body
    )


def _fields(plugin_class: ast.ClassDef) -> list[Field]:
    fields = []
    for node in plugin_class.body:
        if not isinstance(node, ast.AnnAssign) or not isinstance(node.target, ast.Name):
            continue
        field_name = node.target.id
        if field_name.startswith("_") or field_name in ("name", "version"):
            continue
        annotation = ast.unparse(node.annotation)
        default = ast.unparse(node.value) if node.value is not None else None
        fields.append(Field(field_name, annotation, default))
    return fields


def _used_enums(fields: list[Field]) -> set[str]:
    enums = set()
    for field in fields:
        if field.annotation == "AccessGranularity":
            enums.add("AccessGranularity")
    return enums


def _render_field(field: Field) -> str:
    if field.default is None:
        return f"    {field.name}: {field.annotation}"
    return f"    {field.name}: {field.annotation} = {field.default}"


def build_plugin_module(plugin_dir: Path) -> tuple[str, str, str] | None:
    """Returns (module_name, class_name, source) for a plugin with its own
    configuration, or None for a plugin that has no configuration to expose."""
    schema_source = (plugin_dir / "schema.py").read_text()
    schema_tree = ast.parse(schema_source)
    plugin_class = _plugin_class(schema_tree)

    if not _has_configuration(plugin_class):
        return None

    model_tree = ast.parse((plugin_dir / "model.py").read_text())
    configuration_type = _find_assignment(model_tree, "CONFIGURATION_TYPE")

    fields = _fields(plugin_class)
    enums = _used_enums(fields)

    lines = ["from typing import ClassVar", ""]
    lines.append("from sdk.plugins.base import TechnicalAssetConfiguration")
    if enums:
        lines.append("from sdk.plugins.enums import " + ", ".join(sorted(enums)))
    lines.append("")
    lines.append("")
    lines.append(f"class {plugin_class.name}(TechnicalAssetConfiguration):")
    lines.append(f'    configuration_type: ClassVar[str] = "{configuration_type}"')
    lines.append("")
    lines.extend(_render_field(field) for field in fields)
    lines.append("")

    return (plugin_dir.name, plugin_class.name, "\n".join(lines))


def build_enums_module() -> str:
    enums_tree = ast.parse((TECHNICAL_ASSET_CONFIGURATION_DIR / "enums.py").read_text())
    used = {
        base.id
        for node in ast.walk(enums_tree)
        if isinstance(node, ast.ClassDef)
        for base in node.bases
        if isinstance(base, ast.Name)
    }
    lines = ["from enum import Enum", ""]
    for node in enums_tree.body:
        if not isinstance(node, ast.ClassDef) or node.name not in ENUMS_TO_EXPORT:
            continue
        lines.append("")
        lines.append(f"class {node.name}(str, Enum):")
        for member in node.body:
            if isinstance(member, ast.Assign) and isinstance(
                member.targets[0], ast.Name
            ):
                lines.append(
                    f"    {member.targets[0].id} = {ast.unparse(member.value)}"
                )
    del used
    return "\n".join(lines) + "\n"


ENUMS_TO_EXPORT = {"AccessGranularity"}


def main() -> None:
    PLUGINS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in PLUGINS_OUT_DIR.glob("*.py"):
        if stale.name not in ("base.py", "__init__.py"):
            stale.unlink()

    generated: list[tuple[str, str]] = []
    any_enums_used = False

    for plugin_dir in sorted(TECHNICAL_ASSET_CONFIGURATION_DIR.iterdir()):
        if not plugin_dir.is_dir() or not (plugin_dir / "schema.py").exists():
            continue
        result = build_plugin_module(plugin_dir)
        if result is None:
            continue
        module_name, class_name, source = result
        if "sdk.plugins.enums" in source:
            any_enums_used = True
        (PLUGINS_OUT_DIR / f"{module_name}.py").write_text(HEADER + source)
        generated.append((module_name, class_name))

    if any_enums_used:
        (PLUGINS_OUT_DIR / "enums.py").write_text(HEADER + build_enums_module())

    module_imports = {
        "base": "from sdk.plugins.base import TechnicalAssetConfiguration"
    }
    for module_name, class_name in generated:
        module_imports[module_name] = (
            f"from sdk.plugins.{module_name} import {class_name}"
        )
    if any_enums_used:
        module_imports["enums"] = "from sdk.plugins.enums import " + ", ".join(
            sorted(ENUMS_TO_EXPORT)
        )
    init_lines = [module_imports[name] for name in sorted(module_imports)]

    all_names = sorted(
        {class_name for _, class_name in generated}
        | {"TechnicalAssetConfiguration"}
        | (ENUMS_TO_EXPORT if any_enums_used else set())
    )
    init_lines.append("")
    init_lines.append("__all__ = [")
    init_lines.extend(f'    "{name}",' for name in all_names)
    init_lines.append("]")

    (PLUGINS_OUT_DIR / "__init__.py").write_text(HEADER + "\n".join(init_lines) + "\n")


HEADER = f"# CODE GENERATED BY {Path(__file__).name}. DO NOT EDIT MANUALLY.\n"


if __name__ == "__main__":
    main()
