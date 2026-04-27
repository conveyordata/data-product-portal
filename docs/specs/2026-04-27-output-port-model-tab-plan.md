# Output Port Model Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only "Model" tab to the output port detail page that displays table schemas (tables + columns) and semantic models, populated via API endpoints.

**Architecture:** Two new sub-feature modules under `backend/app/data_products/output_ports/` (table_schemas and semantic_models), each following the freshness module pattern: model → service → router → tests. The frontend adds a `ModelTab` component to the existing dataset tabs, lazy-loading from the two new GET endpoints via auto-generated RTK Query hooks.

**Tech Stack:** Python/FastAPI/SQLAlchemy (backend), Alembic (migrations), pytest + factory_boy (tests), React/TypeScript/Ant Design/RTK Query (frontend), i18next (localization).

**Spec:** `docs/specs/2026-04-27-output-port-model-tab-design.md`

---

## File Map

**New backend files:**
- `backend/app/data_products/output_ports/table_schemas/model.py`
- `backend/app/data_products/output_ports/table_schemas/schema_request.py`
- `backend/app/data_products/output_ports/table_schemas/schema_response.py`
- `backend/app/data_products/output_ports/table_schemas/service.py`
- `backend/app/data_products/output_ports/table_schemas/router.py`
- `backend/app/data_products/output_ports/semantic_models/model.py`
- `backend/app/data_products/output_ports/semantic_models/schema_request.py`
- `backend/app/data_products/output_ports/semantic_models/schema_response.py`
- `backend/app/data_products/output_ports/semantic_models/service.py`
- `backend/app/data_products/output_ports/semantic_models/router.py`
- `backend/app/database/alembic/versions/<timestamp>-<id>_add_output_port_model_metadata.py`

**Modified backend files:**
- `backend/app/data_products/output_ports/router.py` — include two new sub-routers

**New test files:**
- `backend/tests/factories/output_port_table_schema.py`
- `backend/tests/factories/output_port_column.py`
- `backend/tests/factories/output_port_semantic_model.py`
- `backend/tests/app/data_products/output_ports/table_schemas/__init__.py`
- `backend/tests/app/data_products/output_ports/table_schemas/test_router.py`
- `backend/tests/app/data_products/output_ports/semantic_models/__init__.py`
- `backend/tests/app/data_products/output_ports/semantic_models/test_router.py`

**Modified test files:**
- `backend/tests/factories/__init__.py` — register three new factories

**New frontend files:**
- `frontend/src/pages/dataset/components/dataset-tabs/model-tab/model-tab.tsx`
- `frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/table-schema-list.tsx`
- `frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/column-table.tsx`
- `frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/semantic-model-list.tsx`
- `frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/semantic-model-card.tsx`

**Modified frontend files:**
- `frontend/src/pages/dataset/components/dataset-tabs/dataset-tabkeys.ts` — add `Model`
- `frontend/src/pages/dataset/components/dataset-tabs/dataset-tabs.tsx` — register tab
- `frontend/src/store/api/services/generated/` — auto-generated (do not edit manually)

---

## Task 1: Table Schema and Column ORM Models

**Files:**
- Create: `backend/app/data_products/output_ports/table_schemas/model.py`

- [ ] **Step 1: Write the model file**

```python
# backend/app/data_products/output_ports/table_schemas/model.py
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.configuration.tags.model import Tag
from app.database.database import Base
from app.shared.model import utcnow

tag_output_port_table_schema_table = Table(
    "tags_output_port_table_schemas",
    Base.metadata,
    Column("table_schema_id", ForeignKey("output_port_table_schemas.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)

tag_output_port_column_table = Table(
    "tags_output_port_columns",
    Base.metadata,
    Column("column_id", ForeignKey("output_port_columns.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)


class OutputPortTableSchema(Base):
    __tablename__ = "output_port_table_schemas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_output_port_table_schema_table, lazy="joined"
    )
    columns: Mapped[list["OutputPortColumn"]] = relationship(
        back_populates="table_schema",
        cascade="all, delete-orphan",
        lazy="joined",
        order_by="OutputPortColumn.name",
    )


class OutputPortColumn(Base):
    __tablename__ = "output_port_columns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    table_schema_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("output_port_table_schemas.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    data_type: Mapped[str | None] = mapped_column(String, nullable=True)

    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_output_port_column_table, lazy="joined"
    )
    table_schema: Mapped["OutputPortTableSchema"] = relationship(
        back_populates="columns", lazy="raise"
    )
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/data_products/output_ports/table_schemas/model.py
git commit -m "feat: add OutputPortTableSchema and OutputPortColumn ORM models"
```

---

## Task 2: Semantic Model ORM Model

**Files:**
- Create: `backend/app/data_products/output_ports/semantic_models/model.py`

- [ ] **Step 1: Write the model file**

```python
# backend/app/data_products/output_ports/semantic_models/model.py
import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class SemanticModelFormat(str, enum.Enum):
    MetricsFlow = "MetricsFlow"
    OpenSemanticInterchange = "OpenSemanticInterchange"


class OutputPortSemanticModel(Base):
    __tablename__ = "output_port_semantic_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # ForeignKey imported inline to avoid circular imports at module load
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[SemanticModelFormat] = mapped_column(
        SAEnum(SemanticModelFormat), nullable=False
    )
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
```

