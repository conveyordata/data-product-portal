import datetime
from uuid import UUID

from pydantic import Field

from app.shared.schema import ORMModel


class OutputPortQueryStatsUpdate(ORMModel):
    date: datetime.date = Field(
        description="Day the queries were executed, in ISO 8601 format (YYYY-MM-DD)",
        examples=["2025-01-15"],
    )
    consumer_data_product_id: UUID = Field(
        description="ID of the data product that queried the output port"
    )
    query_count: int = Field(
        ge=0,
        description="Number of queries the consumer data product ran against the output port on this day. "
        "Overwrites any count previously sent for the same day and consumer.",
        examples=[42],
    )


class UpdateOutputPortQueryStatus(ORMModel):
    output_port_query_stats_updates: list[OutputPortQueryStatsUpdate] = Field(
        description="Daily query counts per consumer data product"
    )


class OutputPortQueryStatsDelete(ORMModel):
    date: datetime.date = Field(
        description="Day to delete, in ISO 8601 format (YYYY-MM-DD)",
        examples=["2025-01-15"],
    )
    consumer_data_product_id: UUID = Field(
        description="ID of the consumer data product whose count to delete"
    )
