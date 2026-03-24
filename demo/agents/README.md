# Demo Scenario: AI Agents for Data Products

This demo showcases how the Data Product Portal can provision **AI agents** alongside data products. Each data product gets its own Agno agent — pre-configured with direct PostgreSQL access scoped to its schema and a semantic model that encodes business logic. When a data product requests access to another's output port and the request is approved, the consumer's agent automatically gains cross-schema query access and inherits the provider's semantic model.

The company is **SwiftGear**, a specialty outdoor gear retailer. Their data team is adopting data product thinking to make their operational data accessible and trustworthy — not just for engineers, but for analysts and AI agents.

## Prerequisites

### Domains

| Domain | Description |
| --- | --- |
| **Sales** | Responsible for all activities related to sales transactions, order management, and subscription revenue. |
| **Marketing** | Focused on customer acquisition, demographic data, and behavioral analytics. |
| **Logistics** | Manages inventory levels, warehouse operations, and stock lifecycle tracking. |

### Conceptual Data Model

SwiftGear's operational data spans three domains:

- **Inventory**: Daily stock snapshots and historical stock-level logs per SKU and warehouse.
- **Sales**: Order headers, line items, and subscription/recurring revenue records.
- **Customers**: Master customer records and anonymous web session logs.

### Source Data (in `dpp_demo` database)

Each data product owns a dedicated PostgreSQL schema in the `dpp_demo` database, provisioned automatically when the product is created.

#### `inventory_snapshot` schema

| Table | Description |
| --- | --- |
| `inventory_latest` | Current stock snapshot: SKU, quantity on hand, warehouse |
| `stock_levels` | Historical log of stock levels; includes a `is_retired` flag |

**Semantic gotcha:** Always filter `is_retired = FALSE` from `stock_levels` when computing sellable inventory. Use `inventory_latest` for current counts.

#### `sales_transaction_ledger` schema

| Table | Description |
| --- | --- |
| `orders` | Order headers: customer, amount, status, timestamps |
| `order_items` | Line items: order, SKU, quantity, price |
| `recurring_revenue` | Subscription MRR/ARR, status, churn dates |

**Semantic gotcha:** All monetary values are stored in **cents**. Divide by 100 for dollar amounts. The `calculated_total` column is a legacy error — ignore it.

#### `customer_demographic_master` schema

| Table | Description |
| --- | --- |
| `customers` | Master customer records: email, name, signup date |
| `web_sessions` | Anonymous session logs: page paths, timestamps |

**Semantic gotcha:** `acquired_by` in `customers` is an internal admin ID, not a customer ID — never join it to the customers table. Web session `user_id` is an anonymous UUID and cannot be joined directly to customers.

## Architecture

```
Portal UI
    │
    ├── creates data product → webhook → Provisioner
    │                                        │
    │                           ┌────────────┴───────────────┐
    │                           │                            │
    │                    provisions DB schema          writes agent config
    │                    creates OSI TA                to /agent_configs/
    │                    creates PostgreSQL TA         {namespace}.yml
    │                    updates lifecycle → Ready
    │
    ├── approves input port → webhook → Provisioner
    │                                        │
    │                           ┌────────────┴───────────────┐
    │                           │                            │
    │                    GRANT SELECT on              appends provider OSI
    │                    provider schema              file to consumer
    │                    to consumer user             agent config
    │
    └── Agno link → navigates to os.agno.com/chat
                        │
                    Agno Agent Server (port 7070)
                        │
                    reads /agent_configs/*.yml (hot-reload)
                        │
                    Agent per data product:
                    - MCP postgres (scoped user)
                    - FileTools (/products OSI files)
                    - LocalSkills (postgres-semantic)
```

## Scenario Steps

### 1. Configure Secrets

The Agno agent server requires an Anthropic API key. Copy the example file and fill it in — it is gitignored and never committed:

```bash
cd demo/agents
cp .env.secret.example .env.secret
# then edit .env.secret and set your ANTHROPIC_API_KEY
```

