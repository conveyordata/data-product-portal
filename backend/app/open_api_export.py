from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from fastapi.openapi.utils import get_openapi

from app.main import app as f_app

if TYPE_CHECKING:
    from fastapi import FastAPI

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
        json.dumps(custom_openapi(f_app), indent=2) + "\n",
    )


def custom_openapi(app: FastAPI):
    """
    The events sent via the webhook are considered inputs, which are processed differently from outputs.
    Because we decided to allow duplicate names for objects during the naming migration (dataset -> output port),
    clashes are created. This function fixes those clashes again.
    Once the migration is complete, and all old objects are removed, this function can be removed too.
    """

    # 1. Generate the standard base specification (with routes and webhooks)
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        description=app.description,
        routes=app.routes,
        webhooks=app.webhooks.routes,
    )

    schemas = openapi_schema.get("components", {}).get("schemas", {})

    # 2. Identify every model that FastAPI split into -Input and -Output variants
    split_models = sorted([key[:-7] for key in schemas if key.endswith("-Output")])

    # 3. Convert to a string to perform a precise pointer re-routing
    schema_json = json.dumps(openapi_schema)
    for model in split_models:
        # Re-route webhook references away from the alias-heavy -Input models
        schema_json = schema_json.replace(
            f"#/components/schemas/{model}-Input",
            f"#/components/schemas/{model}-Output",
        )
        # Fix the discriminator string mappings inside your unified event stream
        schema_json = schema_json.replace(f'"{model}-Input"', f'"{model}-Output"')

    # Parse back into a dictionary to drop the unreferenced Input schemas
    openapi_schema = json.loads(schema_json)
    schemas = openapi_schema.get("components", {}).get("schemas", {})

    for model in split_models:
        # Safely remove the orphaned -Input schema definition completely
        schemas.pop(f"{model}-Input", None)

        # Rename the remaining -Output schema key to the clean, base model name
        if f"{model}-Output" in schemas:
            schemas[model] = schemas.pop(f"{model}-Output")

    # 4. Perform a final string pass to clean up the trailing "-Output" from all references
    schema_json = json.dumps(openapi_schema)
    for model in split_models:
        schema_json = schema_json.replace(
            f"#/components/schemas/{model}-Output", f"#/components/schemas/{model}"
        )

    final_schema = json.loads(schema_json)

    # 5. Reset internal titles to match their clean schema keys and remove readOnly tags
    schemas = final_schema.get("components", {}).get("schemas", {})
    for schema_name, schema in schemas.items():
        if isinstance(schema, dict):
            schema["title"] = schema_name
            if "properties" in schema:
                for prop in schema["properties"].values():
                    if isinstance(prop, dict):
                        prop.pop("readOnly", None)

    app.openapi_schema = final_schema
    return app.openapi_schema


if __name__ == "__main__":
    app()
