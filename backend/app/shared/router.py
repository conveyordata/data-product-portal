from fastapi import APIRouter, Security

from app.authorization.role_assignments.router import router as role_assignment
from app.authorization.roles.router import router as role
from app.authorization.router import router as authorization
from app.configuration.data_product_lifecycles.router import (
    router as data_product_lifecycle,
)
from app.configuration.data_product_settings.router import (
    router as data_product_setting,
)
from app.configuration.data_product_types.router import router as data_product_type
from app.configuration.domains.router import router as domain
from app.configuration.environments.router import router as environment
from app.configuration.platforms.router import router as platform
from app.configuration.tags.router import router as tag
from app.configuration.theme_settings.router import router as theme_settings
from app.core.auth.auth import api_key_authenticated
from app.core.config.env_var_parser import get_boolean_variable
from app.data_products.output_port_technical_assets_link.router import (
    router as data_output_dataset,
)
from app.data_products.output_ports.router import router as dataset
from app.data_products.router import router as data_product
from app.data_products.technical_assets.router import router as data_outputs
from app.data_products_datasets.router import router as data_product_dataset
from app.graph.router import router as graph
from app.notifications.router import router as notification
from app.pending_actions.router import router as pending_action
from app.resource_names.router import router as resource_name
from app.search_output_ports.router import router as search_output_ports
from app.users.router import router as user

router = (
    APIRouter(dependencies=[Security(api_key_authenticated)])
    if get_boolean_variable("OIDC_ENABLED", False)
    else APIRouter()
)

router.include_router(authorization)
router.include_router(search_output_ports)
router.include_router(dataset)
router.include_router(data_product)
router.include_router(data_product_type)
router.include_router(data_product_lifecycle)
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
router.include_router(graph)
router.include_router(notification)
router.include_router(pending_action)
router.include_router(resource_name)
