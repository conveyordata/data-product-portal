from __future__ import annotations

import json
from pathlib import Path

import typer
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute, BaseRoute

from app.core.logging import logger
from app.main import app as fastapi_app

app = typer.Typer(
    help="Generate the openapi spec of the backend and output as a json file./."
)


def _route_filter(routes: list[BaseRoute]) -> list[BaseRoute]:
    """
    returns a selection of routes that we want to use for SDK generation
    """
    result = []
    for route in routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api/v2"):
            if not getattr(route, "deprecated"):
                result.append(route)
            else:
                logger.debug(f"Excluding v2 deprecated route: {route.path}")
    return result


@app.command()
def export_openapi(
    output: Path = typer.Argument(default="openapi.json", help="Path where to export"),
    exclude_deprecated: bool = typer.Option(
        default=False,
        help="When set to true, only includes non-deprecated v2 API routes",
    ),
):
    routes = fastapi_app.routes
    if exclude_deprecated:
        routes = _route_filter(routes)

    # generate dict
    result = get_openapi(
        title=fastapi_app.title,
        version=fastapi_app.version,
        contact=fastapi_app.contact,
        routes=routes,
        summary=fastapi_app.summary if not exclude_deprecated else None,
        description=fastapi_app.description,
    )

    # write to file
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2) + "\n",
    )


if __name__ == "__main__":
    app()
