from .. import TestingSessionLocal
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
    UserFactory,
]

for factory_model in factories:
    factory_model._meta.sqlalchemy_session = TestingSessionLocal()  # type: ignore
    factory_model._meta.sqlalchemy_session_persistence = "commit"  # type: ignore
