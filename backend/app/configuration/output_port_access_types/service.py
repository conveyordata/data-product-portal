from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.configuration.output_port_access_types.model import (
    OutputPortAccessType as OutputPortAccessTypeModel,
)
from app.configuration.output_port_access_types.model import (
    ensure_output_port_access_type_exists,
)
from app.configuration.output_port_access_types.schema_request import (
    OutputPortAccessTypeCreate,
    OutputPortAccessTypeUpdate,
)
from app.configuration.output_port_access_types.schema_response import (
    CreateOutputPortAccessTypeResponse,
    OutputPortAccessTypesGetItem,
    UpdateOutputPortAccessTypeResponse,
)
from app.core.authz import Action, Authorization
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.data_products.output_ports.service import OutputPortService
from app.database.database import UNFILTERED
from app.users.model import User


class OutputPortAccessTypeService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_output_port_access_types(
        self, user: User, include_output_port_count: bool
    ) -> Sequence[OutputPortAccessTypesGetItem]:
        counts = None
        if include_output_port_count:
            can_configure = Authorization().has_access(
                sub=str(user.id),
                dom="*",
                obj="*",
                act=Action.GLOBAL__UPDATE_CONFIGURATION,
            )
            counts = OutputPortService(self.db).count_by_access_type(
                include_hidden=can_configure
            )
        access_types = self.db.scalars(
            select(OutputPortAccessTypeModel).order_by(OutputPortAccessTypeModel.name)
        ).all()
        return [
            OutputPortAccessTypesGetItem(
                id=access_type.id,
                name=access_type.name,
                description=access_type.description,
                access_function=access_type.access_function,
                output_port_count=None
                if counts is None
                else counts.get(access_type.id, 0),
            )
            for access_type in access_types
        ]

    def create_output_port_access_type(
        self, request: OutputPortAccessTypeCreate
    ) -> CreateOutputPortAccessTypeResponse:
        access_type = OutputPortAccessTypeModel(**request.parse_pydantic_schema())
        self.db.add(access_type)
        self.db.flush()
        return CreateOutputPortAccessTypeResponse(id=access_type.id)

    def update_output_port_access_type(
        self, id: UUID, request: OutputPortAccessTypeUpdate
    ) -> UpdateOutputPortAccessTypeResponse:
        access_type = ensure_output_port_access_type_exists(id, self.db)
        access_type.name = request.name
        access_type.description = request.description
        if request.access_function != access_type.access_function:
            self._ensure_not_last_invite_only(access_type)
            access_type.access_function = request.access_function
            OutputPortService(self.db).remap_output_ports_access_function(
                access_type.id, request.access_function
            )
        self.db.flush()
        return UpdateOutputPortAccessTypeResponse(id=id)

    def delete_output_port_access_type(self, id: UUID) -> None:
        access_type = ensure_output_port_access_type_exists(id, self.db)
        self._ensure_not_last_invite_only(access_type)
        in_use = self.db.scalar(
            select(func.count())
            .select_from(OutputPortModel)
            .where(OutputPortModel.access_type_id == id),
            execution_options=UNFILTERED,
        )
        if in_use:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete an access type used by {in_use} output ports",
            )
        self.db.delete(access_type)
        self.db.flush()

    def _ensure_not_last_invite_only(
        self, access_type: OutputPortAccessTypeModel
    ) -> None:
        if (
            access_type.access_function == OutputPortAccessFunction.PRIVATE
            and self.db.scalar(
                select(func.count())
                .select_from(OutputPortAccessTypeModel)
                .where(
                    OutputPortAccessTypeModel.access_function
                    == OutputPortAccessFunction.PRIVATE
                )
            )
            == 1
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one access type must stay Invite only",
            )
