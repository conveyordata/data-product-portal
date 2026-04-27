#!/usr/bin/env python3
"""Upload dbt project schema and semantic model metadata to the Data Product Portal."""

import argparse
import os
import sys
from pathlib import Path
from uuid import UUID

import yaml

from sdk.api_client.api.data_products_output_ports import (
    create_output_port_semantic_model,
    create_output_port_table_schema,
    get_output_port_semantic_models,
    get_output_port_table_schemas,
    replace_output_port_semantic_model,
    replace_output_port_table_schema,
)
from sdk.api_client.client import Client
from sdk.api_client.models.column_request import ColumnRequest
from sdk.api_client.models.semantic_model_format import SemanticModelFormat
from sdk.api_client.models.semantic_model_request import SemanticModelRequest
from sdk.api_client.models.semantic_model_request_content import (
    SemanticModelRequestContent,
)
from sdk.api_client.models.table_schema_request import TableSchemaRequest


def load_portal_config(project_dir: Path) -> tuple[UUID, UUID]:
    portal_yml = project_dir / "portal.yml"
    config = yaml.safe_load(portal_yml.read_text())
    return UUID(config["data_product_id"]), UUID(config["output_port_id"])


def load_columns(project_dir: Path) -> list[ColumnRequest]:
    schema_yml = project_dir / "models" / "schema.yml"
    schema = yaml.safe_load(schema_yml.read_text())
    model = schema["models"][0]
    return [
        ColumnRequest(
            name=col["name"],
            description=col.get("description"),
            data_type=col.get("data_type"),
        )
        for col in model.get("columns", [])
    ]


def load_semantic_model_content(project_dir: Path) -> SemanticModelRequestContent:
    sem_yml = project_dir / "models" / "semantic_model.yml"
    content_dict = yaml.safe_load(sem_yml.read_text())
    return SemanticModelRequestContent.from_dict(content_dict)


def upsert_table_schema(
    client: Client,
    data_product_id: UUID,
    output_port_id: UUID,
    project_name: str,
    columns: list[ColumnRequest],
) -> None:
    print("[table-schema] Fetching existing schemas...")
    existing = get_output_port_table_schemas.sync(
        data_product_id=data_product_id,
        id=output_port_id,
        client=client,
    )
    body = TableSchemaRequest(name=project_name, columns=columns)
    if not existing:
        print("[table-schema] None found — creating new schema")
        result = create_output_port_table_schema.sync(
            data_product_id=data_product_id,
            id=output_port_id,
            client=client,
            body=body,
        )
    else:
        schema_id = existing[0].id
        print(f"[table-schema] Found existing schema {schema_id} — replacing")
        result = replace_output_port_table_schema.sync(
            data_product_id=data_product_id,
            id=output_port_id,
            schema_id=schema_id,
            client=client,
            body=body,
        )
    if result is None:
        print("[table-schema] ERROR: no response from API", file=sys.stderr)
        sys.exit(1)
    print(f"[table-schema] Done: {result.id}")


def upsert_semantic_model(
    client: Client,
    data_product_id: UUID,
    output_port_id: UUID,
    project_name: str,
    content: SemanticModelRequestContent,
) -> None:
    print("[semantic-model] Fetching existing semantic models...")
    existing = get_output_port_semantic_models.sync(
        data_product_id=data_product_id,
        id=output_port_id,
        client=client,
    )
    body = SemanticModelRequest(
        name=project_name,
        format_=SemanticModelFormat.METRICSFLOW,
        content=content,
    )
    if not existing:
        print("[semantic-model] None found — creating new semantic model")
        result = create_output_port_semantic_model.sync(
            data_product_id=data_product_id,
            id=output_port_id,
            client=client,
            body=body,
        )
    else:
        model_id = existing[0].id
        print(f"[semantic-model] Found existing model {model_id} — replacing")
        result = replace_output_port_semantic_model.sync(
            data_product_id=data_product_id,
            id=output_port_id,
            model_id=model_id,
            client=client,
            body=body,
        )
    if result is None:
        print("[semantic-model] ERROR: no response from API", file=sys.stderr)
        sys.exit(1)
    print(f"[semantic-model] Done: {result.id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload dbt metadata to the Portal")
    parser.add_argument("--project", required=True, help="dbt project directory name")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    project_dir = script_dir / args.project

    if not project_dir.is_dir():
        print(f"ERROR: project directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    portal_url = os.environ.get("PROV_DPP_API_URL", "http://localhost:8080")
    print(f"Portal URL: {portal_url}")
    print(f"Project: {args.project}")

    data_product_id, output_port_id = load_portal_config(project_dir)
    print(f"Data product: {data_product_id}")
    print(f"Output port:  {output_port_id}")

    columns = load_columns(project_dir)
    print(f"Columns loaded: {len(columns)}")

    content = load_semantic_model_content(project_dir)

    client = Client(base_url=portal_url)

    upsert_table_schema(client, data_product_id, output_port_id, args.project, columns)
    upsert_semantic_model(
        client, data_product_id, output_port_id, args.project, content
    )

    print("Done.")


if __name__ == "__main__":
    main()
