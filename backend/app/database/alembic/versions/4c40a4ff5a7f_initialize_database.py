"""Initialize database

Revision ID: 4c40a4ff5a7f
Revises:
Create Date: 2024-04-17 17:15:55.096655

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from app.core.auth.device_flows.schema import DeviceFlowStatus
from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_product_types.enums import DataProductIconKey
from app.data_products.status import DataProductStatus
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "4c40a4ff5a7f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String, unique=True),
        sa.Column("id", UUID, primary_key=True),
        sa.Column("external_id", sa.String),
        sa.Column("first_name", sa.String),
        sa.Column("last_name", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "tags",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("value", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "environments",
        sa.Column("name", sa.String, primary_key=True),
        sa.Column("context", sa.String),
        sa.Column("is_default", sa.Boolean),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "domains",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("description", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "data_product_types",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("description", sa.String),
        sa.Column(
            "icon_key", sa.Enum(DataProductIconKey), default=DataProductIconKey.DEFAULT
        ),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "data_products",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("external_id", sa.String),
        sa.Column("description", sa.String),
        sa.Column("about", sa.String),
        sa.Column(
            "status", sa.Enum(DataProductStatus), default=DataProductStatus.PENDING
        ),
        sa.Column("type_id", UUID, sa.ForeignKey("data_product_types.id")),
        sa.Column("domain_id", UUID, sa.ForeignKey("domains.id")),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "permissionsets",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("data_product", UUID, sa.ForeignKey("data_products.id")),
        sa.Column("environment", sa.String, sa.ForeignKey("environments.name")),
        sa.Column("name", sa.String),
        sa.Column("rolearn", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "datasets",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("external_id", sa.String),
        sa.Column("name", sa.String),
        sa.Column("description", sa.String),
        sa.Column("about", sa.String),
        sa.Column("status", sa.Enum(DatasetStatus), default=DatasetStatus.PENDING),
        sa.Column(
            "access_type", sa.Enum(DatasetAccessType), default=DatasetAccessType.PUBLIC
        ),
        sa.Column("domain_id", UUID, sa.ForeignKey("domains.id")),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "datasets_owners",
        sa.Column("dataset_id", UUID, sa.ForeignKey("datasets.id")),
        sa.Column("users_id", UUID, sa.ForeignKey("users.id")),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )
    op.create_table(
        "tags_data_products",
        sa.Column("data_product_id", UUID, sa.ForeignKey("data_products.id")),
        sa.Column("tag_id", UUID, sa.ForeignKey("tags.id")),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )
    op.create_primary_key(
        "pk_tags_data_products", "tags_data_products", ["tag_id", "data_product_id"]
    )
    op.create_table(
        "tags_datasets",
        sa.Column("dataset_id", UUID, sa.ForeignKey("datasets.id")),
        sa.Column("tag_id", UUID, sa.ForeignKey("tags.id")),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )
    op.create_primary_key("pk_tags_datasets", "tags_datasets", ["tag_id", "dataset_id"])
    op.create_table(
        "data_product_memberships",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "data_product_id", UUID(as_uuid=True), sa.ForeignKey("data_products.id")
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column(
            "role", sa.Enum(DataProductUserRole), default=DataProductUserRole.MEMBER
        ),
        sa.Column(
            "status",
            sa.Enum(DataProductMembershipStatus),
            default=DataProductMembershipStatus.PENDING_APPROVAL,
        ),
        sa.Column("requested_by_id", UUID, sa.ForeignKey("users.id")),
        sa.Column("requested_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("approved_by_id", UUID, sa.ForeignKey("users.id")),
        sa.Column("approved_on", sa.DateTime(timezone=False)),
        sa.Column("denied_by_id", UUID, sa.ForeignKey("users.id")),
        sa.Column("denied_on", sa.DateTime(timezone=False)),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "data_products_datasets",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "data_product_id", UUID(as_uuid=True), sa.ForeignKey("data_products.id")
        ),
        sa.Column("dataset_id", UUID(as_uuid=True), sa.ForeignKey("datasets.id")),
        sa.Column(
            "status",
            sa.Enum(DataProductDatasetLinkStatus),
            default=DataProductDatasetLinkStatus.PENDING_APPROVAL,
        ),
        sa.Column("requested_by_id", UUID),
        sa.Column("requested_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("approved_by_id", UUID),
        sa.Column("approved_on", sa.DateTime(timezone=False)),
        sa.Column("denied_by_id", UUID),
        sa.Column("denied_on", sa.DateTime(timezone=False)),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "device_flows",
        sa.Column("device_code", UUID, primary_key=True),
        sa.Column("user_code", sa.String),
        sa.Column("scope", sa.String),
        sa.Column("interval", sa.Integer),
        sa.Column("expiration", sa.Integer),
        sa.Column("status", sa.Enum(DeviceFlowStatus)),
        sa.Column("client_id", sa.String),
        sa.Column("max_expiry", sa.DateTime(timezone=False)),
        sa.Column("last_checked", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("oidc_redirect_uri", sa.String),
        sa.Column("authz_code", sa.String),
        sa.Column("authz_verif", sa.String),
        sa.Column("authz_state", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("device_flows")
    op.drop_table("data_products_datasets")
    op.drop_table("datasets_owners")
    op.drop_table("tags_data_products")
    op.drop_table("tags_datasets")
    op.drop_table("users")
    op.drop_table("tags")
    op.drop_table("environments")
    op.drop_table("data_products")
    op.drop_table("data_product_types")
    op.drop_table("permissionsets")
    op.drop_table("datasets")
    op.drop_table("data_product_memberships")
    op.drop_table("domains")
