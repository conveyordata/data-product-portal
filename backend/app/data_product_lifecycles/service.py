from uuid import UUID

from sqlalchemy.orm import Session

from app.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.data_product_lifecycles.schema import (
    DataProductLifeCycle,
    DataProductLifeCycleCreate,
)


class DataProductLifeCycleService:
    def get_data_product_lifecycles(self, db: Session) -> list[DataProductLifeCycle]:
        return (
            db.query(DataProductLifeCycleModel)
            .order_by(DataProductLifeCycleModel.name)
            .all()
        )

    def create_data_product_lifecycle(
        self, data_product_lifecycle: DataProductLifeCycleCreate, db: Session
    ) -> dict[str, UUID]:
        data_product_lifecycle = DataProductLifeCycleModel(
            **data_product_lifecycle.parse_pydantic_schema()
        )
        db.add(data_product_lifecycle)
        db.commit()
        return {"id": data_product_lifecycle.id}