> **Note:** The ForeignKey for `output_port_id` must reference `datasets.id`. Add the import and FK properly:

```python
from sqlalchemy import ForeignKey

    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
```

Full corrected model file:

```python
# backend/app/data_products/output_ports/semantic_models/model.py
import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class SemanticModelFormat(str, enum.Enum):
    MetricsFlow = "MetricsFlow"
    OpenSemanticInterchange = "OpenSemanticInterchange"


class OutputPortSemanticModel(Base):
    __tablename__ = "output_port_semantic_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[SemanticModelFormat] = mapped_column(
        SAEnum(SemanticModelFormat), nullable=False
    )
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/data_products/output_ports/semantic_models/model.py
git commit -m "feat: add OutputPortSemanticModel ORM model"
```

---

## Task 3: Database Migration

**Files:**
- Create: `backend/app/database/alembic/versions/<timestamp>-<id>_add_output_port_model_metadata.py`

- [ ] **Step 1: Generate the migration skeleton**

Run from `backend/`:
```bash
cd backend && poetry run alembic revision --autogenerate -m "add_output_port_model_metadata"
```

This creates a file like `backend/app/database/alembic/versions/2026_04_27_HHMM-<hexid>_add_output_port_model_metadata.py` with `down_revision = "a2b3c4d5e6f7"`.

- [ ] **Step 2: Replace upgrade() and downgrade() with the correct content**

Open the generated file and replace the `upgrade()` and `downgrade()` functions with:

```python
from app.shared.model import utcnow  # add to imports at top


def upgrade() -> None:
    op.create_table(
        "output_port_table_schemas",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column(
            "output_port_id",
            sa.UUID,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
    )
    op.create_index(
        op.f("ix_output_port_table_schemas_output_port_id"),
        "output_port_table_schemas",
        ["output_port_id"],
        unique=False,
    )

    op.create_table(
        "output_port_columns",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column(
            "table_schema_id",
            sa.UUID,
            sa.ForeignKey("output_port_table_schemas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("data_type", sa.String, nullable=True),
    )

    op.create_table(
        "tags_output_port_table_schemas",
        sa.Column(
            "table_schema_id",
            sa.UUID,
            sa.ForeignKey("output_port_table_schemas.id"),
            nullable=False,
        ),
        sa.Column("tag_id", sa.UUID, sa.ForeignKey("tags.id"), nullable=False),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=False),
            server_default=utcnow(),
        ),
        sa.Column(
            "updated_on",
            sa.DateTime(timezone=False),
            onupdate=utcnow(),
        ),
    )

    op.create_table(
        "tags_output_port_columns",
        sa.Column(
            "column_id",
            sa.UUID,
            sa.ForeignKey("output_port_columns.id"),
            nullable=False,
        ),
        sa.Column("tag_id", sa.UUID, sa.ForeignKey("tags.id"), nullable=False),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=False),
            server_default=utcnow(),
        ),
        sa.Column(
            "updated_on",
            sa.DateTime(timezone=False),
            onupdate=utcnow(),
        ),
    )

    op.create_table(
        "output_port_semantic_models",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column(
            "output_port_id",
            sa.UUID,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column(
            "format",
            sa.Enum("MetricsFlow", "OpenSemanticInterchange", name="semanticmodelformat"),
            nullable=False,
        ),
        sa.Column("content", sa.dialects.postgresql.JSONB(), nullable=False),
    )
    op.create_index(
        op.f("ix_output_port_semantic_models_output_port_id"),
        "output_port_semantic_models",
        ["output_port_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_output_port_semantic_models_output_port_id"),
        table_name="output_port_semantic_models",
    )
    op.drop_table("output_port_semantic_models")
    op.drop_table("tags_output_port_columns")
    op.drop_table("tags_output_port_table_schemas")
    op.drop_table("output_port_columns")
    op.drop_index(
        op.f("ix_output_port_table_schemas_output_port_id"),
        table_name="output_port_table_schemas",
    )
    op.drop_table("output_port_table_schemas")
```

Also add `from sqlalchemy.dialects import postgresql as sa_pg` to the imports if `sa.dialects.postgresql.JSONB` is not resolved — or use `sa_pg.JSONB()` after importing it.

- [ ] **Step 3: Apply the migration**

```bash
cd backend && poetry run alembic upgrade head
```

Expected: `Running upgrade a2b3c4d5e6f7 -> <new-id>, add_output_port_model_metadata`

- [ ] **Step 4: Commit**

```bash
git add backend/app/database/alembic/versions/
git commit -m "feat: add migration for output port model metadata tables"
```

---

## Task 4: Table Schema Request + Response Schemas

**Files:**
- Create: `backend/app/data_products/output_ports/table_schemas/schema_request.py`
- Create: `backend/app/data_products/output_ports/table_schemas/schema_response.py`

- [ ] **Step 1: Write the request schema**

```python
# backend/app/data_products/output_ports/table_schemas/schema_request.py
from uuid import UUID

from app.shared.schema import ORMModel


class ColumnRequest(ORMModel):
    name: str
    description: str | None = None
    data_type: str | None = None
    tag_ids: list[UUID] = []


class TableSchemaRequest(ORMModel):
    name: str
    description: str | None = None
    tag_ids: list[UUID] = []
    columns: list[ColumnRequest] = []
```

- [ ] **Step 2: Write the response schema**

