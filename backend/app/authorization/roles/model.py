import uuid

from sqlalchemy import Column, Integer, SmallInteger, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import mapped_column, validates

from app.authorization.roles.schema import Prototype, Scope
from app.core.authz.actions import AuthorizationAction
from app.database.database import Base
from app.shared.model import BaseORM


class Role(Base, BaseORM):
    __tablename__ = "roles"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)

    scope = mapped_column(
        SAEnum(
            Scope,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )
    prototype = Column(SmallInteger, default=Prototype.CUSTOM)
    description = Column(String)
    permissions = Column(ARRAY(Integer))

    @validates("permissions")
    def validate_permissions(self, key: str, permissions: list[int]) -> list[int]:
        """
        For a Data Product role we want to ensure that the HIDDEN_DATA_PRODUCT__READ permission is always included,
        even if not explicitly set.
        This permission is required to ensure people have access to hidden data products.
        """

        match self.scope:
            case Scope.DATA_PRODUCT:
                if (
                    int(AuthorizationAction.HIDDEN__DATA_PRODUCT__READ)
                    not in permissions
                ):
                    permissions = [
                        *permissions,
                        int(AuthorizationAction.HIDDEN__DATA_PRODUCT__READ),
                    ]
                if (
                    int(AuthorizationAction.HIDDEN__OUTPUT_PORT__READ)
                    not in permissions
                ):
                    permissions = [
                        *permissions,
                        int(AuthorizationAction.HIDDEN__OUTPUT_PORT__READ),
                    ]
            case Scope.DATASET:
                if (
                    int(AuthorizationAction.HIDDEN__OUTPUT_PORT__READ)
                    not in permissions
                ):
                    permissions = [
                        *permissions,
                        int(AuthorizationAction.HIDDEN__OUTPUT_PORT__READ),
                    ]
            case _:
                pass
        return sorted(set(permissions))
