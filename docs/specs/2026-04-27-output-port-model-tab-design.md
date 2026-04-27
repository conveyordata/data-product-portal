# Output Port Model Tab — Design Spec

**Date:** 2026-04-27
**Status:** Approved

## Overview

Add a "Model" tab to the output port detail page that displays:

1. **Table schemas** — description, tags per table; name, description, data_type, tags per column
2. **Semantic models** — linked semantic model definitions in MetricsFlow or Open Semantic Interchange (OSI) format

Metadata is imported via API (format-agnostic for v1); the UI is read-only display only. The import trigger mechanism (CLI, dbt artifact upload, etc.) is out of scope for v1.

## Context & Constraints

- An **output port** exposes multiple tables to consumers.
- A **technical asset** is the storage location used for access grants (e.g., a Postgres schema, S3 prefix, Snowflake database). It is coarser-grained than a table.
- The same technical asset can be linked to multiple output ports, each exposing different table subsets. Therefore, table schema metadata belongs at the **output port level**, not the technical asset level.
- Semantic models also live at the **output port level** — they describe the semantic meaning of the tables that specific output port exposes.
- Schema metadata originates from dbt (schema.yml) or similar tooling; the portal stores and displays it.

## Data Model

Two new feature modules following the existing `backend/app/<feature>/` pattern (router, service, model, schema_request, schema_response).

### Module: `output_port_table_schemas`

```
OutputPortTableSchema
  id:             UUID (PK)
  output_port_id: UUID → Dataset (FK, ON DELETE CASCADE)
  name:           str
  description:    str | None
  tags:           [Tag]  via junction table tags_output_port_table_schemas

OutputPortColumn
  id:              UUID (PK)
  table_schema_id: UUID → OutputPortTableSchema (FK, ON DELETE CASCADE)
  name:            str
  description:     str | None
  data_type:       str | None
  tags:            [Tag]  via junction table tags_output_port_columns
```

Tags reuse the existing `Tag` model, following the same many-to-many pattern as `tags_datasets` and `tags_data_outputs`.

### Module: `output_port_semantic_models`

```
OutputPortSemanticModel
  id:             UUID (PK)
  output_port_id: UUID → Dataset (FK, ON DELETE CASCADE)
  name:           str
  format:         enum { MetricsFlow, OpenSemanticInterchange }
  content:        JSONB  ← raw semantic model stored as-is
```

`content` is stored as an opaque JSONB blob in v1. Parsing into format-specific structured fields is deferred until the import mechanism is defined and a richer display is needed.

### Changes to existing output port response

`GetOutputPortResponse` gains two new nested lists:

```python
table_schemas: list[OutputPortTableSchemaResponse]
semantic_models: list[OutputPortSemanticModelResponse]
```

These are eagerly loaded so the frontend can render the Model tab from the existing `getOutputPort` RTK Query call without additional requests.

## API Endpoints

All endpoints are nested under:
```
/api/data_products/{data_product_id}/output_ports/{output_port_id}/
```

Authorization follows the existing `Authorization.enforce()` Casbin pattern on all routers.

### Table Schemas

| Method   | Path                                  | Description                                      |
|----------|---------------------------------------|--------------------------------------------------|
| `GET`    | `table-schemas`                       | List all table schemas for the output port       |
| `POST`   | `table-schemas`                       | Create a table schema with columns inline        |
| `PUT`    | `table-schemas/{schema_id}`           | Replace a table schema and its columns           |
| `DELETE` | `table-schemas/{schema_id}`           | Delete a table schema (cascades to columns)      |

`POST`/`PUT` request body — columns are included inline to avoid separate column endpoints in v1:

```json
{
  "name": "orders",
  "description": "Order transactions",
  "tags": ["finance", "core"],
  "columns": [
    { "name": "id", "data_type": "int", "description": "Primary key", "tags": [] },
    { "name": "amount", "data_type": "decimal", "description": "Order total", "tags": ["pii"] }
  ]
}
```

Tags are referenced by **string value** (matching the existing pattern used by `tags_datasets` and `tags_data_outputs`). Tag records are created on first use if they don't already exist.
```

### Semantic Models

| Method   | Path                                  | Description                                      |
|----------|---------------------------------------|--------------------------------------------------|
| `GET`    | `semantic-models`                     | List all semantic models for the output port     |
| `POST`   | `semantic-models`                     | Create a semantic model                          |
| `PUT`    | `semantic-models/{model_id}`          | Replace a semantic model                         |
| `DELETE` | `semantic-models/{model_id}`          | Delete a semantic model                          |

`POST`/`PUT` request body:

```json
{
  "name": "revenue_model",
  "format": "MetricsFlow",
  "content": { "...": "raw semantic model object" }
}
```

## Frontend

### New "Model" tab

Added to the output port detail page (`dataset-tabs.tsx`) with a new `TabKeys.Model` key. Positioned after "About".

The tab is read-only. It loads data from the existing `getOutputPort` RTK Query response (table_schemas + semantic_models nested in), requiring no additional API calls beyond the regenerated API client (`npm run generate-api`).

### Table Schemas section

- Ant Design `Collapse` component, one panel per table
- **Panel header**: table name, description, tags as `<Tag>` badges
- **Panel body**: read-only Ant Design `Table` with columns: Name | Type | Description | Tags
- Empty state: *"No table schemas imported yet"*

### Semantic Models section

- Below the table schemas section
- Each semantic model as a card: name + format badge (MetricsFlow / OSI) + raw `content` in a syntax-highlighted `<pre>` block (JSON)
- Empty state: *"No semantic models imported yet"*

### New files

```
frontend/src/pages/dataset/components/dataset-tabs/
  model-tab/
    model-tab.tsx
    components/
      table-schema-list.tsx
      column-table.tsx
      semantic-model-list.tsx
      semantic-model-card.tsx
```

### Localization

All user-facing strings go through i18next. Run `npm run extract-translations` after implementation.

## Out of Scope (v1)

- Import/sync mechanism (CLI push, dbt artifact upload, webhook)
- Editing schema metadata in the portal UI
- Parsing semantic model content into format-specific structured fields
- Column-level endpoints (columns are always managed inline with their table schema)
- Constraints, meta fields (explicitly excluded per dbt parity requirement)
