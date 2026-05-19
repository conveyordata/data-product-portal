from typing import Any, Optional

from pydantic import BaseModel, Field


# Took relevant properties from: https://github.com/bitol-io/open-data-contract-standard/blob/main/docs/schema.md
class SchemaPropertyRequest(BaseModel):
    name: str
    business_name: Optional[str] = Field(None, alias="businessName")
    logical_type: Optional[str] = Field(None, alias="logicalType")
    physical_type: Optional[str] = Field(None, alias="physicalType")
    description: Optional[str] = None
    examples: Optional[list[Any]] = None
    primary_key: bool = Field(False, alias="primaryKey")
    primary_key_position: Optional[int] = Field(None, alias="primaryKeyPosition")
    unique: bool = False
    required: bool = False
    partitioned: bool = False
    partition_key_position: Optional[int] = Field(None, alias="partitionKeyPosition")
    properties: list["SchemaPropertyRequest"] = []

    model_config = {"populate_by_name": True}


SchemaPropertyRequest.model_rebuild()


class SchemaObjectRequest(BaseModel):
    name: str
    logical_type: Optional[str] = Field(None, alias="logicalType")
    physical_type: Optional[str] = Field(None, alias="physicalType")
    physical_name: Optional[str] = Field(None, alias="physicalName")
    description: Optional[str] = None
    properties: list[SchemaPropertyRequest] = []

    model_config = {"populate_by_name": True}


class BitolContractRequest(BaseModel):
    """
    Accepts a BitOL data contract (https://bitol-io.github.io/open-data-contract-standard/).
    Only the `schema` section is extracted; all other fields are ignored.
    """

    schema_objects: list[SchemaObjectRequest] = Field(default=[], alias="schema")

    model_config = {"populate_by_name": True}
