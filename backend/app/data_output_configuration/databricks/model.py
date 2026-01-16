from sqlalchemy.orm import Mapped, mapped_column

from app.data_output_configuration.base_model import BaseDataOutputConfiguration


class DatabricksDataOutput(BaseDataOutputConfiguration):
    catalog: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    schema: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    bucket_identifier: Mapped[str] = mapped_column(
        nullable=True, use_existing_column=True
    )
    catalog_path: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    table: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    table_path: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    entire_schema: Mapped[bool] = mapped_column(
        nullable=True, use_existing_column=True, default=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "DatabricksDataOutput",
        "polymorphic_load": "inline",
    }
