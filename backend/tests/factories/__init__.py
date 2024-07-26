from .. import TestingSessionLocal
from .environment import EnvironmentFactory
from .platform import PlatformFactory
from .user import UserFactory

factories = [EnvironmentFactory, PlatformFactory, UserFactory]

for factory_model in factories:
    factory_model._meta.sqlalchemy_session = TestingSessionLocal()  # type: ignore
    factory_model._meta.sqlalchemy_session_persistence = "commit"  # type: ignore