```python
# backend/app/data_products/output_ports/table_schemas/schema_response.py
from uuid import UUID

from app.configuration.tags.schema import Tag
from app.shared.schema import ORMModel


class ColumnResponse(ORMModel):
    id: UUID
    name: str
    description: str | None = None
    data_type: str | None = None
    tags: list[Tag]


class TableSchemaResponse(ORMModel):
    id: UUID
    output_port_id: UUID
    name: str
    description: str | None = None
    tags: list[Tag]
    columns: list[ColumnResponse]
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/data_products/output_ports/table_schemas/schema_request.py \
        backend/app/data_products/output_ports/table_schemas/schema_response.py
git commit -m "feat: add table schema request/response schemas"
```

---

## Task 5: Table Schema Service

**Files:**
- Create: `backend/app/data_products/output_ports/table_schemas/service.py`

- [ ] **Step 1: Write the service**

```python
# backend/app/data_products/output_ports/table_schemas/service.py
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

    def list(self, output_port_id: UUID) -> list[OutputPortTableSchema]:
        return (
            self.db.query(OutputPortTableSchema)
            .filter(OutputPortTableSchema.output_port_id == output_port_id)
            .order_by(OutputPortTableSchema.name)
            .all()
        )

    def create(self, output_port_id: UUID, request: TableSchemaRequest) -> OutputPortTableSchema:
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

    def replace(self, schema_id: UUID, request: TableSchemaRequest) -> OutputPortTableSchema:
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/data_products/output_ports/table_schemas/service.py
git commit -m "feat: add TableSchemaService"
```

---

## Task 6: Table Schema Router

**Files:**
- Create: `backend/app/data_products/output_ports/table_schemas/router.py`

- [ ] **Step 1: Write the router**

```python
# backend/app/data_products/output_ports/table_schemas/router.py
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.table_schemas.schema_request import TableSchemaRequest
from app.data_products.output_ports.table_schemas.schema_response import TableSchemaResponse
from app.data_products.output_ports.table_schemas.service import TableSchemaService
from app.database.database import get_db_session

router = APIRouter(tags=["Data Products - Output Ports - Table Schemas"])
base_route = "/v2/data_products/{data_product_id}/output_ports/{id}"


@router.get(f"{base_route}/table-schemas")
def get_output_port_table_schemas(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
) -> list[TableSchemaResponse]:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return TableSchemaService(db).list(id)


@router.post(
    f"{base_route}/table-schemas",
    dependencies=[
        Depends(Authorization.enforce(Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver))
    ],
)
def create_output_port_table_schema(
    data_product_id: UUID,
    id: UUID,
    request: TableSchemaRequest,
    db: Session = Depends(get_db_session),
) -> TableSchemaResponse:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return TableSchemaService(db).create(id, request)


@router.put(
    f"{base_route}/table-schemas/{{schema_id}}",
    dependencies=[
        Depends(Authorization.enforce(Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver))
    ],
)
def replace_output_port_table_schema(
    data_product_id: UUID,
    id: UUID,
    schema_id: UUID,
    request: TableSchemaRequest,
    db: Session = Depends(get_db_session),
) -> TableSchemaResponse:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return TableSchemaService(db).replace(schema_id, request)


@router.delete(
    f"{base_route}/table-schemas/{{schema_id}}",
    status_code=204,
    dependencies=[
        Depends(Authorization.enforce(Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver))
    ],
)
def delete_output_port_table_schema(
    data_product_id: UUID,
    id: UUID,
    schema_id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    TableSchemaService(db).delete(schema_id)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/data_products/output_ports/table_schemas/router.py
git commit -m "feat: add table schema CRUD router"
```

---

## Task 7: Table Schema Tests

**Files:**
- Create: `backend/tests/factories/output_port_table_schema.py`
- Create: `backend/tests/factories/output_port_column.py`
- Modify: `backend/tests/factories/__init__.py`
- Create: `backend/tests/app/data_products/output_ports/table_schemas/__init__.py`
- Create: `backend/tests/app/data_products/output_ports/table_schemas/test_router.py`

- [ ] **Step 1: Write the factories**

```python
# backend/tests/factories/output_port_table_schema.py
import factory

from app.data_products.output_ports.table_schemas.model import OutputPortTableSchema
from .dataset import DatasetFactory


class OutputPortTableSchemaFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortTableSchema

    id = factory.Faker("uuid4")
    output_port_id = factory.LazyAttribute(lambda o: DatasetFactory().id)
    name = factory.Faker("word")
    description = factory.Faker("sentence")
```

```python
# backend/tests/factories/output_port_column.py
import factory

from app.data_products.output_ports.table_schemas.model import OutputPortColumn
from .output_port_table_schema import OutputPortTableSchemaFactory


class OutputPortColumnFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortColumn

    id = factory.Faker("uuid4")
    table_schema_id = factory.LazyAttribute(lambda o: OutputPortTableSchemaFactory().id)
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    data_type = "varchar"
```

- [ ] **Step 2: Register factories in `backend/tests/factories/__init__.py`**

Add these imports and entries to the existing file (after the existing imports, before the `factories` list):

```python
from .output_port_table_schema import OutputPortTableSchemaFactory
from .output_port_column import OutputPortColumnFactory
```

Add to the `factories` list:
```python
    OutputPortTableSchemaFactory,
    OutputPortColumnFactory,
```

- [ ] **Step 3: Create the test `__init__.py`**

