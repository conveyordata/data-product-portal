import factory

from app.core.auth.device_flows.model import DeviceFlow


class DeviceFlowFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DeviceFlow
