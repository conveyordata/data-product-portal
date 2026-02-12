"""
Example staging model for {{ cookiecutter.project_name }}

This is a simple starter model that you can use as a template.
Replace this with your actual data transformations.
"""

from sqlmesh import model


@model(
    "staging.example_data",
    kind="FULL",
    cron="@daily",
    columns={"id": "int", "name": "text", "created_at": "timestamp", "value": "double"},
    description="Example staging table - replace with your actual data",
)
def execute(context, **kwargs):
    """
    This is a simple example model.

    Replace this with your actual data transformation logic:
    - Read from source files (CSV, Parquet, JSON, etc.)
    - Load from external databases
    - Transform raw data into staging format
    """
    return context.fetchdf("""
    SELECT
        1 as id,
        'example' as name,
        CURRENT_TIMESTAMP as created_at,
        3.14 as value
    UNION ALL
    SELECT
        2 as id,
        'sample' as name,
        CURRENT_TIMESTAMP as created_at,
        2.71 as value
    """)
