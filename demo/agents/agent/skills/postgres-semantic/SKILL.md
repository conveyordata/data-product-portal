---
name: postgres-semantic
description: "Use for ANY PostgreSQL interaction — queries, schema exploration, metrics, or business data questions. MUST be used before postgres tools to load semantic models containing business context, field mappings, and validated metric formulas."
---

# PostgreSQL Semantic Model Integration

Load semantic models before any database operation. They contain business rules, exact field expressions, and validated metrics that make queries correct.

## Workflow

### Step 1: Check for semantic models (MANDATORY FIRST STEP)

Before calling any database tool, list the semantic models at `/products`:

```python
list_files(path="/products")
```

If the directory is empty or missing, skip to Step 5 and query directly.

### Step 2: Load relevant models

Load model files matching the user's question:

| Question contains | Load |
|---|---|
| orders, revenue, transactions, payments, pricing | `sales-transaction-ledger/osi.yml` |
| customers, users, sessions, acquisition, behavior | `customer-demographic-master/osi.yml` |
| inventory, stock, warehouse, products, SKUs | `inventory-snapshot/osi.yml` |
| unclear or multi-domain | all models |

```python
read_file(path="/products/sales-transaction-ledger/osi.yml")
read_file(path="/products/customer-demographic-master/osi.yml")
read_file(path="/products/inventory-snapshot/osi.yml")
```

### Step 3: Extract from each model

- **`ai_context.instructions`** (top level) — critical business rules for all queries
- **`datasets[].source`** — actual schema.table name to query
- **`datasets[].fields[].expression`** — exact SQL expression to use (never guess)
- **`metrics[].expression`** — pre-validated SQL calculation (use as-is)
- **`relationships[]`** — correct join conditions across domains

### Step 4: Apply context

1. Apply domain instructions (e.g., divide cents by 100 for dollar amounts)
2. Use exact field `expression` values — never invent column names
3. Use pre-defined metric expressions verbatim
4. Use `relationships` for cross-domain joins
5. Respect field-level `ai_context` warnings

### Step 5: Query the database

```python
show_tables()           # list available tables
describe_table(table="schema.table")  # table structure
run_query(query="SELECT ...")         # execute SQL
```

Always cite which semantic rule or metric you applied in your response.
