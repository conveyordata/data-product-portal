from __future__ import annotations

import json
from pathlib import Path

import typer
from fastapi.openapi.utils import get_openapi

from app.main import app as fastapi_app

app = typer.Typer(
    help="Generate the openapi spec of the backend and output as a json file./."
)


@app.command()
def export_openapi(
    output: Path = typer.Argument(default="openapi.json", help="Path where to export"),
    openapi_version: str | None = typer.Option(
        default=None,
        help="If set, overrides the openapi version in the output. This is useful for compatibility with tools that do not support OpenAPI 3.1.",
    ),
):
    # generate dict
    result = get_openapi(
        title=fastapi_app.title,
        version=fastapi_app.version,
        contact=fastapi_app.contact,
        routes=fastapi_app.routes,
        summary=fastapi_app.summary,
        description=fastapi_app.description,
        openapi_version=openapi_version or "3.1.0",
    )

    # write to file
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2) + "\n",
    )


if __name__ == "__main__":
    app()
