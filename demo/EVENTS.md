# Events documentation

Using Webhooksite to capture the events and documenting so we can use it to implement provisioners.

## Creating a new data product

```
{
  "method": "POST",
  "url": "/api/v2/data_products",
  "query": "",
  "response": "{\"id\":\"cb5a2c67-5727-4d55-ad0e-4910701d336e\"}",
  "status_code": 200
}
```

## Updating a data product
```
{
  "method": "PUT",
  "url": "/api/v2/data_products/cb5a2c67-5727-4d55-ad0e-4910701d336e",
  "query": "",
  "response": "",
  "status_code": 200
}
```

## Deleting a data product
```
{
  "method": "DELETE",
  "url": "/api/v2/data_products/cb5a2c67-5727-4d55-ad0e-4910701d336e",
  "query": "",
  "response": "",
  "status_code": 200
}
```

## Approving an output port accesss request

```
{
  "method": "POST",
  "url": "/api/v2/data_products/33244836-8878-4d96-a098-85471d7e2c16/output_ports/f9d1d396-51bd-432f-be70-a238124711f0/input_ports/approve",
  "query": "",
  "response": "null",
  "status_code": 200
}
```

# Request payloads

## Updating a data product
Verb: PUT
Address: api/v2/data_products/970be9df-4d42-4fb7-968c-f516345a9495
Payload:
```
{"name":"Logistics WMS Shipments","namespace":"logistics-wms-shipments","description":"Tracks order shipment and delivery status from the warehouse.","type_id":"99ed24ed-2816-417f-b8b2-7ec4300d3f34","lifecycle_id":"1264036d-2430-4125-a5e2-784fafaedc72","domain_id":"03341c55-92ca-456a-9331-fb23055472fe","tag_ids":[]}
```


## Creating a PosPostgreSQLTechnicalAssetConfigurationtgres technical asset

Verb: POST
Address: api/v2/data_products/970be9df-4d42-4fb7-968c-f516345a9495/technical_assets
Payload:
```
{"name":"Customer 360","namespace":"customer-360","description":"Customer 369","tag_ids":[],"status":"active","technical_mapping":"custom","platform_id":"99898d61-ba3b-4f30-a929-8356ccfe521f","service_id":"242d7e16-edd5-41e1-9e25-775ecc29706e","configuration":{"configuration_type":"PostgreSQLTechnicalAssetConfiguration","database":"dpp_demo","schema":"customer+360","access_granularity":"schema","table":"*"},"result":"dpp_demo.customer+360.*"}
```
