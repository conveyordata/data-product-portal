# Provisioner

## Running locally

`poetry run fastapi dev ./provisioner/main.py`

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{ "method": "POST", "url": "/api/data_products", "query": "", "response": "{\"id\":\"97a3bf4c-12b9-4f03-aff5-8917aef0b0e7\"}", "status_code": 200 }' \
  http://localhost:8000/
```
