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

As a single query can join multiple assets (tables), we propose to split the stats into 2 different tables, one for the output port stats and one for the asset stats. Here is an example:

```
-- Query from consumer C1 on output port OP1
SELECT order_id, customer_id, product_id, pice FROM OP1.orders;

-- Query from consumer C2 on output port OP1
SELECT order_id, customer, product, pice FROM P1.orders INNER JOIN OP1.customers ON OP1.orders.customer_id = OP1.customers.id;
```

This would result in the following stats: 
* Consumer (C1, OP1) query count: 1
* Consumer (C2, OP1) query count: 1
* Asset (orders) query count: 2
* Asset (customers) query count: 1

To summarise:
* Asset query counts cannot be used to calculate consumer query counts as this would lead to incorrect aggregations
* We want to be able to delete assets and their stats without impacting hystorical consumer query counts

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
