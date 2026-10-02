from typing import Any, TypeVar

from pydantic import ValidationError

from app.identities.model import Identity
from app.identities.schema_response import IdentityBatchCreateError
from app.shared.schema import ORMModel

CreateSchema = TypeVar("CreateSchema", bound=ORMModel)


def get_identity_display_name(identity: Identity) -> str:
    # Local imports to avoid circular dependencies
    from app.groups.model import Group
    from app.machine_users.model import MachineUser
    from app.users.model import User

    if isinstance(identity, User):
        return f"{identity.first_name} {identity.last_name}"

    if isinstance(identity, (Group, MachineUser)):
        return identity.display_name

    raise ValueError(f"Unsupported identity type: {identity.type}")

def validate_batch_create_items(
    items: list[Any],
    schema: type[CreateSchema],
) -> tuple[list[CreateSchema], list[IdentityBatchCreateError]]:
    validated_items: list[CreateSchema] = []
    errors: list[IdentityBatchCreateError] = []

    for item in items:
        try:
            validated_items.append(schema.model_validate(item))
        except ValidationError as exception:
            errors.append(
                IdentityBatchCreateError(
                    item=item,
                    errors=[error["msg"] for error in exception.errors()],
                )
            )

    return validated_items, errors