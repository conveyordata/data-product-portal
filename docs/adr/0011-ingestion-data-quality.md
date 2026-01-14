# Ingest data quality results in Portal

## Consumers would benefit from data quality results on Output ports

In order to be confident in an output port, it would be helpful to show measure of quality.
We would like to show a high-level view or summary in Portal, without the details of the individual checks as to not rewrite DQ tooling.

This summary should easily be calculated based on the output of the DQ tooling using a simple script.
The portal API will support ingesting the summary of data quality results.

In the future we can simplify the ingestion process by providing an SDK or creating a plugin for different DQ tooling.
We currently store the summary results on output ports, but the summary contains high-level information about the technical assets.

## Decision Drivers

* Minimize the friction for producers to ingest data quality results
* Integrate with existing DQ tooling instead of creating a new standard
* Keep the quality data for Portal simple

## Considered Options

* **Ingest minimal data** For every quality run, store: timestamp, boolean, detail url link. This is the minimum necessary to show success/failure of quality check
* **Ingest all DQ checks** Have all granular details to calculate data quality. Ingest full run_results.json containing the data quality checks.
* **Extract a summary of DQ results** Calculate a summary of the data quality results using a simple script.


## Decision Outcome

**Chosen option:** *Extract a summary of the DQ results*.
It is the middle ground between the two extremes and provides the best of both worlds.
- We store only a summary and thus do not reinvent DQ tooling
- The summary provides some extra useful information over just a boolean value, which can be useful to gauge quality

## Pros and Cons of the Options

### Option 1: Ingest minimal data

* **Good, because** the data is very simple to manage in Portal.
* **Good, because** it is the simplest option to integrate with DQ tooling
* **Bad, because** it requires a minimal script to calculate the overall status based on the DQ checks
* **Bad, because** we lack some information about the assets for this output port
* **Bad, because** makes it difficult to extend DQ data later on as we have no clear concepts.
  This would mean going to Option 3 anyway if needed

### Option 2: Ingest all DQ checks

* **Good, because** for producers, they could just send the DQ results to Portal, to our SDK to process.
* **Bad, because** all DQ tools are widely different which makes it hard to find a least common denominator
* **Bad, because** it is more complex to store and display all DQ results in an easy overview

### Option 3: Extract a summary of DQ results

* **Good, because** it can provide all the necessary details for showing actionable DQ in portal
* **Good, because** it support many extension possibilities in the future, when we come up with extra dimensions.
* **Neutral, because** it is relatively simple to calculate a summary based on the different DQ results of Soda, dbt, Great expectations
* **Bad, because** it requires a simple script to calculate the summary as an extra step after running the DQ checks

Summary submitted by a producer could look as follows:

```
{
  "generated_at": "2026-01-12T08:15:00Z",
  "overall_status": "WARN",
  "summary": "Optional extra user info",
  "technical_assets": [
    {
      "name": "orders",
      "status": "PASS"
    },
    {
      "name": "order_items",
      "status": "WARN"
    },
    {
      "name": "customers",
      "status": "ERROR"
    }
  ],
  "dimensions": {
    "completeness": "WARN", #Are records missing or partial
    "validity": "PASS" # Do values have the expected format, ranges,...
    "coverage": # Can be calculated by portal as assets with checks/total assets
  },
  "details_url": "https://ci.company.com/runs/123"
}
```

Important note:
- status can have 3 values: PASS, WARN, FAIL
- The dimensions are optional and are inferred best effort based on the type of checks
- The asset details combine all checks for a given asset into one value
- The overall status is calculated based on the different asset details
- It can be that checks are executed for assets that are not exposed by the output port. These should be filtered out by Portal.
  Portal enriches the summary with the following stats:
```
{
"assets": {
  "total_assets": 3,                # Portal technical assets for this output port
  "with_checks": 2,                 # Portal assets with checks in the summary provided
  "with_issues": 1                  # Portal assets with failures/warnings in the summary provided
  }
}
```
