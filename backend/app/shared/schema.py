from uuid import UUID

from pydantic import BaseModel


class ORMModel(BaseModel):
    class Config:
        from_attributes = True

    @classmethod
    def is_pydantic(cls, obj: object):
        """Checks whether an object is pydantic."""
        return type(obj).__class__.__name__ == "ModelMetaclass"

    def parse_pydantic_schema(self):
        """
        Iterates through pydantic schema and parses nested schemas
        to a dictionary containing SQLAlchemy models.
        Only works if nested schemas have specified the Meta.orm_model.
        """
        parsed_schema = dict(self)
        for key, value in parsed_schema.items():
            try:
                if isinstance(value, list) and len(value):
                    if self.is_pydantic(value[0]):
                        parsed_schema[key] = [
                            schema.Meta.orm_model(**schema.dict()) for schema in value
                        ]
                else:
                    if self.is_pydantic(value):
                        parsed_schema[key] = value.Meta.orm_model(**value.dict())
            except AttributeError:
                parsed_schema[key] = value.model_dump_json()
        return parsed_schema


class IdNameSchema(ORMModel):
    id: UUID
    name: str
