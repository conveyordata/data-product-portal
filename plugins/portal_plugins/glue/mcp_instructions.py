MCP_INSTRUCTIONS = """
    ═══════════════════════════════════════════════════════════════════════
    DATA QUERY FLOW (Glue / Athena — Steps 4–8)
    ═══════════════════════════════════════════════════════════════════════

    Step 4: CHECK ACCESS — TRY CONSUMING DATA PRODUCTS FIRST 🔑
    ────────────────────────────────────────────────────────────
    get_aws_credentials(namespace, environment)
    Try consuming data product namespaces first, then the owner namespace.
    Use the same namespace for ALL subsequent calls.

    Step 5: GET DATABASE + BUCKET + WORKGROUP
    ────────────────────────────────────────────
    get_glue_database(environment, technical_asset_id, data_product_namespace)
    → Returns {'database': '...', 'bucket': '...', 'workgroup': '...'}
    → Resolves database name from owner's technical asset (always correct)
    → Resolves workgroup for the CONSUMING data product (data_product_namespace param)
    → Use database directly in SQL queries — no prefix computation needed.
    → Pass bucket and workgroup to query_athena (both optional).

    CRITICAL: Pass data_product_namespace (consuming product) to get the correct workgroup!
    The workgroup template is rendered for the consumer's namespace, allowing them to
    query using their own IAM role and workgroup permissions.

    Step 6: LIST TABLES
    ────────────────────
    list_glue_tables(data_product_namespace, environment, database_name)

    Step 7: EXECUTE QUERY
    ──────────────────────
    query_athena(data_product_namespace, env, query, bucket=None, workgroup=None)
    → Use the database name from get_glue_database directly in the SQL:
      SELECT * FROM "datalake_prod_my-product__sales"."users"
    → Always quote names that contain hyphens.

    Step 8: GET RESULTS
    ────────────────────
    get_athena_query_results(query_execution_id, data_product_namespace, env)
    → RUNNING → wait 3-5 s and retry
    → SUCCEEDED → return formatted rows
    → FAILED    → show error
"""
