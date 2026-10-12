import datetime
import re
from typing import Annotated
from uuid import UUID

from pydantic import BeforeValidator, Field

from app.shared.schema import ORMModel


def _require_iso_date(value: object) -> object:
    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return value
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value
    raise ValueError("Input should be a date in YYYY-MM-DD format")


IsoDate = Annotated[datetime.date, BeforeValidator(_require_iso_date)]


class OutputPortQueryStatsUpdate(ORMModel):
    date: IsoDate = Field(
        description="Day the queries were executed, in ISO 8601 format (YYYY-MM-DD)",
        examples=["2025-01-15"],
    )
    consumer_data_product_id: UUID = Field(
        description="ID of the data product that queried the output port"
    )
    query_count: int = Field(
        strict=True,
        ge=0,
        le=2**31 - 1,
        description="Number of queries the consumer data product ran against the output port on this day. "
        "Overwrites any count previously sent for the same day and consumer.",
        examples=[42],
    )


class UpdateOutputPortQueryStatus(ORMModel):
    output_port_query_stats_updates: list[OutputPortQueryStatsUpdate] = Field(
        description="Daily query counts per consumer data product"
    )


class OutputPortQueryStatsDelete(ORMModel):
    date: IsoDate = Field(
        description="Day to delete, in ISO 8601 format (YYYY-MM-DD)",
        examples=["2025-01-15"],
    )
    consumer_data_product_id: UUID = Field(
        description="ID of the consumer data product whose count to delete"
    )
