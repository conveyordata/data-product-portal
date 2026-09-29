from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.configuration.output_port_classifications.model import (
    OutputPortClassification as OutputPortClassificationModel,
)
from app.configuration.output_port_classifications.model import (
    ensure_output_port_classification_exists,
)
from app.configuration.output_port_classifications.schema_request import (
    OutputPortClassificationCreate,
    OutputPortClassificationUpdate,
)
from app.configuration.output_port_classifications.schema_response import (
    CreateOutputPortClassificationResponse,
    OutputPortClassificationsGetItem,
    UpdateOutputPortClassificationResponse,
)
from app.core.authz import Action, Authorization
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.service import OutputPortService
from app.users.model import User


class OutputPortClassificationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_output_port_classifications(
        self, user: User
    ) -> Sequence[OutputPortClassificationsGetItem]:
        can_configure = Authorization().has_access(
            sub=str(user.id), dom="*", obj="*", act=Action.GLOBAL__UPDATE_CONFIGURATION
        )
        counts = OutputPortService(self.db).count_by_classification(
            include_hidden=can_configure
        )
        classifications = self.db.scalars(
            select(OutputPortClassificationModel).order_by(
                OutputPortClassificationModel.name
            )
        ).all()
        return [
            OutputPortClassificationsGetItem(
                id=classification.id,
                name=classification.name,
                description=classification.description,
                access_function=classification.access_function,
                output_port_count=counts.get(classification.id, 0),
            )
            for classification in classifications
        ]

    def create_output_port_classification(
        self, request: OutputPortClassificationCreate
    ) -> CreateOutputPortClassificationResponse:
        classification = OutputPortClassificationModel(
            **request.parse_pydantic_schema()
        )
        self.db.add(classification)
        self.db.flush()
        return CreateOutputPortClassificationResponse(id=classification.id)

    def update_output_port_classification(
        self, id: UUID, request: OutputPortClassificationUpdate
    ) -> UpdateOutputPortClassificationResponse:
        classification = ensure_output_port_classification_exists(id, self.db)
        classification.name = request.name
        classification.description = request.description
        if request.access_function != classification.access_function:
            self._ensure_not_last_invite_only(classification)
            OutputPortService(self.db).reclassify_output_ports(
                classification.id, request.access_function
            )
            classification.access_function = request.access_function
        self.db.flush()
        return UpdateOutputPortClassificationResponse(id=id)

    def delete_output_port_classification(self, id: UUID) -> None:
        classification = ensure_output_port_classification_exists(id, self.db)
        self._ensure_not_last_invite_only(classification)
        in_use = (
            OutputPortService(self.db)
            .count_by_classification(include_hidden=True)
            .get(id, 0)
        )
        if in_use:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete a classification used by {in_use} output ports",
            )
        self.db.delete(classification)
        self.db.flush()

    def _ensure_not_last_invite_only(
        self, classification: OutputPortClassificationModel
    ) -> None:
        if (
            classification.access_function == OutputPortAccessFunction.PRIVATE
            and self.db.scalar(
                select(func.count())
                .select_from(OutputPortClassificationModel)
                .where(
                    OutputPortClassificationModel.access_function
                    == OutputPortAccessFunction.PRIVATE
                )
            )
            == 1
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one classification must stay Invite only",
            )
