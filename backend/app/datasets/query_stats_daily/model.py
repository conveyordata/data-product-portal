from datetime import date as DateType

from sqlalchemy import ForeignKey, Integer, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, column_property, mapped_column

from app.data_products.model import DataProduct
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

    consumer_data_product_name = column_property(
        select(DataProduct.name)
        .where(DataProduct.id == consumer_data_product_id)
        .correlate_except(DataProduct)
        .scalar_subquery()
    )
