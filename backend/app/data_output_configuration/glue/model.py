from sqlalchemy.orm import Mapped, mapped_column

from app.data_output_configuration.base_model import BaseDataOutputConfiguration


class GlueDataOutput(BaseDataOutputConfiguration):
    database: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    database_suffix: Mapped[str] = mapped_column(
        nullable=True, use_existing_column=True
    )
    table: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    bucket_identifier: Mapped[str] = mapped_column(
        nullable=True, use_existing_column=True
    )
    database_path: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    table_path: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)

    __mapper_args__ = {
        "polymorphic_identity": "GlueDataOutput",
        "polymorphic_load": "inline",
    }
