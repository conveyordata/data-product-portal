from datetime import date as DateType

from sqlalchemy import Column, ForeignKey, Integer, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, column_property, mapped_column

from app.database.database import Base


class DatasetQueryStatsDaily(Base):
    __tablename__ = "dataset_query_stats_daily"
    date: Mapped[DateType] = mapped_column(primary_key=True)
    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("datasets.id"), primary_key=True, index=True
    )
    consumer_data_product_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_products.id"), primary_key=True, index=True
    )
    query_count: Mapped[int] = mapped_column(Integer, default=0)

    # Computed field: consumer_data_product_name from join
    consumer_data_product_name = column_property(
        select(Column("name", String))
        .select_from(Base.metadata.tables["data_products"])
        .where(Base.metadata.tables["data_products"].c.id == consumer_data_product_id)
        .correlate_except(Base.metadata.tables["data_products"])
        .scalar_subquery()
    )