```bash
mkdir -p backend/tests/app/data_products/output_ports/table_schemas
touch backend/tests/app/data_products/output_ports/table_schemas/__init__.py
```

- [ ] **Step 4: Write failing tests**

```python
# backend/tests/app/data_products/output_ports/table_schemas/test_router.py
from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    OutputPortTableSchemaFactory,
    RoleFactory,
    TagFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/data_products"


def _assign_update_properties_role(session, dataset):
    RoleService(db=session).initialize_prototype_roles()
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
    )
    DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=dataset.id)
    return user


class TestTableSchemaRouter:
    def test_get_table_schemas_empty(self, client, session):
        dataset = DatasetFactory()
        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas"
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_table_schemas_returns_existing(self, client, session):
        dataset = DatasetFactory()
        OutputPortTableSchemaFactory(output_port_id=dataset.id, name="orders")
        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas"
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["name"] == "orders"
        assert body[0]["columns"] == []
        assert body[0]["tags"] == []

    def test_post_creates_table_schema_with_columns(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        tag = TagFactory()

        payload = {
            "name": "orders",
            "description": "Order transactions",
            "tag_ids": [str(tag.id)],
            "columns": [
                {"name": "id", "data_type": "int", "description": "PK", "tag_ids": []},
                {"name": "amount", "data_type": "decimal", "description": "Total", "tag_ids": []},
            ],
        }
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas",
            json=payload,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "orders"
        assert len(body["columns"]) == 2
        assert body["columns"][0]["name"] == "amount"  # sorted alphabetically
        assert len(body["tags"]) == 1
        assert body["tags"][0]["id"] == str(tag.id)

    def test_post_requires_permissions(self, client, session):
        dataset = DatasetFactory()
        RoleService(db=session).initialize_prototype_roles()
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas",
            json={"name": "orders", "tag_ids": [], "columns": []},
        )
        assert response.status_code == 403

    def test_put_replaces_table_schema(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        schema = OutputPortTableSchemaFactory(output_port_id=dataset.id, name="old_name")

        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas/{schema.id}",
            json={"name": "new_name", "tag_ids": [], "columns": []},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "new_name"

    def test_put_not_found(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        import uuid
        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas/{uuid.uuid4()}",
            json={"name": "x", "tag_ids": [], "columns": []},
        )
        assert response.status_code == 404

    def test_delete_removes_table_schema(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        schema = OutputPortTableSchemaFactory(output_port_id=dataset.id)

        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas/{schema.id}"
        )
        assert response.status_code == 204

    def test_delete_not_found(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        import uuid
        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas/{uuid.uuid4()}"
        )
        assert response.status_code == 404
```

- [ ] **Step 5: Run tests — expect failure because router is not wired yet**

```bash
cd backend && poetry run pytest tests/app/data_products/output_ports/table_schemas/ -v
```

Expected: `FAILED` — `404` responses because endpoints don't exist yet. (Wiring happens in Task 9.)

- [ ] **Step 6: Commit**

```bash
git add backend/tests/factories/output_port_table_schema.py \
        backend/tests/factories/output_port_column.py \
        backend/tests/factories/__init__.py \
        backend/tests/app/data_products/output_ports/table_schemas/
git commit -m "test: add table schema factories and router tests"
```

---

## Task 8: Semantic Model Schemas + Service + Router

**Files:**
- Create: `backend/app/data_products/output_ports/semantic_models/schema_request.py`
- Create: `backend/app/data_products/output_ports/semantic_models/schema_response.py`
- Create: `backend/app/data_products/output_ports/semantic_models/service.py`
- Create: `backend/app/data_products/output_ports/semantic_models/router.py`

- [ ] **Step 1: Write request and response schemas**

```python
# backend/app/data_products/output_ports/semantic_models/schema_request.py
from app.data_products.output_ports.semantic_models.model import SemanticModelFormat
from app.shared.schema import ORMModel


class SemanticModelRequest(ORMModel):
    name: str
    format: SemanticModelFormat
    content: dict
```

```python
# backend/app/data_products/output_ports/semantic_models/schema_response.py
from uuid import UUID

from app.data_products.output_ports.semantic_models.model import SemanticModelFormat
from app.shared.schema import ORMModel


class SemanticModelResponse(ORMModel):
    id: UUID
    output_port_id: UUID
    name: str
    format: SemanticModelFormat
    content: dict
```

- [ ] **Step 2: Write the service**

```python
# backend/app/data_products/output_ports/semantic_models/service.py
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.data_products.output_ports.semantic_models.model import OutputPortSemanticModel
from app.data_products.output_ports.semantic_models.schema_request import SemanticModelRequest


class SemanticModelService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, output_port_id: UUID) -> list[OutputPortSemanticModel]:
        return (
            self.db.query(OutputPortSemanticModel)
            .filter(OutputPortSemanticModel.output_port_id == output_port_id)
            .order_by(OutputPortSemanticModel.name)
            .all()
        )

    def create(self, output_port_id: UUID, request: SemanticModelRequest) -> OutputPortSemanticModel:
        model = OutputPortSemanticModel(
            output_port_id=output_port_id,
            name=request.name,
            format=request.format,
            content=request.content,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def replace(self, model_id: UUID, request: SemanticModelRequest) -> OutputPortSemanticModel:
        model = self._get_or_404(model_id)
        model.name = request.name
        model.format = request.format
        model.content = request.content
        self.db.commit()
        self.db.refresh(model)
        return model

    def delete(self, model_id: UUID) -> None:
        model = self._get_or_404(model_id)
        self.db.delete(model)
        self.db.commit()

    def _get_or_404(self, model_id: UUID) -> OutputPortSemanticModel:
        model = self.db.get(OutputPortSemanticModel, model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Semantic model {model_id} not found",
            )
        return model
```

