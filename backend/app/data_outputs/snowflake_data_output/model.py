from sqlalchemy.orm import Mapped, mapped_column

from app.data_outputs.base_model import BaseDataOutputConfiguration


class SnowflakeDataOutput(BaseDataOutputConfiguration):
    database: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    schema: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    table: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    bucket_identifier: Mapped[str] = mapped_column(
        nullable=True, use_existing_column=True
    )
    database_path: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    table_path: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)

    __mapper_args__ = {
        "polymorphic_identity": "SnowflakeDataOutput",
    }
