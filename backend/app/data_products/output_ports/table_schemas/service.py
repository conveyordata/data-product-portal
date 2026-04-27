from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.configuration.tags.model import Tag, ensure_tag_exists
from app.data_products.output_ports.table_schemas.model import (
    OutputPortColumn,
    OutputPortTableSchema,
)
from app.data_products.output_ports.table_schemas.schema_request import (
    TableSchemaRequest,
)


class TableSchemaService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, output_port_id: UUID) -> list[OutputPortTableSchema]:
        return (
            self.db.query(OutputPortTableSchema)
            .filter(OutputPortTableSchema.output_port_id == output_port_id)
            .order_by(OutputPortTableSchema.name)
            .all()
        )

    def create(
        self, output_port_id: UUID, request: TableSchemaRequest
    ) -> OutputPortTableSchema:
        tags = self._fetch_tags(request.tag_ids)
        schema = OutputPortTableSchema(
            output_port_id=output_port_id,
            name=request.name,
            description=request.description,
            tags=tags,
        )
        schema.columns = [
            OutputPortColumn(
                name=col.name,
                description=col.description,
                data_type=col.data_type,
                tags=self._fetch_tags(col.tag_ids),
            )
            for col in request.columns
        ]
        self.db.add(schema)
        self.db.commit()
        self.db.refresh(schema)
        return schema

    def replace(
        self, schema_id: UUID, request: TableSchemaRequest
    ) -> OutputPortTableSchema:
        schema = self._get_or_404(schema_id)
        schema.name = request.name
        schema.description = request.description
        schema.tags = self._fetch_tags(request.tag_ids)
        schema.columns = [
            OutputPortColumn(
                name=col.name,
                description=col.description,
                data_type=col.data_type,
                tags=self._fetch_tags(col.tag_ids),
            )
            for col in request.columns
        ]
        self.db.commit()
        self.db.refresh(schema)
        return schema

    def delete(self, schema_id: UUID) -> None:
        schema = self._get_or_404(schema_id)
        self.db.delete(schema)
        self.db.commit()

    def _get_or_404(self, schema_id: UUID) -> OutputPortTableSchema:
        schema = self.db.get(OutputPortTableSchema, schema_id)
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table schema {schema_id} not found",
            )
        return schema

    def _fetch_tags(self, tag_ids: list[UUID]) -> list[Tag]:
        return [ensure_tag_exists(tag_id, self.db) for tag_id in tag_ids]
