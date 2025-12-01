#  REST API Endpoints for Output Port Usage

## Context and Problem Statement
We need a comprehensive set of API endpoints for the usage feature. This includes:

* Consumer-Facing: GET endpoints for the UI to read and display data.
* Producer-Facing: POST/PUT/DELETE endpoints for producers to manage qualitative metadata (e.g., Curated Queries) via our UI.
* Ingestion: POST/PUT/DELETE endpoint to push quantitative daily statistics.

## Decision Drivers

* Separation of Concerns: Clearly separate read-only, metadata management, and bulk ingestion endpoints.
* Performance: Endpoints must be fast and lightweight.
* Developer Experience: Endpoints must be logical and well-defined.

## Considered Options

* **Option 1: One Monolithic Endpoint** Create a single endpoint `/api/datasets/{id}/usage` that handles everything.
* **Option 2: Separate Endpoints per Use Case** Create distinct endpoints for consumers (GET), producers (PUT/POST/DEL), and the ingestion pipeline.

## Decision Outcome

**Chosen option:** *Option 2: Separate Endpoints per Use Case*. Clean and more maintainable.

### Confirmation

#### Consumer-Facing Endpoints (Read-Only)

1. Queries Over Time
    * `GET /api/datasets/{id}/usage/time-series`
    * Query Params: `granularity=week|month|day` (default week), `time_range=90d|1y` (default 90d).

2. Curated Queries (List)
    * `GET /api/datasets/{id}/usage/curated-queries`

3. Most Popular Assets
    * `GET /api/datasets/{id}/usage/popular-assets`
    * Query Params: `time_range=90d (default).`

4. Most Often Combined With
    * `GET /api/datasets/{id}/usage/combined-with`
    * Query Params: `time_range=90d (default).`

#### Producer-Facing Endpoints (Metadata Management)

As we want to support sorting operations and don't expect too many curated queries, we provide as single atomic operation.

1. Create new curated query
    * `PUT /api/datasets/{id}/usage/curated-queries`
    * Payload: `{"curated_queries: [{"title": "string", "description": "string", "query_text": "string"}, ... ]}`
    * Response (200): The updated query object.


#### Ingestion Endpoint (Bulk Ingestion)

Push daily stats

* `PATCH /api/datasets/{id}/usage/time-series`

Payload:
```[json]
{
  "query_stats": [
    {
      "date": "YYYY-MM-DD",
      "consumer_id": "uuid",
      "query_count": "integer"
    }
  ],
  "asset_stats": [
    {
      "date": "YYYY-MM-DD",
      "asset_id": "uuid",
      "consumer_id": "uuid",
      "query_count": "integer"
    }
  ]
}
```

  - Success Response (202 Accepted): The data has been accepted for batch processing.
  - Limits: Requires payload size limit on this. We can solve splitting in the SDK (ADR-0007).


`DELETE /api/datasets/{id}/usage/time-series`
* Payload:
```[json]
{
  "date": "YYYY-MM-DD"
  "consumer_data_product_id": "uuid"
  "asset_id": "uuid"
}
```



## Pros and Cons of the Options

### Option 1: One Monolithic Endpoint

* **Good, because** simplistic single endpoint
* **Bad, because** exploding size of default outpur payload
* **Bad, because** Violates REST principles
* **Bad, because** No separation of concerns

### Option 2: Separate Endpoints per Use Case

* **Good, because** follows REST principles
* **Good, because** clear separation of concerns
* **Medium, because** introduces multiple endpoints, increasing complexity