### 2. Start the Demo

```bash
task reset
```

Wait for all services to be healthy, then create the three data products:

```bash
task create-products
```

This triggers the provisioner for each product, which:
- Creates a dedicated PostgreSQL schema and user in `dpp_demo`
- Creates an OSI Semantic Model technical asset pointing to `/products/{namespace}/osi.yml`
- Creates a PostgreSQL technical asset scoped to the product's schema
- Writes an agent config YAML to the shared `agent_configs` volume
- Advances the data product lifecycle to **Ready**

### 3. Three Data Products, Three Agents

After creation, the portal shows three data products, each with:

| Data Product | Domain | Namespace | Agent User |
| --- | --- | --- | --- |
| Inventory Snapshot | Logistics | `inventory-snapshot` | `inventory_snapshot_user` |
| Sales Transaction Ledger | Sales | `sales-transaction-ledger` | `sales_transaction_ledger_user` |
| Customer Demographic Master | Marketing | `customer-demographic-master` | `customer_demographic_master_user` |

Each agent can only query its own schema. Try asking the **Inventory Snapshot** agent:
> *"How many camping items do we currently have in stock?"*

The agent will load the OSI semantic model first (via the `postgres-semantic` skill), understand that `inventory_latest` is the right table and that `sku LIKE 'CAMP-%'` identifies camping gear, then query PostgreSQL.

Try a trap question:
> *"What's our total inventory including retired items?"*

The semantic model's instructions tell the agent to always filter out retired items and to challenge incorrect premises.

### 4. Link Data Products (Cross-Domain Access)

To demonstrate access propagation, have the **Sales Transaction Ledger** request access to the **Inventory Snapshot** output port in the portal UI:

1. In the portal, navigate to **Sales Transaction Ledger**
2. Go to **Input Ports** → request access to **Inventory Snapshot**'s output port
3. Approve the request

The provisioner's webhook handler will:
- `GRANT SELECT ON ALL TABLES IN SCHEMA inventory_snapshot TO sales_transaction_ledger_user`
- Append `/products/inventory-snapshot/osi.yml` to the Sales Transaction Ledger agent config

The Agno server picks up the updated YAML via uvicorn hot-reload. Now ask the **Sales Transaction Ledger** agent a cross-domain question:
> *"Which of our top-selling SKUs are at risk of going out of stock?"*

The agent now has access to both `sales_transaction_ledger` and `inventory_snapshot` schemas, plus both semantic models to correctly interpret the data.

## Technical Asset Details

Each data product gets two technical assets automatically:

### OSI Semantic Model TA
Points to `/products/{namespace}/osi.yml` — the semantic model mounted into the Agno container. It encodes:
- Correct field expressions (e.g. `total_amount / 100.0` for dollar amounts)
- Business rules and AI gotchas
- Pre-validated metric formulas
- Cross-domain relationships

### PostgreSQL TA
Grants schema-level SELECT access in `dpp_demo`. The result string `dpp_demo.{schema}.*` is shown in the portal UI.

### Agno Link
The Agno plugin generates a link to `https://os.agno.com/chat?type=agent&id={namespace}`. Clicking it opens the agent chat for that data product in Agno's hosted UI.

## Toil & Maintenance

- **Provisioner Service**: Must be maintained to handle changes in the Portal's API or webhook payload structure. The approve-link handler extracts `consumer_data_product_id` from the webhook response — validate this if the Portal API changes.
- **OSI Semantic Models**: The `products/*/osi.yml` files are static. Update them when the underlying schema changes or when business logic evolves.
- **Agent Config Volume**: The `agent_configs` Docker volume is ephemeral by default. After a `docker compose down -v`, re-run `python setup/create_products.py` to regenerate.
- **SQL Seed Synchronization**: `portal_seed.sql` must stay in sync with the Portal's database schema. If new required fields are added to core models, update the seed accordingly.