- [ ] **Step 3: Write the router**

```python
# backend/app/data_products/output_ports/semantic_models/router.py
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.semantic_models.schema_request import SemanticModelRequest
from app.data_products.output_ports.semantic_models.schema_response import SemanticModelResponse
from app.data_products.output_ports.semantic_models.service import SemanticModelService
from app.database.database import get_db_session

router = APIRouter(tags=["Data Products - Output Ports - Semantic Models"])
base_route = "/v2/data_products/{data_product_id}/output_ports/{id}"


@router.get(f"{base_route}/semantic-models")
def get_output_port_semantic_models(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
) -> list[SemanticModelResponse]:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return SemanticModelService(db).list(id)


@router.post(
    f"{base_route}/semantic-models",
    dependencies=[
        Depends(Authorization.enforce(Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver))
    ],
)
def create_output_port_semantic_model(
    data_product_id: UUID,
    id: UUID,
    request: SemanticModelRequest,
    db: Session = Depends(get_db_session),
) -> SemanticModelResponse:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return SemanticModelService(db).create(id, request)


@router.put(
    f"{base_route}/semantic-models/{{model_id}}",
    dependencies=[
        Depends(Authorization.enforce(Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver))
    ],
)
def replace_output_port_semantic_model(
    data_product_id: UUID,
    id: UUID,
    model_id: UUID,
    request: SemanticModelRequest,
    db: Session = Depends(get_db_session),
) -> SemanticModelResponse:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return SemanticModelService(db).replace(model_id, request)


@router.delete(
    f"{base_route}/semantic-models/{{model_id}}",
    status_code=204,
    dependencies=[
        Depends(Authorization.enforce(Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver))
    ],
)
def delete_output_port_semantic_model(
    data_product_id: UUID,
    id: UUID,
    model_id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    SemanticModelService(db).delete(model_id)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/data_products/output_ports/semantic_models/
git commit -m "feat: add semantic model schemas, service, and router"
```

---

## Task 9: Semantic Model Tests

**Files:**
- Create: `backend/tests/factories/output_port_semantic_model.py`
- Modify: `backend/tests/factories/__init__.py`
- Create: `backend/tests/app/data_products/output_ports/semantic_models/__init__.py`
- Create: `backend/tests/app/data_products/output_ports/semantic_models/test_router.py`

- [ ] **Step 1: Write the factory**

```python
# backend/tests/factories/output_port_semantic_model.py
import factory

from app.data_products.output_ports.semantic_models.model import (
    OutputPortSemanticModel,
    SemanticModelFormat,
)
from .dataset import DatasetFactory


class OutputPortSemanticModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortSemanticModel

    id = factory.Faker("uuid4")
    output_port_id = factory.LazyAttribute(lambda o: DatasetFactory().id)
    name = factory.Faker("word")
    format = SemanticModelFormat.MetricsFlow
    content = factory.LazyFunction(lambda: {"version": 2, "models": []})
```

- [ ] **Step 2: Register in `backend/tests/factories/__init__.py`**

Add import:
```python
from .output_port_semantic_model import OutputPortSemanticModelFactory
```

Add to `factories` list:
```python
    OutputPortSemanticModelFactory,
```

- [ ] **Step 3: Create the test `__init__.py`**

```bash
mkdir -p backend/tests/app/data_products/output_ports/semantic_models
touch backend/tests/app/data_products/output_ports/semantic_models/__init__.py
```

- [ ] **Step 4: Write the tests**

```python
# backend/tests/app/data_products/output_ports/semantic_models/test_router.py
import uuid

from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    OutputPortSemanticModelFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/data_products"


def _assign_update_properties_role(session, dataset):
    RoleService(db=session).initialize_prototype_roles()
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
    )
    DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=dataset.id)
    return user


class TestSemanticModelRouter:
    def test_get_semantic_models_empty(self, client, session):
        dataset = DatasetFactory()
        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models"
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_semantic_models_returns_existing(self, client, session):
        dataset = DatasetFactory()
        OutputPortSemanticModelFactory(output_port_id=dataset.id, name="revenue_model")
        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models"
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["name"] == "revenue_model"
        assert body[0]["format"] == "MetricsFlow"

    def test_post_creates_semantic_model(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)

        payload = {
            "name": "revenue_model",
            "format": "MetricsFlow",
            "content": {"version": 2, "models": [{"name": "revenue"}]},
        }
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models",
            json=payload,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "revenue_model"
        assert body["format"] == "MetricsFlow"
        assert body["content"]["version"] == 2

    def test_post_requires_permissions(self, client, session):
        dataset = DatasetFactory()
        RoleService(db=session).initialize_prototype_roles()
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models",
            json={"name": "x", "format": "MetricsFlow", "content": {}},
        )
        assert response.status_code == 403

    def test_put_replaces_semantic_model(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        model = OutputPortSemanticModelFactory(output_port_id=dataset.id, name="old_name")

        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models/{model.id}",
            json={"name": "new_name", "format": "OpenSemanticInterchange", "content": {"entities": []}},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "new_name"
        assert body["format"] == "OpenSemanticInterchange"

    def test_put_not_found(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models/{uuid.uuid4()}",
            json={"name": "x", "format": "MetricsFlow", "content": {}},
        )
        assert response.status_code == 404

    def test_delete_removes_semantic_model(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        model = OutputPortSemanticModelFactory(output_port_id=dataset.id)

        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models/{model.id}"
        )
        assert response.status_code == 204

    def test_delete_not_found(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models/{uuid.uuid4()}"
        )
        assert response.status_code == 404
```

