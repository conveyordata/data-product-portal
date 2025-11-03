# Database Model for Output Port Curated Queries

## Context and Problem Statement
The "Curated Queries" feature allows data producers to manually define a list of up to 3 example queries for their data product.

## Decision Drivers

* Relational Integrity: Curated queries must be directly and clearly associated with a single ouput port.

* Write Simplicity: CREATE, UPDATE, and DELETE operations (from the producer-facing UI) should be simple, atomic, and efficient.

## Considered Options

* **Option 1: New output_port_curated_queries Table** Create a new, dedicated table with a foreign key to the data_products table. Each row represents one curated query.
* **Option 2: JSONB Column in outputport Table** Add a new JSONB column (e.g., curated_queries) to the existing data_products table. This column would hold a JSON array of query objects.

## Decision Outcome

**Chosen option:** *Option 1: New output_port_curated_queries Table*. This is the most robust and maintainable solution allowing more explicit schema management. The complexity of write operations for the JSONB model makes it unsuitable for data that is managed via item-specific CRUD operations.

### Confirmation

Table: output_port_curated_queries
Schema:
* curated_query_id (UUID, PK)
* output_port_id (UUID, FK, Indexed)
* title (VARCHAR(255))
* description (TEXT)
* query_text (TEXT)
* sort_order (SMALLINT) - To allow producers to order the queries
* created_at (TIMESTAMPZ)
* updated_at (TIMESTAMPZ)

## Pros and Cons of the Options

### Option 1:New output_port_curated_queries Table

* **Good, because** Clean/Normalized: Follows standard relational database design.
* **Good, because** Can easily query across all curated queries if needed in the future.
* **Bad, because** Requires a JOIN or separate SELECT to fetch queries with a output port.

### Option 2: JSONB Column in outputport Table

* **Good, because** No JOINs: All data is co-located in one row.
* **Bad, because** Complex Writes: PUT (update) and DELETE (remove) are extremely difficult. The application must read the entire JSON array, modify it, and write the entire array back, which is inefficient and creates a risk of race conditions.
