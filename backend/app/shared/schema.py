from uuid import UUID

from pydantic import BaseModel


class ORMModel(BaseModel):
    class Config:
        from_attributes = True

    @classmethod
    def is_pydantic(cls, obj: object) -> bool:
        """Checks whether an object is pydantic."""
        return type(obj).__class__.__name__ == "ModelMetaclass"

    @staticmethod
    def _orm_kwargs(schema: "ORMModel") -> dict:
        """model_dump() also includes computed fields; the ORM model only
        accepts its own real columns, so drop anything else."""
        return {
            key: value
            for key, value in schema.model_dump().items()
            if key in type(schema).model_fields
        }

    def parse_pydantic_schema(self) -> dict:
        """
        Iterates through pydantic schema and parses nested schemas
        to a dictionary containing SQLAlchemy models.
        Only works if nested schemas have specified the Meta.orm_model.
        """
        parsed_schema = dict(self)
        try:
            for key, value in parsed_schema.items():
                if isinstance(value, list) and len(value):
                    if self.is_pydantic(value[0]):
                        parsed_schema[key] = [
                            schema.Meta.orm_model(**self._orm_kwargs(schema))
                            for schema in value
                        ]
                else:
                    if self.is_pydantic(value):
                        parsed_schema[key] = value.Meta.orm_model(
                            **self._orm_kwargs(value)
                        )
        except AttributeError:
            raise AttributeError(
                "Found nested Pydantic model but Meta.orm_model was not specified."
            )
        return parsed_schema


class IdNameSchema(ORMModel):
    id: UUID
    name: str
