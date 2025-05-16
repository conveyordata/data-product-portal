from fastapi import APIRouter, Security

from app.authorization.router import router as authorization
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
from app.graph.router import router as graph
from app.platforms.router import router as platform
from app.role_assignments.router import router as role_assignment
from app.roles.router import router as role
from app.tags.router import router as tag
from app.theme_settings.router import router as theme_settings
from app.users.router import router as user
from app.integrations.router import router as integrations

router = (
    APIRouter(dependencies=[Security(api_key_authenticated)])
    if get_boolean_variable("OIDC_ENABLED", False)
    else APIRouter()
)

router.include_router(authorization)
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
router.include_router(role_assignment)
router.include_router(theme_settings)
router.include_router(integrations)
router.include_router(graph)
