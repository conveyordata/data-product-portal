# Provisioner

The provisioner is a level-based reconciler. On startup it resyncs every existing
data product, and the webhook endpoint (`POST /`) reconciles a data product again
whenever the portal emits a CloudEvent for it. Reconciliation is idempotent, so the
same event can safely be delivered multiple times.

## Running locally

`poetry run fastapi dev ./provisioner/main.py`

Send a data product CloudEvent to trigger a reconcile:

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{
    "specversion": "1.0",
    "type": "data_product.event",
    "source": "data-product-portal",
    "id": "evt-1",
    "time": "2024-01-01T00:00:00Z",
    "data": { "id": "97a3bf4c-12b9-4f03-aff5-8917aef0b0e7" }
  }' \
  http://localhost:8080/
```
