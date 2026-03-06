---
name: postgres-semantic
description: "Use this skill for ANY PostgreSQL database interaction - queries, schema exploration, data analysis, metric calculations, or business questions about data. This applies when users mention databases, SQL, tables, data queries, analytics, reporting, metrics, KPIs, customer data, sales data, inventory, revenue, or any data-related questions. CRITICAL - This skill MUST be used BEFORE any postgres: tools because it loads semantic models that contain essential business context, correct field mappings, relationship definitions, and pre-validated metric calculations. Using postgres tools without checking semantic models first will result in incorrect queries, wrong field names, missing business logic, and inaccurate results. Always check for semantic models first, even for simple queries."
---

# PostgreSQL Semantic Model Integration

**CRITICAL PRIORITY INSTRUCTION**: This skill MUST be triggered and used BEFORE any other PostgreSQL operations. Semantic models contain the source of truth for business logic, field mappings, and data relationships. Skipping this step will result in incorrect queries and inaccurate results.

This skill enhances PostgreSQL database interactions by leveraging semantic models when available. Semantic models provide business context, field definitions, relationships, and pre-defined metrics that make database queries more accurate and meaningful.

## Mandatory First Step

**BEFORE using ANY postgres: tools**, you MUST:
1. Check if semantic models exist
2. Load relevant semantic models
3. Apply the context from semantic models to your work

This is not optional. Even for "simple" queries, semantic models may contain critical business rules (like "prices are in cents, divide by 100" or "filter out retired items") that will make your query wrong if you skip this step.

## When to Use This Skill

**Use this skill for EVERY PostgreSQL interaction**, including:

### Database Queries & Analysis
- Writing SQL queries (SELECT, INSERT, UPDATE, DELETE)
- Analyzing database schema or table structure
- Understanding table relationships and foreign keys
- Computing metrics, aggregations, or KPIs
- Exploring data structure or available fields
- Answering business questions about data

### Common User Phrases That Trigger This Skill
- "How many customers..." / "Show me sales..." / "What's our revenue..."
- "Query the database..." / "Get data from..." / "Find records where..."
- "Calculate the total..." / "What's the average..." / "Count the..."
- "Join customers and orders..." / "Relationship between X and Y..."
- "What tables do we have..." / "Show me the schema..."
- "Active subscriptions" / "Inventory levels" / "Top products"
- Any mention of: database, SQL, query, table, data, metrics, analytics, reporting

### Why This Matters
Standard postgres: tools know the technical schema (tables, columns, types) but NOT:
- What fields actually mean in business terms
- What units values are stored in (cents vs dollars, seconds vs minutes)
- Which records to filter out (retired items, test accounts, deleted users)
- How to correctly join tables (some IDs look similar but mean different things)
- Pre-validated metric calculations used across the organization

Semantic models provide this critical context. Using postgres tools without them is like reading a foreign language without a dictionary.

## Core Workflow

### Overview
```
EVERY PostgreSQL task follows this sequence:
1. Check for semantic models (MANDATORY)
2. Load relevant models (if they exist)
3. Parse and understand the context
4. Apply context to your postgres operations
5. Use postgres: tools with correct field names and business logic
```

### Step 1: Check for Semantic Models (MANDATORY FIRST STEP)

**Do this BEFORE anything else**. Even before calling `postgres:list_tables` or any other postgres tool.

The semantic models are located at: `/products`

```bash
# Use bash to check if directory exists and list files
ls -la /products
```

Or use the Filesystem tool:
```python
Filesystem:list_directory(path="/products")
```

**Expected result**: You should see directories like `inventory-snapshot/`, `sales-transaction-ledger/`, `customer-demographic-master/` each containing `osi.yml`

**If directory doesn't exist or is empty**: Skip to Step 5 and use postgres tools directly (but this is rare)

### Step 2: Load Relevant Semantic Models

Once you've confirmed semantic models exist, load the ones relevant to the user's question. **When in doubt, load all of them** - it's better to have too much context than too little.

```python
# Read semantic model files
Filesystem:read_multiple_files(paths=[
    "/products/sales-transaction-ledger/osi.yml",
    "/products/customer-demographic-master/osi.yml",
    "/products/inventory-snapshot/osi.yml"
])
```

**Model Selection Guide:**

| User Question Contains | Load These Models | Why |
|------------------------|-------------------|-----|
| orders, revenue, subscriptions, transactions, purchases, payments, pricing | **sales-transaction-ledger/osi.yml** | Financial and transactional data |
| customers, users, sessions, acquisition, behavior, traffic, signups | **customer-demographic-master/osi.yml** | Customer and engagement data |
| inventory, stock, warehouse, products, SKUs, items, quantities | **inventory-snapshot/osi.yml** | Supply chain and product data |
| Unclear or multi-domain question | **All models** | Better to over-fetch context |

