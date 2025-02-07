from sqlalchemy.orm import Mapped, mapped_column

from app.data_outputs.base_model import BaseDataOutputConfiguration


class RedshiftDataOutput(BaseDataOutputConfiguration):
    bucket: Mapped[str] = mapped_column(nullable=True)
    suffix: Mapped[str] = mapped_column(nullable=True)
    path: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "RedshiftDataOutput",
    }
