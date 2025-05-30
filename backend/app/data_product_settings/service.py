from typing import Sequence
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
from app.data_product_settings.enums import DataProductSettingScope
from app.data_product_settings.model import (
    DataProductSetting as DataProductSettingModel,
)
from app.data_product_settings.model import (
    DataProductSettingValue as DataProductSettingValueModel,
)
from app.data_product_settings.schema_request import (
    DataProductSettingCreate,
    DataProductSettingUpdate,
    DataProductSettingValueCreate,
)
from app.data_product_settings.schema_response import DataProductSettingsGet


class DataProductSettingService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = DataProductSettingNamespaceValidator()

    def get_data_product_settings(self) -> Sequence[DataProductSettingsGet]:
        return self.db.scalars(
            select(DataProductSettingModel).order_by(
                DataProductSettingModel.order, DataProductSettingModel.name
            )
        ).all()

    def set_value_for_product(
        self,
        setting_id: UUID,
        product_id: UUID,
        value: str,
    ) -> None:
        scope = self.db.get(DataProductSettingModel, setting_id).scope
        if scope == DataProductSettingScope.DATAPRODUCT:
            setting = self.db.scalars(
                select(DataProductSettingValueModel).filter_by(
                    data_product_id=product_id, data_product_setting_id=setting_id
                )
            ).first()
        elif scope == DataProductSettingScope.DATASET:
            setting = self.db.scalars(
                select(DataProductSettingValueModel).filter_by(
                    dataset_id=product_id, data_product_setting_id=setting_id
                )
            ).first()
        else:
            setting = None

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
            self.db.add(
                DataProductSettingValueModel(**new_setting.parse_pydantic_schema())
            )
        self.db.commit()
        RefreshInfrastructureLambda().trigger()

    def create_data_product_setting(
        self, setting: DataProductSettingCreate
    ) -> dict[str, UUID]:
        if (
            validity := self.namespace_validator.validate_namespace(
                setting.namespace, self.db, setting.scope
            ).validity
        ) != NamespaceValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        setting = DataProductSettingModel(**setting.parse_pydantic_schema())
        self.db.add(setting)
        self.db.commit()
        return {"id": setting.id}

    def update_data_product_setting(
        self, id: UUID, setting: DataProductSettingUpdate
    ) -> dict[str, UUID]:
        current_setting = self.db.get(DataProductSettingModel, id)
        update_setting = setting.model_dump(exclude_unset=True)

        if (
            current_setting.namespace != setting.namespace
            and (
                validity := self.namespace_validator.validate_namespace(
                    setting.namespace, self.db, current_setting.scope
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

        self.db.commit()
        return {"id": id}

    def delete_data_product_setting(self, setting_id: UUID) -> None:
        data_product_setting = self.db.get(
            DataProductSettingModel,
            setting_id,
        )
        self.db.delete(data_product_setting)
        self.db.commit()

    def validate_data_product_settings_namespace(
        self, namespace: str, scope: DataProductSettingScope
    ) -> NamespaceValidation:
        return self.namespace_validator.validate_namespace(namespace, self.db, scope)

    @classmethod
    def data_product_settings_namespace_suggestion(
        cls, name: str
    ) -> NamespaceSuggestion:
        return DataProductSettingNamespaceValidator.namespace_suggestion(name)

    @classmethod
    def data_product_settings_namespace_length_limits(cls) -> NamespaceLengthLimits:
        return DataProductSettingNamespaceValidator.namespace_length_limits()