**Pro tip**: If the user's question mentions multiple domains (like "Which customers bought the most inventory?"), load all relevant models. The relationships section will show you how to correctly join across domains.

### Step 3: Parse and Understand Semantic Models

Semantic models are YAML files with this structure:

```yaml
name: domain_name
ai_context:
  instructions: "Critical business rules and gotchas - READ THIS FIRST"

datasets:
  - name: table_name
    source: schema.table_name
    fields:
      - name: business_friendly_name
        expression: actual_column_or_sql
        description: What this field represents
        ai_context:
          instructions: Usage notes and warnings
          synonyms: [other, names, users, might, use]

metrics:
  - name: metric_name
    expression: "SQL calculation (already validated)"
    description: What this metric measures

relationships:
  - from: this_domain.this_table
    to: other_domain.other_table
    on: join_condition
```

**What to extract from each section:**

1. **Domain Instructions** (`ai_context.instructions` at top level)
   - Critical business rules that apply to ALL queries in this domain
   - Common mistakes to avoid
   - Data quality issues or edge cases
   - Example: "All monetary values in cents - must divide by 100 for dollars"

2. **Datasets** (Tables)
   - Real table name: `source` field (like `sales_transaction_ledger.orders`)
   - Business-friendly name: `name` field
   - Available fields and what they mean

3. **Fields** (Columns)
   - Business name: What users call it
   - Technical expression: The actual SQL to use (might be `column_name` or `CASE WHEN...`)
   - Description: What it represents
   - AI context: Special usage notes, synonyms, warnings

4. **Metrics** (Pre-built calculations)
   - Name: How to reference it
   - Expression: The exact SQL (already validated by data team)
   - Use these instead of writing calculations from scratch

5. **Relationships** (Joins)
   - How to correctly join tables across domains
   - Which keys to use (some IDs look similar but aren't!)
   - Warnings about joins that might seem obvious but are wrong

### Step 4: Apply Semantic Context

Now that you understand the semantic models, use this context when formulating queries:

**Rule 1: Use Domain Instructions**
Look for `ai_context.instructions` at the domain level. These contain critical rules.

Example domain instruction:
```yaml
ai_context:
  instructions: "All monetary values are stored in cents. Always divide by 100 for dollar amounts."
```

Your query MUST include `/100.0` when selecting money fields:
```sql
SELECT total_amount / 100.0 AS total_dollars FROM sales_transaction_ledger.orders
```

**Rule 2: Use Exact Field Expressions**
Never guess column names. Use the `expression` from the semantic model.

**Rule 3: Use Pre-Defined Metrics**
If a metric exists, use its exact expression. Don't reinvent it.

**Rule 4: Respect Relationships**
Cross-reference the `relationships` section for correct joins.

**Rule 5: Honor AI Context Warnings**
Field-level `ai_context` often contains critical warnings about what NOT to do.

### Step 5: Use PostgreSQL Tools (Now You're Ready!)

**Only after** completing Steps 1-4, proceed with the standard PostgreSQL tools:

- `postgres:list_tables` - Explore available tables
- `postgres:list_table_stats` - Table statistics and metadata
- `postgres:execute_sql` - Run your context-aware query
- Other postgres: tools as needed

## Important Rules (Non-Negotiable)

1. **ALWAYS check for semantic models first** — before ANY postgres: tool
2. **Load all relevant models** — when in doubt, load all
3. **Use exact field expressions** — never guess column names
4. **Apply domain instructions religiously** — they prevent common errors
5. **Cite the semantic model** — mention you're using semantic model context
6. **Fall back gracefully** — if models don't exist, use postgres tools directly

## Quick Reference Checklist

```
□ Step 1: Check semantic models exist
  Command: ls /products

□ Step 2: Load relevant models (or all if unsure)
  Files: /products/inventory-snapshot/osi.yml
         /products/sales-transaction-ledger/osi.yml
         /products/customer-demographic-master/osi.yml

□ Step 3: Extract key information:
  □ Domain instructions (ai_context at top)
  □ Field expressions (use these, not guessed names)
  □ Metric formulas (use these, don't rewrite)
  □ Relationship mappings (for joins)

□ Step 4: Apply context to query:
  □ Use exact field expressions
  □ Apply domain rules (divide cents by 100, etc.)
  □ Use correct join conditions
  □ Include necessary filters

□ Step 5: Execute with postgres: tools
  □ Run query with postgres:execute_sql
  □ Cite semantic model in response
```

## Summary: The Golden Rule

**Semantic models are the source of truth for database business logic.**

```
EVERY PostgreSQL task = Check semantic models FIRST → Then use postgres: tools
```

Skip the semantic models → Get wrong results → Waste everyone's time

Use the semantic models → Get right results → Build trust → Ship value
