from fastapi import APIRouter, Security

from app.business_areas.router import router as business_area
from app.core.auth.auth import api_key_authenticated
from app.core.config.env_var_parser import get_boolean_variable
from app.data_contracts.router import router as data_contract
from app.data_outputs.router import router as data_outputs
from app.data_outputs_datasets.router import router as data_output_dataset
from app.data_product_memberships.router import router as data_product_membership
from app.data_product_types.router import router as data_product_type
from app.data_products.router import router as data_product
from app.data_products_datasets.router import router as data_product_dataset
from app.datasets.router import router as dataset
from app.environments.router import router as environment
from app.platforms.router import router as platform
from app.users.router import router as user

router = (
    APIRouter(dependencies=[Security(api_key_authenticated)])
    if get_boolean_variable("OIDC_ENABLED", False)
    else APIRouter()
)
router.include_router(user)
router.include_router(environment)
router.include_router(dataset)
router.include_router(data_product)
router.include_router(data_product_type)
router.include_router(business_area)
router.include_router(data_product_dataset)
router.include_router(data_output_dataset)
router.include_router(data_product_membership)
router.include_router(data_outputs)
router.include_router(platform)
router.include_router(data_contract)
