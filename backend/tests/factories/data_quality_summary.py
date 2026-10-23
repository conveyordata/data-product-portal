import factory

from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.data_products.output_ports.data_quality.model import DataQualitySummary

from .output_port import OutputPortFactory


class DataQualitySummaryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataQualitySummary

    output_port_id = factory.LazyFunction(lambda: OutputPortFactory().id)
    overall_status = DataQualityStatus.SUCCESS
    dimensions: dict[str, str] = {}
