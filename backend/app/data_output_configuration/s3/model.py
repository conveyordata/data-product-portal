from sqlalchemy.orm import Mapped, mapped_column

from app.data_output_configuration.base_model import BaseDataOutputConfiguration


class S3DataOutput(BaseDataOutputConfiguration):
    bucket: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    suffix: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    path: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)

    __mapper_args__ = {
        "polymorphic_identity": "S3DataOutput",
        "polymorphic_load": "inline",
    }
