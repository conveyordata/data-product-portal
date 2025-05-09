import factory

from app.data_output_configuration.s3.model import S3DataOutput


class S3DataOutputFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = S3DataOutput

    id = factory.Faker("uuid4")
    bucket = "bucket"
    path = "path"
    suffix = ""
