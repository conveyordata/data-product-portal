from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data_product_settings.model import (
    DataProductSetting as DataProductSettingModel,
)
from app.data_product_settings.model import (
    DataProductSettingValue as DataProductSettingValueModel,
)
from app.data_product_settings.schema import (
    DataProductSetting,
    DataProductSettingValueCreate,
)


class DataProductSettingService:
    def get_data_product_settings(self, db: Session) -> list[DataProductSetting]:
        return (
            db.query(DataProductSettingModel)
            .order_by(DataProductSettingModel.order, DataProductSettingModel.name)
            .all()
        )

    def set_value_for_product(
        self, setting_id: UUID, product_id: UUID, value: str, db: Session
    ):
        setting = db.scalars(
            select(DataProductSettingValueModel).filter_by(
                data_product_id=product_id, data_product_setting_id=setting_id
            )
        ).first()
        if setting:
            setting.value = value
        else:
            new_setting = DataProductSettingValueCreate(
                data_product_id=product_id,
                data_product_setting_id=setting_id,
                value=value,
            )
            db.add(DataProductSettingValueModel(**new_setting.parse_pydantic_schema()))
        db.commit()
