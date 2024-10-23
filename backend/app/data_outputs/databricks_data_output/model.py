from sqlalchemy.orm import Mapped, mapped_column

from app.data_outputs.base_model import BaseDataOutputConfiguration


class DatabricksDataOutput(BaseDataOutputConfiguration):
    schema: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    schema_suffix: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    bucket_identifier: Mapped[str] = mapped_column(
        nullable=True, use_existing_column=True
    )
    schema_path: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)

    __mapper_args__ = {
        "polymorphic_identity": "DatabricksDataOutput",
    }
