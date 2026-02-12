"""
Example data mart model for {{ cookiecutter.project_name }}

This model transforms staging data into a final data mart table.
"""

from sqlmesh import model


@model(
    "data_mart.example_summary",
    kind="FULL",
    cron="@daily",
    columns={
        "total_count": "bigint",
        "avg_value": "double",
        "min_value": "double",
        "max_value": "double",
    },
    description="Example summary table - aggregates staging data",
)
def execute(context, **kwargs):
    """
    Example transformation that aggregates staging data.

    Replace this with your actual business logic:
    - Join multiple staging tables
    - Calculate metrics and KPIs
    - Create dimension and fact tables
    """
    staging_table = context.resolve_table("staging.example_data")

    return context.fetchdf(f"""
    SELECT
        COUNT(*) as total_count,
        AVG(value) as avg_value,
        MIN(value) as min_value,
        MAX(value) as max_value
    FROM {staging_table}
    """)
