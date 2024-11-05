from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.datasets.model import Dataset as DatasetModel
from app.datasets.model import ensure_dataset_exists
from app.datasets.schema import DatasetAboutUpdate, DatasetCreateUpdate
from app.datasets.schema_get import DatasetGet, DatasetsGet
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.tags.model import Tag as TagModel
from app.users.model import ensure_user_exists


class DatasetService:
    def get_dataset(self, id: UUID, db: Session) -> DatasetGet:
        dataset = db.get(
            DatasetModel,
            id,
            options=[
                joinedload(DatasetModel.data_product_links),
            ],
        )

        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
            )
        return dataset

    def get_datasets(self, db: Session) -> list[DatasetsGet]:
        return db.query(DatasetModel).order_by(asc(DatasetModel.name)).all()

    def get_user_datasets(self, user_id: UUID, db: Session) -> list[DatasetsGet]:
        return (
            db.query(DatasetModel)
            .options(joinedload(DatasetModel.owners))
            .join(DatasetModel.owners)
            .filter(DatasetModel.owners.any(id=user_id))
            .order_by(asc(DatasetModel.name))
            .all()
        )

    def _update_owners(
        self, dataset: DatasetCreateUpdate, db: Session, owner_ids: list[UUID] = []
    ) -> DatasetCreateUpdate:
        if not owner_ids:
            owner_ids = dataset.owners
        dataset.owners = []
        for owner in owner_ids:
            user = ensure_user_exists(owner, db)
            dataset.owners.append(user)
        return dataset

    def create_dataset(
        self, dataset: DatasetCreateUpdate, db: Session
    ) -> dict[str, UUID]:
        dataset = self._update_owners(dataset, db)
        dataset = DatasetModel(**dataset.parse_pydantic_schema())
        db.add(dataset)
        db.commit()
        RefreshInfrastructureLambda().trigger()

        return {"id": dataset.id}

    def remove_dataset(self, id: UUID, db: Session):
        dataset = db.get(
            DatasetModel,
            id,
            options=[joinedload(DatasetModel.data_product_links)],
        )
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset {id} not found"
            )
        dataset.owners = []
        dataset.data_product_links = []
        dataset.tags = []
        dataset.delete()

        db.commit()
        RefreshInfrastructureLambda().trigger()

    def update_dataset(self, id: UUID, dataset: DatasetCreateUpdate, db: Session):
        current_dataset = ensure_dataset_exists(id, db)
        updated_dataset = dataset.model_dump(exclude_unset=True)

        for k, v in updated_dataset.items():
            if k == "owners":
                current_dataset = self._update_owners(current_dataset, db, v)
            elif k == "tags":
                current_dataset.tags = []
                for tag_data in v:
                    tag = TagModel(**tag_data)
                    current_dataset.tags.append(tag)
            else:
                setattr(current_dataset, k, v) if v else None
        db.commit()
        RefreshInfrastructureLambda().trigger()
        return {"id": current_dataset.id}

    def update_dataset_about(self, id: UUID, dataset: DatasetAboutUpdate, db: Session):
        current_dataset = ensure_dataset_exists(id, db)
        current_dataset.about = dataset.about
        db.commit()

    def add_user_to_dataset(self, dataset_id: UUID, user_id: UUID, db: Session):
        dataset = ensure_dataset_exists(dataset_id, db)
        user = ensure_user_exists(user_id, db)
        if user in dataset.owners:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_id} is already an owner of dataset {dataset_id}",
            )

        dataset.owners.append(user)
        db.commit()
        RefreshInfrastructureLambda().trigger()

    def remove_user_from_dataset(self, dataset_id: UUID, user_id: UUID, db: Session):
        dataset = ensure_dataset_exists(dataset_id, db)
        user = ensure_user_exists(user_id, db)
        dataset.owners.remove(user)
        db.commit()
        RefreshInfrastructureLambda().trigger()

    def get_graph_data(self, id: UUID, level: int, db: Session) -> Graph:
        dataset = db.get(DatasetModel, id)
        nodes = [
            Node(
                id=id,
                isMain=True,
                data=NodeData(id=id, name=dataset.name),
                type=NodeType.datasetNode,
            )
        ]
        edges = []
        for downstream_products in dataset.data_product_links:
            nodes.append(
                Node(
                    id=downstream_products.data_product_id,
                    data=NodeData(
                        id=downstream_products.data_product_id,
                        name=downstream_products.data_product.name,
                        icon_key=downstream_products.data_product.type.icon_key,
                    ),
                    type=NodeType.dataProductNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{downstream_products.id}-{dataset.id}",
                    target=downstream_products.data_product_id,
                    source=dataset.id,
                    animated=downstream_products.status
                    == DataProductDatasetLinkStatus.APPROVED,
                )
            )

        for data_output_link in dataset.data_output_links:
            data_output = data_output_link.data_output
            nodes.append(
                Node(
                    id=data_output.id,
                    data=NodeData(
                        id=data_output.id,
                        icon_key=data_output.configuration.configuration_type,
                        name=data_output.name,
                        link_to_id=data_output.owner_id,
                    ),
                    type=NodeType.dataOutputNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{data_output.id}-{dataset.id}",
                    source=data_output.id,
                    target=dataset.id,
                    animated=data_output_link.status
                    == DataOutputDatasetLinkStatus.APPROVED,
                )
            )
            if level >= 2:
                nodes.append(
                    Node(
                        id=f"{data_output.owner.id}_2",
                        data=NodeData(
                            id=f"{data_output.owner.id}",
                            name=data_output.owner.name,
                            icon_key=data_output.owner.type.icon_key,
                        ),
                        type=NodeType.dataProductNode,
                    )
                )
                edges.append(
                    Edge(
                        id=f"{data_output.owner.id}-{data_output.id}-2",
                        target=data_output.id,
                        source=f"{data_output.owner.id}_2",
                        animated=True,
                    )
                )
        return Graph(nodes=set(nodes), edges=set(edges))
