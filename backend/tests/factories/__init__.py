from .. import test_session
from .data_output import DataOutputFactory
from .data_outputs_datasets import DataOutputDatasetAssociationFactory
from .data_product import DataProductFactory
from .data_product_membership import DataProductMembershipFactory
from .data_product_setting import DataProductSettingFactory
from .data_product_type import DataProductTypeFactory
from .data_products_datasets import DataProductDatasetAssociationFactory
from .dataset import DatasetFactory
from .domain import DomainFactory
from .env_platform_config import EnvPlatformConfigFactory
from .env_platform_service_config import EnvPlatformServiceConfigFactory
from .environment import EnvironmentFactory
from .lifecycle import LifecycleFactory
from .platform import PlatformFactory
from .platform_service import PlatformServiceFactory
from .platform_service_config import PlatformServiceConfigFactory
from .role import RoleFactory
from .role_assignment_data_product import DataProductRoleAssignmentFactory
from .role_assignment_dataset import DatasetRoleAssignmentFactory
from .s3_data_output import S3DataOutputFactory
from .tags import TagFactory
from .theme_settings import ThemeSettingsFactory
from .user import UserFactory

factories = [
    DataOutputFactory,
    DataOutputDatasetAssociationFactory,
    DataProductFactory,
    DataProductMembershipFactory,
    DataProductSettingFactory,
    DataProductTypeFactory,
    DataProductDatasetAssociationFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    DomainFactory,
    EnvPlatformConfigFactory,
    EnvPlatformServiceConfigFactory,
    EnvironmentFactory,
    LifecycleFactory,
    PlatformFactory,
    PlatformServiceFactory,
    PlatformServiceConfigFactory,
    RoleFactory,
    S3DataOutputFactory,
    TagFactory,
    UserFactory,
    ThemeSettingsFactory,
]

for factory_model in factories:
    factory_model._meta.sqlalchemy_session = test_session  # type: ignore
    factory_model._meta.sqlalchemy_session_persistence = "commit"  # type: ignore
