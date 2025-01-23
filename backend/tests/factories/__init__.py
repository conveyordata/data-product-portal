from tests.factories.data_output import DataOutputFactory
from tests.factories.data_outputs_datasets import DataOutputDatasetAssociationFactory
from tests.factories.lifecycle import LifecycleFactory
from tests.factories.s3_data_output import S3DataOutputFactory

from .. import test_session
from .business_area import BusinessAreaFactory
from .data_product import DataProductFactory
from .data_product_membership import DataProductMembershipFactory
from .data_product_type import DataProductTypeFactory
from .data_products_datasets import DataProductDatasetAssociationFactory
from .dataset import DatasetFactory
from .env_platform_config import EnvPlatformConfigFactory
from .env_platform_service_config import EnvPlatformServiceConfigFactory
from .environment import EnvironmentFactory
from .platform import PlatformFactory
from .platform_service import PlatformServiceFactory
from .platform_service_config import PlatformServiceConfigFactory
from .user import UserFactory

factories = [
    EnvironmentFactory,
    PlatformFactory,
    PlatformServiceFactory,
    PlatformServiceConfigFactory,
    EnvPlatformServiceConfigFactory,
    UserFactory,
    BusinessAreaFactory,
    DatasetFactory,
    DataOutputFactory,
    DataProductFactory,
    DataProductMembershipFactory,
    DataProductTypeFactory,
    DataOutputDatasetAssociationFactory,
    DataProductDatasetAssociationFactory,
    EnvPlatformConfigFactory,
    S3DataOutputFactory,
    LifecycleFactory,
]

for factory_model in factories:
    factory_model._meta.sqlalchemy_session = test_session  # type: ignore
    factory_model._meta.sqlalchemy_session_persistence = "commit"  # type: ignore