- [ ] **Step 5: Run tests — expect failure because router is not wired yet**

```bash
cd backend && poetry run pytest tests/app/data_products/output_ports/semantic_models/ -v
```

Expected: `FAILED` — `404` because endpoints don't exist yet.

- [ ] **Step 6: Commit**

```bash
git add backend/tests/factories/output_port_semantic_model.py \
        backend/tests/factories/__init__.py \
        backend/tests/app/data_products/output_ports/semantic_models/
git commit -m "test: add semantic model factory and router tests"
```

---

## Task 10: Wire Sub-Routers and Verify Backend

**Files:**
- Modify: `backend/app/data_products/output_ports/router.py`

- [ ] **Step 1: Add the two sub-router imports and `include_router` calls**

In `backend/app/data_products/output_ports/router.py`, add after the existing sub-router imports (around line 32):

```python
from app.data_products.output_ports.table_schemas.router import (
    router as table_schemas_router,
)
from app.data_products.output_ports.semantic_models.router import (
    router as semantic_models_router,
)
```

Add after the existing `router.include_router(freshness_router)` line (around line 105):

```python
router.include_router(table_schemas_router)
router.include_router(semantic_models_router)
```

- [ ] **Step 2: Run all table schema tests — expect PASS**

```bash
cd backend && poetry run pytest tests/app/data_products/output_ports/table_schemas/ -v
```

Expected: All tests `PASSED`.

- [ ] **Step 3: Run all semantic model tests — expect PASS**

```bash
cd backend && poetry run pytest tests/app/data_products/output_ports/semantic_models/ -v
```

Expected: All tests `PASSED`.

- [ ] **Step 4: Run the full backend test suite**

```bash
cd backend && poetry run pytest -v
```

Expected: All tests `PASSED` (no regressions).

- [ ] **Step 5: Run linting and type checks**

```bash
cd backend && poetry run ruff check . && poetry run ruff format --check . && poetry run mypy app/
```

Fix any issues before committing.

- [ ] **Step 6: Commit**

```bash
git add backend/app/data_products/output_ports/router.py
git commit -m "feat: wire table schema and semantic model routers into output ports"
```

---

## Task 11: Regenerate OpenAPI Spec and Frontend API Client

- [ ] **Step 1: Regenerate the OpenAPI spec**

```bash
cd backend && poetry run python -m app.openapi_export
```

Or check the pre-commit hook command — look for the `Regen openapi spec` hook in `.pre-commit-config.yaml` to find the exact command.

Expected: Updated `openapi.json` or similar spec file.

- [ ] **Step 2: Generate the frontend RTK Query API client**

```bash
cd frontend && npm run generate-api
```

Expected: Two new generated files appear:
- `frontend/src/store/api/services/generated/dataProductsOutputPortsTableSchemasApi.ts`
- `frontend/src/store/api/services/generated/dataProductsOutputPortsSemanticModelsApi.ts`

Open `dataProductsOutputPortsTableSchemasApi.ts` and note the exported hook names. They will follow the pattern `use<FunctionName>Query` / `use<FunctionName>Mutation` based on the router function names. Expected hooks:
- `useGetOutputPortTableSchemasQuery`
- `useCreateOutputPortTableSchemaMutation`
- `useReplaceOutputPortTableSchemaMutation`
- `useDeleteOutputPortTableSchemaMutation`

