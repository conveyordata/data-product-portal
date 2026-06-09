import uuid
from collections import defaultdict
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.data_products.output_ports.contract.model import (
    OutputPortSchemaObject,
    OutputPortSchemaProperty,
)
from app.data_products.output_ports.contract.schema_request import (
    BitolContractRequest,
    SchemaPropertyRequest,
)
from app.data_products.output_ports.contract.schema_response import (
    OutputPortSchemaResponse,
    SchemaObjectResponse,
    SchemaPropertyResponse,
)


class OutputPortContractService:
    def __init__(self, db: Session):
        self.db = db

    def ingest_contract(
        self, output_port_id: UUID, contract: BitolContractRequest
    ) -> OutputPortSchemaResponse:
        self.db.execute(
            delete(OutputPortSchemaObject).where(
                OutputPortSchemaObject.output_port_id == output_port_id
            )
        )

        for position, obj_req in enumerate(contract.schema_objects):
            obj_id = uuid.uuid4()
            self.db.add(
                OutputPortSchemaObject(
                    id=obj_id,
                    output_port_id=output_port_id,
                    name=obj_req.name,
                    logical_type=obj_req.logical_type,
                    physical_type=obj_req.physical_type,
                    physical_name=obj_req.physical_name,
                    description=obj_req.description,
                    position=position,
                )
            )
            for prop in self._flatten_properties(obj_req.properties, obj_id, None):
                self.db.add(prop)

        self.db.commit()
        return self.get_schema(output_port_id)

    def get_schema(self, output_port_id: UUID) -> OutputPortSchemaResponse:
        schema_objects = (
            self.db.query(OutputPortSchemaObject)
            .filter(OutputPortSchemaObject.output_port_id == output_port_id)
            .order_by(OutputPortSchemaObject.position)
            .all()
        )

        all_properties = (
            self.db.query(OutputPortSchemaProperty)
            .filter(
                OutputPortSchemaProperty.schema_object_id.in_(
                    [o.id for o in schema_objects]
                )
            )
            .order_by(
                OutputPortSchemaProperty.schema_object_id,
                OutputPortSchemaProperty.position,
            )
            .all()
        )

        props_by_schema_object: dict[
            UUID, dict[UUID | None, list[OutputPortSchemaProperty]]
        ] = defaultdict(lambda: defaultdict(list))
        for p in all_properties:
            props_by_schema_object[p.schema_object_id][p.parent_property_id].append(p)

        return OutputPortSchemaResponse(
            output_port_id=output_port_id,
            schema_objects=[
                SchemaObjectResponse(
                    id=obj.id,
                    name=obj.name,
                    logical_type=obj.logical_type,
                    physical_type=obj.physical_type,
                    physical_name=obj.physical_name,
                    description=obj.description,
                    position=obj.position,
                    properties=self._build_properties_tree(
                        props_by_schema_object[obj.id], parent_id=None
                    ),
                )
                for obj in schema_objects
            ],
        )

    @classmethod
    def _build_properties_tree(
        cls,
        props_by_parent: dict[UUID | None, list[OutputPortSchemaProperty]],
        parent_id: UUID | None,
    ) -> list[SchemaPropertyResponse]:
        schema_properties: list[SchemaPropertyResponse] = []
        for p in props_by_parent.get(parent_id, []):
            nested_properties = cls._build_properties_tree(props_by_parent, p.id)
            schema_properties.append(
                SchemaPropertyResponse(
                    id=p.id,
                    name=p.name,
                    business_name=p.business_name,
                    logical_type=p.logical_type,
                    physical_type=p.physical_type,
                    description=p.description,
                    examples=p.examples,
                    position=p.position,
                    partitioned=p.partitioned,
                    partition_key_position=p.partition_key_position,
                    required=p.required,
                    primary_key=p.primary_key,
                    primary_key_position=p.primary_key_position,
                    properties=nested_properties
                    if len(nested_properties) > 0
                    else None,
                )
            )
        return schema_properties

    @staticmethod
    def _flatten_properties(
        properties: list[SchemaPropertyRequest],
        schema_object_id: UUID,
        parent_id: UUID | None,
        start_position: int = 0,
    ) -> list[OutputPortSchemaProperty]:
        result = []
        for i, prop in enumerate(properties):
            prop_id = uuid.uuid4()
            result.append(
                OutputPortSchemaProperty(
                    id=prop_id,
                    schema_object_id=schema_object_id,
                    parent_property_id=parent_id,
                    name=prop.name,
                    business_name=prop.business_name,
                    logical_type=prop.logical_type,
                    physical_type=prop.physical_type,
                    description=prop.description,
                    examples=prop.examples,
                    position=start_position + i,
                    partitioned=prop.partitioned,
                    partition_key_position=prop.partition_key_position,
                    primary_key=prop.primary_key,
                    primary_key_position=prop.primary_key_position,
                    unique=prop.unique,
                    required=prop.required,
                )
            )
            if prop.properties:
                result.extend(
                    OutputPortContractService._flatten_properties(
                        prop.properties, schema_object_id, prop_id
                    )
                )
        return result
