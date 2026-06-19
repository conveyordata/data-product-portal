# DB Model for Persisting Output Port Data Models

## Context and Problem Statement

Output ports expose datasets to consumers. To help consumers understand the structure of those datasets,
Portal displays the schema information (tables/views and their columns) for each output port.
This data model is sourced from a [Bitol data contract](https://github.com/bitol-io/open-data-contract-standard) via an ingestion API, following the same push-based
approach used for data quality and usage metrics.

The Bitol schema structure is two-level: **schema objects** (tables, topics,...) each contain **properties**
(columns or fields). Properties can themselves be nested objects, representing struct types or JSON
sub-schemas. The database model must accommodate this hierarchy without overcomplicating the service layer.

## Assumptions

* We assume that the schema is typically fetched as a whole for each output port.
* We assume that most schemas do not have more than 2 levels of nesting. However, we want to support arbitrary nesting without schema changes, so the service layer should be able to handle this gracefully.
* We assume that an output port consists of a small number of tables/topics (< 10).

## Decision Drivers

* Support column-level filtering and search across output ports
* Handle nested properties (struct/object columns) without arbitrary depth restrictions
* Keep the service layer simple. No recursive SQL queries
* Nice to have: follow existing patterns in the codebase (e.g. data quality summary model)

## Considered Options

* **Option A: Fully normalised (two tables)** Two relational tables: one for schema objects and one for every property in the schema.
  The properties reference their parent via a nullable self-referential FK. The schema object ID is denormalised onto every property row (including nested ones) to allow flat queries without recursion.
* **Option B: Fully normalised (two tables)** Two relational tables: one for schema objects, one for properties. The properties reference their parent via a nullable self-referential FK.
* **Option C: JSONB blob for full schema** A single table with the full Bitol `schema:` block stored as a JSONB column on the output port or in a dedicated table.
* **Option D: Hybrid schema object and jsonb properties** Schema objects as normalised rows; properties stored as a JSONB array on each schema object row.

## Decision Outcome

**Chosen option:** *Option A: Fully normalised with adjacency list*.
It is the only option that enables column-level querying and indexing while keeping the service layer simple.
Denormalising `schema_object_id` onto every property row (including nested ones) avoids recursive SQL:
the service fetches all properties for a schema object in one flat query and builds the tree in Python.

### Confirmation

Two tables are added:

**`output_port_schema_objects`**: one row per object declared in the contract schema of the output port. This defines a table/view in the output port.

| Column           | Type                    | Notes                         |
|------------------|-------------------------|-------------------------------|
| `id`             | UUID PK                 |                               |
| `output_port_id` | UUID FK → `datasets.id` | CASCADE delete                |
| `name`           | Text                    |                               |
| `logical_type`   | Text nullable           | e.g. `object`                 |
| `physical_type`  | Text nullable           | e.g. `table`, `view`, `topic` |
| `physical_name`  | Text nullable           | fully-qualified physical name |
| `description`    | Text nullable           |                               |
| `position`       | SmallInteger            | preserves declaration order   |

**`output_port_schema_properties`**: one row per column or field, at any nesting depth.

| Column                 | Type                                      | Notes                                             |
|------------------------|-------------------------------------------|---------------------------------------------------|
| `id`                   | UUID PK                                   |                                                   |
| `schema_object_id`     | UUID FK → `output_port_schema_objects.id` | CASCADE delete; set on every row including nested |
| `parent_property_id`   | UUID FK → self, nullable                  | NULL = root-level property                        |
| `name`                 | Text                                      | indexed for cross-output-port column search       |
| `business_name`        | Text nullable                             |                                                   |
| `primary_key`          | Bool                                      |                                                   |
| `primary_key_position` | SmallInteger                              |                                                   |
| `logical_type`         | Text nullable                             |                                                   |
| `physical_type`        | Text nullable                             |                                                   |
| `description`          | Text nullable                             |                                                   |
| `unique`               | Bool                                      | Indicates whether element contains unique values  |
| `required`             | Bool                                      | Indicates whether null values are allowed         |
| `examples`             | JSON nullable                             | arbitrary list of example values                  |
| `position`             | SmallInteger                              | preserves declaration order                       |

## Pros and Cons of the Options

### Option A: Fully normalised and store schema object ID in every property row

* **Good, because** column-level querying and indexing (`name`, `physical_type`) work without JSON operators
* **Good, because** mirrors the existing `DataQualitySummary` / `DataQualityTechnicalAsset` pattern
* **Good, because** supports arbitrary nesting depth with no schema changes; the service layer tree-builder is depth-agnostic
* **Good, because** denormalising `schema_object_id` allows to use a simple SQL query to fetch schema for 1 output port instead of requiring a recursive CTE.
* **Neutral, because** tree reconstruction happens in Python rather than SQL, which is acceptable given schemas are always fetched per output port
* **Bad, because** two migrations and two ORM models cause it to be more complex than JSONB alternatives

### Option B: Fully normalised with self-referential FK only

* **Good, because** column-level querying and indexing (`name`, `physical_type`) work without JSON operators
* **Good, because** mirrors the existing `DataQualitySummary` / `DataQualityTechnicalAsset` pattern
* **Good, because** supports arbitrary nesting depth with no schema changes; the service layer tree-builder is depth-agnostic
* **Neutral, because** tree reconstruction happens in Python rather than SQL, which is acceptable given schemas are always fetched per output port
* **Bad, because** two migrations and two ORM models cause it to be more complex than JSONB alternatives
* **Bad, because** requires a recursive CTE to build the full schema of a single output port

### Option C: JSONB blob for full schema

* **Good, because** ingestion is trivial as the Bitol `schema:` block is stored as-is
* **Good, because** atomic replace of the full schema in a single write
* **Good, because** handles arbitrary nesting with zero extra modelling
* **Bad, because** column-level search requires JSON operators and cannot use standard indexes efficiently
* **Bad, because** diverges from the normalised pattern used for data quality
* **Bad, because** putting restriction or schema validation on content, needs to happen outside.

### Option D: Hybrid (schema object and jsonb for properties)

* **Good, because** one table instead of two; schema objects are queryable
* **Good, because** handles arbitrary nesting naturally within the JSON array
* **Bad, because** accessing top-level and nested properties works differently, creating an inconsistent service layer
* **Bad, because** column-level search features are not supported
* **Bad, because** diverges from the normalised pattern used for data quality
