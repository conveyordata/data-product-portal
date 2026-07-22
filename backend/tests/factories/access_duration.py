import factory

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.access_durations.model import AccessDuration


class AccessDurationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AccessDuration
        sqlalchemy_get_or_create = (
            "abstract_data_product_type",
            "access_duration_type",
        )

    id = factory.Faker("uuid4")
    abstract_data_product_type = AbstractDataProductType.DATA_PRODUCT
    access_duration_type = AccessDurationType.PERMANENT
    days = None
    is_default = True
