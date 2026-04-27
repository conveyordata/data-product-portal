import factory

from app.data_products.output_ports.semantic_models.model import (
    OutputPortSemanticModel,
    SemanticModelFormat,
)

from .dataset import DatasetFactory


class OutputPortSemanticModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortSemanticModel

    id = factory.Faker("uuid4")
    output_port_id = factory.LazyAttribute(lambda o: DatasetFactory().id)
    name = factory.Faker("word")
    format = SemanticModelFormat.MetricsFlow
    content = factory.LazyFunction(lambda: {"version": 2, "models": []})
