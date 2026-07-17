import factory

from app.technical_asset_configuration.s3.model import S3TechnicalAssetConfiguration


class S3DataOutputFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = S3TechnicalAssetConfiguration

    id = factory.Faker("uuid4")
    bucket = "bucket"
    path = "path"
    suffix = ""
