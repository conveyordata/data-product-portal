import random

from sqlalchemy import select
from tests import test_session
from tests.factories.data_output import DataOutputFactory
from tests.factories.data_outputs_datasets import DataOutputDatasetAssociationFactory
from tests.factories.data_product import DataProductFactory
from tests.factories.data_products_datasets import DataProductDatasetAssociationFactory
from tests.factories.dataset import DatasetFactory

from app.platform_services.model import PlatformService


def add_random_data(
    nr_of_data_products: int = 50,
    nr_of_datasets: int = 50,
):
    """
    Add random data products and datasets to the database.
    """
    data_products = []
    data_outputs = []

    # Get the S3 service from the database for data output creation
    service = test_session.scalar(
        select(PlatformService).where(PlatformService.name == "S3")
    )

    # Create data products and data outputs and associate them with each other
    for _ in range(nr_of_data_products):
        data_product = DataProductFactory()

        for _ in range(random.randint(0, 3)):
            data_output = DataOutputFactory(owner=data_product, service=service)
            data_outputs.append(data_output)

        data_products.append(data_product)

    # Create datasets and associate them with random data products and data outputs
    for _ in range(nr_of_datasets):
        dataset = DatasetFactory()

        # Add data outputs to the dataset
        for _ in range(random.randint(0, 3)):
            data_output = random.choice(data_outputs)

            DataOutputDatasetAssociationFactory(
                data_output=data_output,
                dataset=dataset,
            )

        # Add data products to the dataset
        for _ in range(random.randint(0, 3)):
            data_product = random.choice(data_products)

            DataProductDatasetAssociationFactory(
                data_product=data_product,
                dataset=dataset,
            )


if __name__ == "__main__":
    add_random_data()
