# Database Model for Output Port Usage Metrics

## Context and Problem Statement
To power the new usage charts, we must ingest and store analytics data from systems (e.g. Snowflake) into our application's PostgreSQL database. The data needs to support multiple, distinct features:

"Queries over time": A time-series chart of unique queries.
"Query distribution": A bar chart of unique queries aggregated by consumer.
"Most popular assets": A table of top assets (tables) by query touches.

A core scenario is: A single query (e.g., query_id: 'xyz') can join multiple assets (e.g., Table A and Table B) within the same output port. We must be able to count this as one query for the "Queries over time" chart, but also count one touch for Table A and one touch for Table B for the "Most popular assets" chart.

## Decision Drivers

* Query Performance: The API endpoints must return data quickly. 
* Storage Efficiency: We must avoid storing raw query logs.
* Metric Accuracy: The model must disambiguate between query counts (for time-series) and asset touch counts (for popularity).
* Flexibility: The model must support future granularities (daily, monthly) and longer time ranges.

## Considered Options

* **Option 1: Store Raw Query Logs** Ingest every query event, potentially with an array of assets touched.
* **Option 2: Aggregated Tables** Create two separate, specialized tables. One table aggregates query counts (ignoring assets) and the other aggregates asset quert counts per day.

## Decision Outcome

**Chosen option:** *Option 2: Aggregated Tables* Performance and efficiency as the main driver.

### Confirmation

#### Table 1: outpur_port_query_stats_daily

Purpose: To power the "Queries over time" and "Query distribution per consumer" charts.
Granularity: One row per (date, product, consumer, domain).

Schema:
* date (DATE, PK)
* output_port_id (UUID, PK, FK)
* consumer_id (UUID, PK, FK)
* query_count (INT)

#### Table 2: tech_asset_stats_daily

Purpose: To power the "Most popular assets" chart.

Schema:
* date (DATE, PK)
* output_port_id (UUID, PK, FK)
* tech_asset_id (UUID, PK, FK)
* consumer_id (UUID, PK, FK)
* query_count (INT)

## Pros and Cons of the Options

### Option 1 – Store Raw Query Logs

* **Good, because** Maximum Flexibility.
* **Bad, because** reason Unusable Performance: COUNT(DISTINCT) is a non-starter for dashboard queries.
* **Bad, because** High Storage Cost.

### Option 2 – Aggregated Tables

* **Good, because** Correctly Models Both Metrics: Perfectly solves the "join" scenario.
* **Good, because** Performance: All API queries are simple SUMs on pre-aggregated data. No COUNT(DISTINCT) needed.
* **Neutral, because** Slightly More Storage: (But still minimal compared to raw logs).
* **Bad, because** Slightly More Complex Ingestion: The pipeline must run two separate aggregation queries.
