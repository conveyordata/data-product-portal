from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.namespace.validation import (
    DataProductSettingNamespaceValidator,
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
    NamespaceValidityType,
)
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
from app.dependencies import OnlyWithProductAccessDataProductID, only_dataset_owners
from app.users.schema import User


class DataProductSettingService:
    def __init__(self):
        self.namespace_validator = DataProductSettingNamespaceValidator()

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
        RefreshInfrastructureLambda().trigger()

    def create_data_product_setting(
        self, setting: DataProductSetting, db: Session
    ) -> dict[str, UUID]:
        if (
            validity := self.namespace_validator.validate_namespace(
                setting.namespace, db, setting.scope
            ).validity
        ) != NamespaceValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        setting = DataProductSettingModel(**setting.parse_pydantic_schema())
        db.add(setting)
        db.commit()
        return {"id": setting.id}

    def update_data_product_setting(
        self, id: UUID, setting: DataProductSettingUpdate, db: Session
    ) -> dict[str, UUID]:
        current_setting = db.get(DataProductSettingModel, id)
        update_setting = setting.model_dump(exclude_unset=True)

        if (
            current_setting.namespace != setting.namespace
            and (
                validity := self.namespace_validator.validate_namespace(
                    setting.namespace, db, current_setting.scope
                ).validity
            )
            != NamespaceValidityType.VALID
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        for k, v in update_setting.items():
            setattr(current_setting, k, v)

        db.commit()
        return {"id": id}

    def delete_data_product_setting(self, setting_id: UUID, db: Session):
        db.query(DataProductSettingModel).filter_by(id=setting_id).delete()
        db.commit()

    def validate_data_product_settings_namespace(
        self, namespace: str, scope: DataProductSettingScope, db: Session
    ) -> NamespaceValidation:
        return self.namespace_validator.validate_namespace(namespace, db, scope)

    def data_product_settings_namespace_suggestion(
        self, name: str
    ) -> NamespaceSuggestion:
        return self.namespace_validator.namespace_suggestion(name)

    def data_product_settings_namespace_length_limits(self) -> NamespaceLengthLimits:
        return self.namespace_validator.namespace_length_limits()