And in `dataProductsOutputPortsSemanticModelsApi.ts`:
- `useGetOutputPortSemanticModelsQuery`
- `useCreateOutputPortSemanticModelMutation`
- `useReplaceOutputPortSemanticModelMutation`
- `useDeleteOutputPortSemanticModelMutation`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/store/api/services/generated/ backend/  # include updated spec
git commit -m "feat: regenerate OpenAPI spec and frontend API client for model metadata endpoints"
```

---

## Task 12: Frontend — Add Model Tab Key and Shell

**Files:**
- Modify: `frontend/src/pages/dataset/components/dataset-tabs/dataset-tabkeys.ts`
- Modify: `frontend/src/pages/dataset/components/dataset-tabs/dataset-tabs.tsx`
- Create: `frontend/src/pages/dataset/components/dataset-tabs/model-tab/model-tab.tsx`

- [ ] **Step 1: Add the tab key**

In `frontend/src/pages/dataset/components/dataset-tabs/dataset-tabkeys.ts`, add `Model` after `About`:

```typescript
export enum TabKeys {
    About = 'about',
    Model = 'model',
    Usage = 'usage',
    Consumers = 'consumers',
    Producers = 'producers',
    Team = 'team',
    Explorer = 'explorer',
    Settings = 'settings',
    History = 'history',
}
```

- [ ] **Step 2: Create the Model tab shell**

```typescript
// frontend/src/pages/dataset/components/dataset-tabs/model-tab/model-tab.tsx
import { Divider, Empty, Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { useGetOutputPortTableSchemasQuery } from '@/store/api/services/generated/dataProductsOutputPortsTableSchemasApi.ts';
import { useGetOutputPortSemanticModelsQuery } from '@/store/api/services/generated/dataProductsOutputPortsSemanticModelsApi.ts';
import { TableSchemaList } from './components/table-schema-list';
import { SemanticModelList } from './components/semantic-model-list';

// NOTE: Check the actual generated file for the exact hook names.
// If hooks are named differently, update the imports above to match.

type Props = {
    datasetId: string;
    dataProductId: string;
};

export function ModelTab({ datasetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const {
        data: tableSchemas = [],
        isFetching: isFetchingSchemas,
    } = useGetOutputPortTableSchemasQuery({ id: datasetId, dataProductId });

    const {
        data: semanticModels = [],
        isFetching: isFetchingModels,
    } = useGetOutputPortSemanticModelsQuery({ id: datasetId, dataProductId });

    if (isFetchingSchemas || isFetchingModels) {
        return <LoadingSpinner />;
    }

    return (
        <Flex vertical gap="large">
            <div>
                <Typography.Title level={5}>{t('Tables')}</Typography.Title>
                {tableSchemas.length === 0 ? (
                    <Empty description={t('No table schemas imported yet')} />
                ) : (
                    <TableSchemaList schemas={tableSchemas} />
                )}
            </div>
            <Divider />
            <div>
                <Typography.Title level={5}>{t('Semantic Models')}</Typography.Title>
                {semanticModels.length === 0 ? (
                    <Empty description={t('No semantic models imported yet')} />
                ) : (
                    <SemanticModelList models={semanticModels} />
                )}
            </div>
        </Flex>
    );
}
```

> **Note on generated hook args:** After running `npm run generate-api`, open the generated files and check what argument shape the GET hooks expect. The query arg type will list the required fields (typically `{ id: string; dataProductId: string }`). Adjust the hook call if the generated arg names differ.

- [ ] **Step 3: Register the tab in `dataset-tabs.tsx`**

In `frontend/src/pages/dataset/components/dataset-tabs/dataset-tabs.tsx`:

Add import at the top:
```typescript
import { ModelTab } from './model-tab/model-tab.tsx';
```

Add import for the icon (use `TableOutlined` from `@ant-design/icons`):
```typescript
import { ..., TableOutlined } from '@ant-design/icons';
```

Add the new tab entry to the `tabs` array, after the About tab:
```typescript
{
    label: t('Model'),
    key: TabKeys.Model,
    icon: <TableOutlined />,
    children: <ModelTab datasetId={datasetId} dataProductId={dataProductId} />,
},
```

- [ ] **Step 4: Run the frontend type checker**

```bash
cd frontend && npm run check
```

Fix any type errors before continuing.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/dataset/components/dataset-tabs/dataset-tabkeys.ts \
        frontend/src/pages/dataset/components/dataset-tabs/dataset-tabs.tsx \
        frontend/src/pages/dataset/components/dataset-tabs/model-tab/model-tab.tsx
git commit -m "feat: add Model tab shell to output port detail page"
```

---

## Task 13: Frontend — Table Schema Components

**Files:**
- Create: `frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/table-schema-list.tsx`
- Create: `frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/column-table.tsx`

The TypeScript types for `TableSchemaResponse` and `ColumnResponse` are auto-generated and available from the generated API files. Import them from the generated file (check the exact type name in `dataProductsOutputPortsTableSchemasApi.ts`).

- [ ] **Step 1: Write the column table component**

```typescript
// frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/column-table.tsx
import { Table, Tag } from 'antd';
import type { ColumnType } from 'antd/es/table';
import { useTranslation } from 'react-i18next';

// Replace with the actual generated type from the API — check:
// frontend/src/store/api/services/generated/dataProductsOutputPortsTableSchemasApi.ts
type Column = {
    id: string;
    name: string;
    description?: string | null;
    data_type?: string | null;
    tags: { id: string; value: string }[];
};

type Props = {
    columns: Column[];
};

export function ColumnTable({ columns }: Props) {
    const { t } = useTranslation();

    const tableColumns: ColumnType<Column>[] = [
        {
            title: t('Name'),
            dataIndex: 'name',
            key: 'name',
            render: (name: string) => <code>{name}</code>,
        },
        {
            title: t('Type'),
            dataIndex: 'data_type',
            key: 'data_type',
            render: (type: string | null) => type ? <code>{type}</code> : '—',
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            key: 'description',
            render: (desc: string | null) => desc ?? '—',
        },
        {
            title: t('Tags'),
            dataIndex: 'tags',
            key: 'tags',
            render: (tags: { id: string; value: string }[]) =>
                tags.map((tag) => <Tag key={tag.id}>{tag.value}</Tag>),
        },
    ];

    return (
        <Table
            dataSource={columns}
            columns={tableColumns}
            rowKey="id"
            pagination={false}
            size="small"
        />
    );
}
```

- [ ] **Step 2: Write the table schema list component**

```typescript
// frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/table-schema-list.tsx
import { Collapse, Flex, Tag } from 'antd';
import { useTranslation } from 'react-i18next';
import { ColumnTable } from './column-table';

// Replace with the actual generated type from the API — check:
// frontend/src/store/api/services/generated/dataProductsOutputPortsTableSchemasApi.ts
type TableSchema = {
    id: string;
    name: string;
    description?: string | null;
    tags: { id: string; value: string }[];
    columns: {
        id: string;
        name: string;
        description?: string | null;
        data_type?: string | null;
        tags: { id: string; value: string }[];
    }[];
};

type Props = {
    schemas: TableSchema[];
};

export function TableSchemaList({ schemas }: Props) {
    const { t } = useTranslation();

    const items = schemas.map((schema) => ({
        key: schema.id,
        label: (
            <Flex gap="small" align="center">
                <strong>{schema.name}</strong>
                {schema.description && (
                    <span style={{ color: 'var(--ant-color-text-secondary)', fontWeight: 'normal' }}>
                        {schema.description}
                    </span>
                )}
                {schema.tags.map((tag) => (
                    <Tag key={tag.id}>{tag.value}</Tag>
                ))}
            </Flex>
        ),
        children: schema.columns.length === 0 ? (
            <span style={{ color: 'var(--ant-color-text-secondary)' }}>{t('No columns')}</span>
        ) : (
            <ColumnTable columns={schema.columns} />
        ),
    }));

    return <Collapse items={items} />;
}
```

- [ ] **Step 3: Run type checker**

```bash
cd frontend && npm run check
```

Fix any type errors. If the `Column` / `TableSchema` inline types don't match the generated types, import the generated types directly from the API file instead.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/column-table.tsx \
        frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/table-schema-list.tsx
git commit -m "feat: add table schema list and column table components"
```

---

## Task 14: Frontend — Semantic Model Components and i18n

**Files:**
- Create: `frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/semantic-model-card.tsx`
- Create: `frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/semantic-model-list.tsx`

- [ ] **Step 1: Write the semantic model card**

```typescript
// frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/semantic-model-card.tsx
import { Card, Tag } from 'antd';

// Replace with generated type from dataProductsOutputPortsSemanticModelsApi.ts
type SemanticModel = {
    id: string;
    name: string;
    format: 'MetricsFlow' | 'OpenSemanticInterchange';
    content: Record<string, unknown>;
};

type Props = {
    model: SemanticModel;
};

const FORMAT_COLORS: Record<SemanticModel['format'], string> = {
    MetricsFlow: 'blue',
    OpenSemanticInterchange: 'green',
};

export function SemanticModelCard({ model }: Props) {
    return (
        <Card
            size="small"
            title={
                <span>
                    {model.name}{' '}
                    <Tag color={FORMAT_COLORS[model.format]}>{model.format}</Tag>
                </span>
            }
            style={{ marginBottom: 8 }}
        >
            <pre
                style={{
                    background: 'var(--ant-color-fill-quaternary)',
                    borderRadius: 4,
                    padding: 12,
                    overflow: 'auto',
                    maxHeight: 400,
                    fontSize: 12,
                    margin: 0,
                }}
            >
                {JSON.stringify(model.content, null, 2)}
            </pre>
        </Card>
    );
}
```

- [ ] **Step 2: Write the semantic model list**

```typescript
// frontend/src/pages/dataset/components/dataset-tabs/model-tab/components/semantic-model-list.tsx
import { SemanticModelCard } from './semantic-model-card';

type SemanticModel = {
    id: string;
    name: string;
    format: 'MetricsFlow' | 'OpenSemanticInterchange';
    content: Record<string, unknown>;
};

type Props = {
    models: SemanticModel[];
};

export function SemanticModelList({ models }: Props) {
    return (
        <>
            {models.map((model) => (
                <SemanticModelCard key={model.id} model={model} />
            ))}
        </>
    );
}
```

- [ ] **Step 3: Run type checker**

```bash
cd frontend && npm run check
```

Fix any type errors.

- [ ] **Step 4: Extract i18n translations**

```bash
cd frontend && npm run extract-translations
```

This adds any new `t('...')` keys to the translation files. Review the diff and add translations if needed.

- [ ] **Step 5: Run the frontend test suite**

```bash
cd frontend && npm test run
```

Expected: All existing tests pass (no regressions).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/dataset/components/dataset-tabs/model-tab/
git commit -m "feat: add semantic model card and list components, extract i18n strings"
```

---

## Self-Review Checklist

- [x] **Spec coverage:**
  - Table schema (description + tags on tables, description + tags + data_type on columns) — Tasks 1, 4, 5, 6, 12, 13
  - Semantic models (MetricsFlow + OSI, stored as JSONB) — Tasks 2, 8, 9, 14
  - API endpoints (GET/POST/PUT/DELETE for both) — Tasks 6, 8, 10
  - Read-only frontend Model tab — Tasks 12, 13, 14
  - Storage at output port level — confirmed in models (FK to `datasets.id`)
  - `GetOutputPortResponse` unchanged — confirmed (not touched)
  - i18n — Task 14
  - Tests — Tasks 7, 9

- [x] **No placeholders:** All code blocks are complete. Migration revision ID comes from alembic autogenerate — this is intentional (the ID is generated at migration creation time).

- [x] **Type consistency:** `OutputPortTableSchema`, `OutputPortColumn`, `OutputPortSemanticModel` names are consistent throughout. `SemanticModelFormat` used in both model and schema files. `TableSchemaRequest`/`TableSchemaResponse` match service method signatures.
