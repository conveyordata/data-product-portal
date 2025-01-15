from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_settings.schema import (
    DataProductSetting,
    DataProductSettingCreate,
)
from app.data_product_settings.service import DataProductSettingService
from app.database.database import get_db_session
from app.dependencies import OnlyWithProductAccess, only_for_admin

router = APIRouter(prefix="/data_product_settings", tags=["data_product_settings"])


@router.get("")
def get_data_products_settings(
    db: Session = Depends(get_db_session),
) -> list[DataProductSetting]:
    return DataProductSettingService().get_data_product_settings(db)


@router.post("", dependencies=[Depends(only_for_admin)])
def create_data_product_setting(
    setting: DataProductSettingCreate,
    db: Session = Depends(get_db_session),
):
    return DataProductSettingService().create_data_product_setting(setting, db)


@router.put(
    "",
    dependencies=[Depends(only_for_admin)],
)
def update_data_product_setting(
    setting: DataProductSetting,
    db: Session = Depends(get_db_session),
):
    return DataProductSettingService().update_data_product_setting(setting, db)


@router.post(
    "/{data_product_id}/{setting_id}",
    dependencies=[Depends(OnlyWithProductAccess([DataProductUserRole.OWNER]))],
)
def set_value_for_data_product(
    data_product_id: UUID,
    setting_id: UUID,
    value: str,
    db: Session = Depends(get_db_session),
):
    return DataProductSettingService().set_value_for_product(
        setting_id, data_product_id, value, db
    )


@router.delete("", dependencies=[Depends(only_for_admin)])
def delete_data_product_setting(
    setting_id: UUID,
    db: Session = Depends(get_db_session),
):
    return DataProductSettingService().delete_data_product_setting(setting_id, db)
