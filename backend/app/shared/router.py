from fastapi import APIRouter, Depends, Security

from app.audit.service import audit_logs
from app.core.auth.auth import api_key_authenticated
from app.core.config.env_var_parser import get_boolean_variable
from app.data_outputs.router import router as data_outputs
from app.data_outputs_datasets.router import router as data_output_dataset
from app.data_product_lifecycles.router import router as data_product_lifecycle
from app.data_product_memberships.router import router as data_product_membership
from app.data_product_settings.router import router as data_product_setting
from app.data_product_types.router import router as data_product_type
from app.data_products.router import router as data_product
from app.data_products_datasets.router import router as data_product_dataset
from app.datasets.router import router as dataset
from app.domains.router import router as domain
from app.environments.router import router as environment
from app.platforms.router import router as platform
from app.roles.router import router as role
from app.tags.router import router as tag
from app.users.router import router as user

router = (
    APIRouter(dependencies=[Security(api_key_authenticated), Depends(audit_logs)])
    if get_boolean_variable("OIDC_ENABLED", False)
    else APIRouter(dependencies=[Depends(audit_logs)])
)

router.include_router(dataset)
router.include_router(data_product)
router.include_router(data_product_type)
router.include_router(data_product_lifecycle)
router.include_router(data_product_membership)
router.include_router(data_product_setting)
router.include_router(data_product_dataset)
router.include_router(data_output_dataset)
router.include_router(data_outputs)
router.include_router(domain)
router.include_router(environment)
router.include_router(platform)
router.include_router(tag)
router.include_router(user)
router.include_router(role)
