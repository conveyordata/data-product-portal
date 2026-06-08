from __future__ import annotations

import json
from pathlib import Path

import typer

from app.main import app as f_app

app = typer.Typer(
    help="Generate the openapi spec of the backend and output as a json file./."
)


@app.command()
def export_openapi(
    output: Path = typer.Argument(default="openapi.json", help="Path where to export"),
):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(f_app.openapi(), indent=2) + "\n",
    )


if __name__ == "__main__":
    app()
