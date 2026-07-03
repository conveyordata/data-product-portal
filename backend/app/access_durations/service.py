from sqlalchemy.orm import Session

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.access_durations.model import AccessDuration as AccessDurationModel
from app.access_durations.schema_request import AccessDurationUpdate
from app.access_durations.schema_response import AccessDuration


class AccessDurationService:
    def __init__(self, db: Session):
        self.db = db

    def get_default_access_duration(
        self, abstract_data_product_type: AbstractDataProductType
    ) -> AccessDuration | None:
        return (
            self.db.query(AccessDurationModel)
            .filter(
                AccessDurationModel.abstract_data_product_type
                == abstract_data_product_type,
                AccessDurationModel.is_default,
            )
            .first()
        )

    def get_access_durations_by_type(
        self, abstract_data_product_type: AbstractDataProductType
    ) -> list[AccessDuration]:
        return (
            self.db.query(AccessDurationModel)
            .filter(
                AccessDurationModel.abstract_data_product_type
                == abstract_data_product_type,
            )
            .all()
        )

    def get_access_duration(
        self,
        abstract_data_product_type: AbstractDataProductType,
        access_duration_type: AccessDurationType,
    ) -> AccessDuration | None:
        return (
            self.db.query(AccessDurationModel)
            .filter(
                AccessDurationModel.abstract_data_product_type
                == abstract_data_product_type,
                AccessDurationModel.access_duration_type == access_duration_type,
            )
            .first()
        )

    def get_access_durations(self) -> list[AccessDuration]:
        return self.db.query(AccessDurationModel).all()

    def update_access_duration(self, access_duration: AccessDurationModel):
        self.db.add(access_duration)
        self.db.commit()
        self.db.refresh(access_duration)
        return access_duration

    def upsert_access_duration(
        self,
        abstract_data_product_type: AbstractDataProductType,
        update: AccessDurationUpdate,
    ) -> list[AccessDurationModel]:
        self.db.query(AccessDurationModel).filter(
            AccessDurationModel.abstract_data_product_type == abstract_data_product_type
        ).delete()

        self.db.add(
            AccessDurationModel(
                abstract_data_product_type=abstract_data_product_type,
                access_duration_type=update.access_duration_type,
                days=update.days,
                is_default=True,
            )
        )

        if update.alternative_allowed:
            alternative_type = (
                AccessDurationType.PERMANENT
                if update.access_duration_type == AccessDurationType.TIME_BOUND
                else AccessDurationType.TIME_BOUND
            )
            self.db.add(
                AccessDurationModel(
                    abstract_data_product_type=abstract_data_product_type,
                    access_duration_type=alternative_type,
                    days=update.alternative_days,
                    is_default=False,
                )
            )

        self.db.commit()
        return self.get_access_durations_by_type(abstract_data_product_type)
