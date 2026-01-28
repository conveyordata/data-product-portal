from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.data_output_configuration.base_model import BaseDataOutputConfiguration


class GlueDataOutput(BaseDataOutputConfiguration):
    __tablename__ = "glue_data_output_configurations"

    database: Mapped[str] = mapped_column(String, nullable=True)
    database_suffix: Mapped[str] = mapped_column(String, nullable=True)
    table: Mapped[str] = mapped_column(String, nullable=True)
    bucket_identifier: Mapped[str] = mapped_column(String, nullable=True)
    database_path: Mapped[str] = mapped_column(String, nullable=True)
    table_path: Mapped[str] = mapped_column(String, nullable=True)
    access_granularity: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "GlueDataOutput",
    }
