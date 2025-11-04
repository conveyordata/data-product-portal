# Ingestion of Output Port Usage Metrics

## Context and Problem Statement
We must get daily aggregated usage data from producers (like Snowflake) into our application.

The ingestion mechanism must be simple for producers, who will need to run two different aggregation queries on their raw query logs and push the results to us.

## Decision Drivers

* Developer Experience: Must be simple for producers, even though they now have to provide two distinct metrics.
* Reliability: The pipeline must be robust (retries, error handling).
* Separation of Concerns: We must define a clear boundary of responsibility between DPP and the producer's systems.
* Atomic Pushes: The push for both query stats and asset stats should be treated as a single unit of work for a given day.

## Considered Options

* **Option 1: Direct REST Endpoint Push** Producers use the REST endpoint directly in their pipeline. We provide the API endpoint and documentation. Producers are responsible for implementing all HTTP logic: authentication, request formatting, JSON serialization, and error/retry handling. They are also 100% responsible for generating the aggregation queries.
* **Option 2: Fluent Python SDK (Simple API Wrapper)** We offer an SDK to give a more friendly interface to push this data. We provide a lightweight Python SDK (data-portal-sdk). This SDK handles all API complexity: authentication, request formatting, and retries. Producers are still responsible for running their own aggregation queries (we provide SQL snippets), but they simply pass the resulting list of dictionaries to a single SDK method.
* **Option 3: Fluent Python SDK (Full Snowflake Integration)** We offer an advanced SDK that provides a friendly interface to push data, an interface on how to gather data, and a Snowflake implementation of that interface. We provide an "advanced" SDK that includes snowflake-connector-python as a dependency. The SDK defines an interface (e.g., an abstract base class) for data gathering. We ship a concrete SnowflakeUsageCollector implementation. Producers would instantiate this collector, (potentially) pass in their Snowflake credentials, and the SDK would be responsible for both running the aggregation queries and pushing the data.

## Decision Outcome

**Chosen option:** *Option 2: Fluent Python SDK (Simple API Wrapper)*. While we would love to go for option 3, we think option 2 is the most realistic atm. We can already take some pieces (e.g. the interface) from option 3.

* It provides a Good DX for producers by abstracting all API complexity (auth, retries, payload formatting) into a single client.push_usage_stats(...) method.

* It maintains a Clear Separation of Concerns. The producer is responsible for data generation (running the SQL in their own environment), and our SDK is responsible for data transmission.

* It avoids the complexity of Option 3.

### Confirmation
Description how this will be reflected in the appliction.

The SDK will provide a single method. This method will call the API endpoint defined in ADR-0006. Our API backend will be responsible for transactionally committing both payloads. This provides the best guarantee of data consistency.

Ideally we are able to generate a client completly from the OpenAPI spec and add a usage layer on top.

```python
# Producer's script (e.g., in Airflow)
from data_portal_sdk import DataPortalClient
from my_snowflake_connector import get_daily_stats

# 1. Producer runs the aggregation queries (implementing the SDK interface)
daily_stats = get_daily_stats(id="...")

# 2. Producer uses the simple SDK to push both payloads at once
client = DataPortalClient(api_key=MY_API_KEY)
client.push_usage_stats(
    id="1234-5678-9012-3456",
    query_stats=daily_stats.query_stats,
    asset_stats=daily_stats.asset_stats
)
```

## Pros and Cons of the Options

### Option 1: Direct REST

* **Good, because** No SDK to Maintain: Zero client-side maintenance for our team.
* **Bad, because** High implementation burden on producers. They must all individually implement auth, error handling, and retries. Very error-prone.

### Option 2: Simple SDK

* **Good, because** Good DX: Simple for producers
* **Good, because** Clear Separation of Concerns: We own the API client (transmission); producers own their data (generation).
* **Good, because** Low SDK Maintenance: The SDK is just an HTTP wrapper.
* **Medium, because** Producers still have to write/run the SQL.

### Option 2: Advanced SDK

* **Good, because** Best DX (in theory): Producers just configure the SDK. We can enforce the correct query logic.
* **Bad, because** SDK Complexity: We now own and maintain a complex client with snowflake-connector-python as a dependency.
* **Bad, because** Dependency/Security Risk: We must manage the Snowflake driver version and may have to handle producer credentials.
* **Bad, because** Blurs Responsibility: We become responsible if their queries fail.
