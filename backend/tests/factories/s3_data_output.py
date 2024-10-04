import factory

from app.data_outputs.s3_data_output.model import S3DataOutput


class S3DataOutputFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = S3DataOutput

    id = factory.Faker("uuid4")
    bucket = "bucket"
    path = "path"
    suffix = ""
