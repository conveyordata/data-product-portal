# Provisioner

## Running locally

`poetry run fastapi dev ./provisioner/main.py`

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{ "method": "POST", "url": "/api/data_products", "query": "", "response": "{\"id\":\"97a3bf4c-12b9-4f03-aff5-8917aef0b0e7\"}", "status_code": 200 }' \
  http://localhost:8000/
```


```
curl --header "Content-Type: application/json" \
  --request PUT \
  --data '{"lifecycle_id":"40cdce63-6acd-4812-9f82-0af9fd902411"}' \
  http://localhost:8080/api/data_products/97a3bf4c-12b9-4f03-aff5-8917aef0b0e7

```
