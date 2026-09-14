import factory

from app.abstract_data_product.type import AbstractDataProductType
from app.configuration.access_durations.enums import AccessDurationType
from app.configuration.access_durations.model import AccessDuration
from tests import TestingSessionLocal


class AccessDurationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AccessDuration

    id = factory.Faker("uuid4")
    abstract_data_product_type = AbstractDataProductType.DATA_PRODUCT
    access_duration_type = AccessDurationType.PERMANENT
    days = None
    is_default = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        session = TestingSessionLocal()
        instance = (
            session.query(model_class)
            .filter(
                model_class.abstract_data_product_type
                == kwargs["abstract_data_product_type"],
                model_class.access_duration_type == kwargs["access_duration_type"],
            )
            .one_or_none()
        )

        if instance is None:
            return super()._create(model_class, *args, **kwargs)

        for key, value in kwargs.items():
            setattr(instance, key, value)
        session.flush()
        return instance
