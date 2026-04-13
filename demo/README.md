# Data Product Portal Demos

This directory contains various demo scenarios to showcase the capabilities of the Data Product Portal.

## Demo Requirements & Structure

Every demo should be self-contained in its own subdirectory and follow these requirements to ensure consistency and ease of use:

- **Separate Folder**: Each demo lives in its own subdirectory within `demo/` (e.g., `demo/basic/`).
- **Orchestration**: A `compose.yaml` file that extends the root project's `compose.yaml` to minimize configuration overhead.
- **Isolated Infrastructure**: Demos should run their own database containers (e.g., `postgresql-demo`) to avoid polluting the main development environment.
- **Initial State (Seeds)**:
  - `portal_seed.sql`: Used to initialize the Portal database with metadata like domains, users, roles, and initial data product definitions.
  - `data_sources_seed.sql`: Used to populate the source database with the raw operational data that the demo will transform into data products.
- **Environment Configuration**:
  - `.env.portal`: Specific environment variables for the Portal backend and frontend.
  - `.env.data_sources`: Connection details and credentials for the demo data sources.
- **Automation**: A `Taskfile.yml` to provide common entry points like `task reset` or `task prepare-demo`.
- **Scenario Documentation**: A local `README.md` explaining the business context and the narrative flow of the demo.


## Existing Demos

### [Basic Demo](./basic/README.md)
**Goal**: Showcase the core value proposition of the Data Product Portal using a simple E-Commerce scenario.
- Demonstrates source-aligned vs. consumer-aligned data products.
- Shows how to use the Portal to discover and request access to data.
- Includes a functional **Provisioner** that automatically scaffolds dbt projects when a new data product is created in the UI.

#### Toil & Maintenance

The following components require regular updates to remain compatible with the core platform:

- **Provisioner Service**: The `provisioner/` FastAPI application must be maintained to handle changes in the Portal's API or webhook payload structures.
- **dbt Templates & Projects**: The dbt projects in `products/` and the cookiecutter templates in `provisioner/templates/` must be updated if dbt-core versions change or if the connection profiles need adjustment.
- **SQL Seed Synchronization**: The `portal_seed.sql` files must be kept in sync with the backend's database models. If new required fields are added to `DataProduct` or `Dataset` models, the seed scripts must be updated accordingly.

### [Agents Demo](./agents/README.md)
**Goal**: Showcase how the Data Product Portal provisions AI agents alongside data products, using SwiftGear (an outdoor gear retailer) as the business scenario.
- Each data product automatically gets a scoped PostgreSQL user, an OSI semantic model, and an Agno AI agent.
- Agents use the semantic model to answer business questions correctly (e.g. monetary values in cents, retired inventory filters).
- When a data product's input port access request is approved, the consumer agent gains cross-schema query access and inherits the provider's semantic model — enabling cross-domain analytics.
- Includes a functional **Provisioner** that handles both product creation and link approval webhooks, and an **Agno Agent Server** that hot-reloads agent configs as access is granted.

#### Toil & Maintenance

See [agents/README.md — Toil & Maintenance](agents/README.md#toil--maintenance).


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

# When a request is made for access from product 558e67c7-9f70-43b2-8be1-56d367a3e5c1 to access output port 43b7d0df-889d-4207-b74c-8729be2577da
```
{
  "method": "POST",
  "url": "/api/v2/data_products/558e67c7-9f70-43b2-8be1-56d367a3e5c1/link_input_ports",
  "query": "",
  "response": "{\"input_port_links\":[\"43b7d0df-889d-4207-b74c-8729be2577da\"]}",
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

## Updating the about of a data product
```
{
  "method": "PUT",
  "url": "/api/v2/data_products/e37a5989-57bc-4273-8117-9ede8a2583cc/about",
  "query": "",
  "response": "",
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

## Updating the about of a data product
Verb: PUT
Address: api/v2/data_products/664b3b49-8546-4357-a8fe-bb556a768009/about
Payload:
```
{"about":"<p><strong>Value Proposition</strong></p><p>This data product establishes a single source of truth for customer identities. By unifying fragmented CRM records, it enables consistent personalization, improved customer relationship management, and highly targeted marketing efforts across all business units.</p><p></p><p><strong>User Consumption Mode</strong></p><p>Analytical &amp; Operational:&nbsp;Optimized for both high-performance operational lookups and comprehensive historical trend analysis.</p><p></p><p><strong>Recommended Use Cases</strong></p><ul><li><p>Marketing:&nbsp;Segmentation for email campaigns and loyalty programs.</p></li><li><p>Support:&nbsp;Providing agents with a 360-degree view of customer history.</p></li><li><p>Data Science:&nbsp;Building churn prediction and lifetime value models..</p></li></ul><p></p><p><strong>Terms of Use</strong></p><ul><li><p>Usage:&nbsp;Approved for all internal analytics, marketing automation, and customer support workflows.</p></li><li><p>Limitations:&nbsp;Not authorized for external regulatory reporting. Handing of PII must strictly adhere to the corporate GDPR compliance framework.</p></li></ul><p></p><p></p>"}
```

## Creating a PosPostgreSQLTechnicalAssetConfigurationtgres technical asset

Verb: POST
Address: api/v2/data_products/970be9df-4d42-4fb7-968c-f516345a9495/technical_assets
Payload:
```
{"name":"Customer 360","namespace":"customer-360","description":"Customer 369","tag_ids":[],"status":"active","technical_mapping":"custom","platform_id":"99898d61-ba3b-4f30-a929-8356ccfe521f","service_id":"242d7e16-edd5-41e1-9e25-775ecc29706e","configuration":{"configuration_type":"PostgreSQLTechnicalAssetConfiguration","database":"dpp_demo","schema":"customer+360","access_granularity":"schema","table":"*"},"result":"dpp_demo.customer+360.*"}
```
