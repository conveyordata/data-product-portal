from tests import test_session

from .access_duration import AccessDurationFactory
from .data_product import DataProductFactory
from .data_product import fake as data_product_fake
from .data_product_setting import DataProductSettingFactory
from .data_product_setting_value import DataProductSettingValueFactory
from .data_product_type import DataProductTypeFactory
from .dataset import DatasetFactory
from .dataset import fake as dataset_fake
from .dataset_query_stats_daily import DatasetQueryStatsFactory
from .domain import DomainFactory
from .env_platform_config import EnvPlatformConfigFactory
from .env_platform_service_config import EnvPlatformServiceConfigFactory
from .environment import EnvironmentFactory
from .event import EventFactory
from .exploration import ExplorationFactory
from .exploration import fake as exploration_fake
from .input_port import InputPortFactory
from .lifecycle import LifecycleFactory
from .notification import NotificationFactory
from .platform import PlatformFactory
from .platform_service import PlatformServiceFactory
from .platform_service_config import PlatformServiceConfigFactory
from .role import RoleFactory
from .role_assignment_data_product import DataProductRoleAssignmentFactory
from .role_assignment_dataset import DatasetRoleAssignmentFactory
from .role_assignment_global import GlobalRoleAssignmentFactory
from .s3_data_output import S3DataOutputFactory
from .tags import TagFactory
from .technical_asset import TechnicalAssetFactory
from .technical_asset_output_ports import TechnicalAssetOutputPortAssociationFactory
from .theme_settings import ThemeSettingsFactory
from .user import UserFactory

_fakes_with_unique = [data_product_fake, dataset_fake, exploration_fake]


def reset_unique_fakers() -> None:
    """Reset the unique word pools of all Faker instances used by factories.

    Must be called between tests to prevent UniquenessException when Faker's
    word vocabulary is exhausted across the full test suite.
    """
    for fake in _fakes_with_unique:
        fake.unique.clear()


factories = [
    AccessDurationFactory,
    TechnicalAssetOutputPortAssociationFactory,
    DataProductFactory,
    DataProductSettingFactory,
    DataProductSettingValueFactory,
    DataProductTypeFactory,
    InputPortFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetQueryStatsFactory,
    DatasetRoleAssignmentFactory,
    DomainFactory,
    EnvPlatformConfigFactory,
    EnvPlatformServiceConfigFactory,
    EnvironmentFactory,
    EventFactory,
    GlobalRoleAssignmentFactory,
    LifecycleFactory,
    PlatformFactory,
    PlatformServiceFactory,
    PlatformServiceConfigFactory,
    RoleFactory,
    S3DataOutputFactory,
    TagFactory,
    UserFactory,
    TechnicalAssetFactory,
    ThemeSettingsFactory,
    NotificationFactory,
    ExplorationFactory,
]

for factory_model in factories:
    factory_model._meta.sqlalchemy_session = test_session  # type: ignore
    factory_model._meta.sqlalchemy_session_persistence = "commit"  # type: ignore
