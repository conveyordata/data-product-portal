from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - yaml is an optional helper
    yaml = None  # type: ignore

from app.main import app


def export_openapi(output: Path, fmt: Optional[str] = None) -> Path:
    """
    Export the FastAPI OpenAPI schema to a file.

    Args:
        output: Destination file path. Parent directories will be created if needed.
        fmt: Optional explicit format: "json" or "yaml". If not provided,
             the format is inferred from the file extension. Defaults to json.

    Returns:
        The path to the written file.
    """
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Build schema without launching the server
    schema = app.openapi()

    # Determine format
    ext = output.suffix.lower().lstrip(".")
    fmt = (fmt or ext or "json").lower()

    if fmt not in {"json", "yaml", "yml"}:
        raise ValueError("Unsupported format. Use 'json' or 'yaml'.")

    if fmt in {"yaml", "yml"}:
        if yaml is None:
            raise RuntimeError(
                "YAML export requested but 'pyyaml' is not installed. "
                "Install pyyaml or export to .json instead."
            )
        text = yaml.safe_dump(schema, sort_keys=False, allow_unicode=True)
        output.write_text(text, encoding="utf-8")
    else:
        output.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    return output


def _parse_args(
    argv: Optional[list[str]] = None,
):  # pragma: no cover - thin CLI wrapper
    import argparse

    parser = argparse.ArgumentParser(
        description="Export the backend OpenAPI specification to a file."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("openapi.json"),
        help="Output file path (defaults to ./openapi.json). Format is inferred from extension.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "yaml"],
        default=None,
        help="Explicit output format. If omitted, inferred from the output file extension.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None):  # pragma: no cover - thin CLI wrapper
    args = _parse_args(argv)
    written = export_openapi(args.output, args.format)
    print(f"OpenAPI spec written to: {written}")


if __name__ == "__main__":  # pragma: no cover
    main()
