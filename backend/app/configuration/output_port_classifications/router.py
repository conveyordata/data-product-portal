from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.output_port_classifications.schema_request import (
    OutputPortClassificationCreate,
    OutputPortClassificationUpdate,
)
from app.configuration.output_port_classifications.schema_response import (
    CreateOutputPortClassificationResponse,
    OutputPortClassificationsGet,
    UpdateOutputPortClassificationResponse,
)
from app.configuration.output_port_classifications.service import (
    OutputPortClassificationService,
)
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import get_db_session
from app.users.model import User

router = APIRouter(
    tags=["Configuration - Output Port classifications"],
    prefix="/v2/configuration/output_port_classifications",
)


@router.get("")
def get_output_port_classifications(
    db: Session = Depends(get_db_session, scope="function"),
    user: User = Depends(get_authenticated_user),
) -> OutputPortClassificationsGet:
    return OutputPortClassificationsGet(
        output_port_classifications=OutputPortClassificationService(
            db
        ).get_output_port_classifications(user)
    )


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def create_output_port_classification(
    output_port_classification: OutputPortClassificationCreate,
    db: Session = Depends(get_db_session, scope="function"),
) -> CreateOutputPortClassificationResponse:
    return OutputPortClassificationService(db).create_output_port_classification(
        output_port_classification
    )


@router.put(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_output_port_classification(
    id: UUID,
    output_port_classification: OutputPortClassificationUpdate,
    db: Session = Depends(get_db_session, scope="function"),
) -> UpdateOutputPortClassificationResponse:
    return OutputPortClassificationService(db).update_output_port_classification(
        id, output_port_classification
    )


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def remove_output_port_classification(
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    OutputPortClassificationService(db).delete_output_port_classification(id)
