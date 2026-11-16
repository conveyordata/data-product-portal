---
name: postgres-semantic
description: "Use for ANY PostgreSQL interaction — queries, schema exploration, metrics, or business data questions. MUST be used before postgres tools to load semantic models containing business context, field mappings, and validated metric formulas."
---

# PostgreSQL Semantic Model Integration

Load semantic models before any database operation. They contain business rules, exact field expressions, and validated metrics that make queries correct.

## Workflow

### Step 1: Find your semantic models (MANDATORY FIRST STEP)

Your semantic models are the files listed under "Semantic Models" in your instructions. Use only those: other files under `/products` belong to data products you have no access to, so never list or read them.

If no files are listed, skip to Step 5 and query directly.

### Step 2: Load the listed models

Before calling any database tool, read every listed file:

```python
read_file(file_name="/products/<namespace>/osi.yml")
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
