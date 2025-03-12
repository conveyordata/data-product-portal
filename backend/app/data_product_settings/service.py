from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_settings.enums import DataProductSettingScope
from app.data_product_settings.model import (
    DataProductSetting as DataProductSettingModel,
)
from app.data_product_settings.model import (
    DataProductSettingValue as DataProductSettingValueModel,
)
from app.data_product_settings.schema import (
    DataProductSetting,
    DataProductSettingUpdate,
    DataProductSettingValueCreate,
)
from app.dependencies import (
    OnlyWithProductAccessDataProductID,
    only_dataset_owners,
)
from app.users.schema import User


class DataProductSettingService:
    def get_data_product_settings(self, db: Session) -> list[DataProductSetting]:
        return (
            db.query(DataProductSettingModel)
            .order_by(DataProductSettingModel.order, DataProductSettingModel.name)
            .all()
        )

    def set_value_for_product(
        self,
        setting_id: UUID,
        product_id: UUID,
        value: str,
        authenticated_user: User,
        db: Session,
    ):
        scope = db.get(DataProductSettingModel, setting_id).scope
        if scope == DataProductSettingScope.DATAPRODUCT:
            OnlyWithProductAccessDataProductID([DataProductUserRole.OWNER])(
                data_product_id=product_id, authenticated_user=authenticated_user, db=db
            )
            setting = db.scalars(
                select(DataProductSettingValueModel).filter_by(
                    data_product_id=product_id, data_product_setting_id=setting_id
                )
            ).first()
        elif scope == DataProductSettingScope.DATASET:
            only_dataset_owners(
                id=product_id, authenticated_user=authenticated_user, db=db
            )
            setting = db.scalars(
                select(DataProductSettingValueModel).filter_by(
                    dataset_id=product_id, data_product_setting_id=setting_id
                )
            ).first()
        if setting:
            setting.value = value
        else:
            if scope == DataProductSettingScope.DATAPRODUCT:
                new_setting = DataProductSettingValueCreate(
                    data_product_id=product_id,
                    data_product_setting_id=setting_id,
                    value=value,
                )
            elif scope == DataProductSettingScope.DATASET:
                new_setting = DataProductSettingValueCreate(
                    dataset_id=product_id,
                    data_product_setting_id=setting_id,
                    value=value,
                )
            db.add(DataProductSettingValueModel(**new_setting.parse_pydantic_schema()))
        db.commit()

    def create_data_product_setting(
        self, setting: DataProductSetting, db: Session
    ) -> dict[str, UUID]:
        setting = DataProductSettingModel(**setting.parse_pydantic_schema())
        db.add(setting)
        db.commit()
        return {"id": setting.id}

    def update_data_product_setting(
        self, id: UUID, setting: DataProductSettingUpdate, db: Session
    ) -> dict[str, UUID]:
        db.query(DataProductSettingModel).filter_by(id=id).update(
            setting.parse_pydantic_schema()
        )
        db.commit()
        return {"id": id}

    def delete_data_product_setting(self, setting_id: UUID, db: Session):
        db.query(DataProductSettingModel).filter_by(id=setting_id).delete()
        db.commit()
