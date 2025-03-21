from datetime import datetime
from uuid import UUID

import emailgen
import pytz
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.email.send_mail import send_mail
from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_outputs.model import ensure_data_output_exists
from app.data_outputs.schema import (
    DataOutput,
    DataOutputCreate,
    DataOutputStatusUpdate,
    DataOutputUpdate,
)
from app.data_outputs.status import DataOutputStatus
from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_product_memberships.enums import DataProductUserRole
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.service import DataProductService
from app.datasets.model import ensure_dataset_exists
from app.events.enum import Type
from app.events.schema import Event, EventCreate
from app.events.service import EventService
from app.graph.graph import Graph
from app.settings import settings
from app.tags.model import Tag as TagModel
from app.tags.model import ensure_tag_exists
from app.users.schema import User


class DataOutputService:
    def ensure_member(
        self, authenticated_user: User, data_output: DataOutputCreate, db: Session
    ):
        product = db.get(DataProductModel, data_output.owner_id)
        if authenticated_user.is_admin:
            return

        data_product_membership = next(
            (
                membership
                for membership in product.memberships
                if membership.user_id == authenticated_user.id
            ),
            None,
        )
        if data_product_membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only members can execute this operation",
            )

    def ensure_owner(
        self, authenticated_user: User, data_output: DataOutputCreate, db: Session
    ):
        product = db.get(DataProductModel, data_output.owner_id)
        if authenticated_user.is_admin:
            return

        data_product_membership = next(
            (
                membership
                for membership in product.memberships
                if membership.user_id == authenticated_user.id
            ),
            None,
        )
        if (
            data_product_membership is None
            or data_product_membership.role != DataProductUserRole.OWNER
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can execute this operation",
            )

    def _get_tags(self, db: Session, tag_ids: list[UUID]) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, db)
            tags.append(tag)
        return tags

    def get_data_outputs(self, db: Session) -> list[DataOutput]:
        data_outputs = db.query(DataOutputModel).all()
        return data_outputs

    def get_data_output(self, id: UUID, db: Session) -> DataOutput:
        return db.query(DataOutputModel).filter(DataOutputModel.id == id).first()

    def get_event_history(self, id: UUID, db: Session) -> list[Event]:
        return EventService().get_history(db, id, Type.DATA_OUTPUT)

    def create_data_output(
        self, data_output: DataOutputCreate, db: Session, authenticated_user: User
    ) -> dict[str, UUID]:
        self.ensure_member(authenticated_user, data_output, db)

        if data_output.sourceAligned:
            data_output.status = DataOutputStatus.PENDING
        else:
            data_product = db.get(DataProductModel, data_output.owner_id)

            # TODO Figure out if this validation needs to happen either way
            # somehow and let sourcealigned be handled internally there?
            data_output.configuration.validate_configuration(data_product)

        data_output = data_output.parse_pydantic_schema()
        tags = self._get_tags(db, data_output.pop("tag_ids", []))
        data_output = DataOutputModel(**data_output, tags=tags)

        db.add(data_output)
        db.commit()

        # config.on_create()
        RefreshInfrastructureLambda().trigger()
        EventService().create_event(
            db,
            EventCreate(
                name="Data output created",
                subject_id=data_output.id,
                subject_type=Type.DATA_OUTPUT,
                target_id=data_output.owner_id,
                target_type=Type.DATA_PRODUCT,
                actor_id=authenticated_user.id,
                domain_id=data_output.owner.domain_id,
            ),
        )
        return {"id": data_output.id}

    def remove_data_output(self, id: UUID, db: Session, authenticated_user: User):
        data_output = db.get(
            DataOutputModel,
            id,
        )
        if not data_output:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data Output {id} not found",
            )
        self.ensure_owner(authenticated_user, data_output, db)
        data_output.dataset_links = []
        EventService().create_event(
            db,
            EventCreate(
                name="Data output removed",
                subject_id=id,
                subject_type=Type.DATA_OUTPUT,
                target_id=data_output.owner_id,
                target_type=Type.DATA_PRODUCT,
                actor_id=authenticated_user.id,
                domain_id=data_output.owner.domain_id,
            ),
        )
        db.delete(data_output)
        db.commit()
        RefreshInfrastructureLambda().trigger()

    def update_data_output_status(
        self,
        id: UUID,
        data_output: DataOutputStatusUpdate,
        db: Session,
        authenticated_user: User,
    ):
        current_data_output = ensure_data_output_exists(id, db)
        current_data_output.status = data_output.status
        db.commit()
        EventService().create_event(
            db,
            EventCreate(
                name="Data output status updated",
                subject_id=id,
                subject_type=Type.DATA_OUTPUT,
                target_id=current_data_output.owner.id,
                target_type=Type.DATA_PRODUCT,
                actor_id=authenticated_user.id,
                domain_id=current_data_output.owner.domain.id,
            ),
        )

    def link_dataset_to_data_output(
        self,
        id: UUID,
        dataset_id: UUID,
        authenticated_user: User,
        db: Session,
        background_tasks: BackgroundTasks,
    ):
        dataset = ensure_dataset_exists(dataset_id, db)
        data_output = ensure_data_output_exists(id, db)
        self.ensure_owner(authenticated_user, data_output, db)

        if dataset.id in [
            link.dataset_id
            for link in data_output.dataset_links
            if link.status != DataOutputDatasetLinkStatus.DENIED
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dataset {dataset_id} already exists in data product {id}",
            )
        # Data output requests always need to be approved
        approval_status = DataOutputDatasetLinkStatus.PENDING_APPROVAL

        dataset_link = DataOutputDatasetAssociationModel(
            dataset_id=dataset_id,
            status=approval_status,
            requested_by=authenticated_user,
            requested_on=datetime.now(tz=pytz.utc),
        )
        data_output.dataset_links.append(dataset_link)
        db.commit()
        db.refresh(data_output)
        RefreshInfrastructureLambda().trigger()
        url = settings.HOST.strip("/") + "/datasets/" + str(dataset.id) + "#data-output"
        action = emailgen.Table(
            ["Data Product", "Request", "Dataset", "Owned By", "Requested By"]
        )
        action.add_row(
            [
                data_output.owner.name,
                "Wants to provide data to ",
                dataset.name,
                ", ".join(
                    [
                        f"{owner.first_name} {owner.last_name}"
                        for owner in dataset.owners
                    ]
                ),
                f"{authenticated_user.first_name} {authenticated_user.last_name}",
            ]
        )
        background_tasks.add_task(
            send_mail,
            [User.model_validate(owner) for owner in dataset.owners],
            action,
            url,
            f"Action Required: {data_output.owner.name} wants "
            f"to provide data to {dataset.name}",
        )
        EventService().create_event(
            db,
            EventCreate(
                name="Data output link requested to dataset",
                subject_id=id,
                subject_type=Type.DATA_OUTPUT,
                target_id=dataset_id,
                target_type=Type.DATASET,
                actor_id=authenticated_user.id,
                domain_id=data_output.owner.domain.id,
            ),
        )
        return {"id": dataset_link.id}

    def unlink_dataset_from_data_output(
        self, id: UUID, dataset_id: UUID, authenticated_user: User, db: Session
    ):
        ensure_dataset_exists(dataset_id, db)
        data_output = ensure_data_output_exists(id, db)
        self.ensure_owner(authenticated_user, data_output, db)
        data_output_dataset = next(
            (
                dataset
                for dataset in data_output.dataset_links
                if dataset.dataset_id == dataset_id
            ),
            None,
        )
        if not data_output_dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product dataset for data output {id} not found",
            )
        data_output.dataset_links.remove(data_output_dataset)
        db.commit()
        RefreshInfrastructureLambda().trigger()
        EventService().create_event(
            db,
            EventCreate(
                name="Data output link removed from dataset",
                subject_id=id,
                subject_type=Type.DATA_OUTPUT,
                target_id=dataset_id,
                target_type=Type.DATASET,
                actor_id=authenticated_user.id,
                domain_id=data_output.owner.domain.id,
            ),
        )

    def update_data_output(
        self,
        id: UUID,
        data_output: DataOutputUpdate,
        db: Session,
        authenticated_user: User,
    ):
        current_data_output = ensure_data_output_exists(id, db)
        update_data_output = data_output.model_dump(exclude_unset=True)

        for k, v in update_data_output.items():
            if k == "tag_ids":
                new_tags = self._get_tags(db, v)
                current_data_output.tags = new_tags
            else:
                setattr(current_data_output, k, v) if v else None

        db.commit()
        RefreshInfrastructureLambda().trigger()
        EventService().create_event(
            db,
            EventCreate(
                name="Data output updated",
                subject_id=id,
                subject_type=Type.DATA_OUTPUT,
                target_id=current_data_output.owner.id,
                target_type=Type.DATA_PRODUCT,
                actor_id=authenticated_user.id,
                domain_id=current_data_output.owner.domain.id,
            ),
        )
        return {"id": current_data_output.id}

    def get_graph_data(self, id: UUID, level: int, db: Session) -> Graph:
        dataOutput = db.get(DataOutputModel, id)
        graph = DataProductService().get_graph_data(dataOutput.owner_id, level, db)

        for node in graph.nodes:
            if node.isMain:
                node.isMain = False
            if node.id == id:
                node.isMain = True

        return graph
