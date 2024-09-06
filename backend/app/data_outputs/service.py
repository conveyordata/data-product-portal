from datetime import datetime
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_outputs.model import ensure_data_output_exists
from app.data_outputs.schema import (
    DataOutput,
    DataOutputCreate,
    DataOutputToDB,
    DataOutputUpdate,
)
from app.data_outputs.status import DataOutputStatus
from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_product_memberships.enums import DataProductUserRole
from app.data_products.model import DataProduct as DataProductModel
from app.datasets.model import ensure_dataset_exists
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

    def get_data_outputs(self, db: Session) -> list[DataOutput]:
        data_outputs = db.query(DataOutputModel).all()
        return data_outputs
        # parsed_data_outputs = []
        # for data_output in data_outputs:
        #     parsed_data_output = data_output
        #     parsed_data_output.configuration = DataOutputMap[
        #         data_output.configuration_type
        #     ].model_validate_json(data_output.configuration)
        #     parsed_data_outputs.append(parsed_data_output)
        # return parsed_data_outputs

    def get_data_output(self, id: UUID, db: Session) -> DataOutput:
        return db.query(DataOutputModel).filter(DataOutputModel.id == id).first()

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

        # TODO Test fastapi errors?
        # TODO This needs to be better implemented > auto convert json
        data_output = DataOutputToDB(
            name=data_output.name,
            platform_id=data_output.platform_id,
            service_id=data_output.service_id,
            description=data_output.description,
            status=data_output.status,
            external_id=data_output.external_id,
            owner_id=data_output.owner_id,
            configuration=data_output.configuration.model_dump_json(),
            configuration_type=data_output.configuration.configuration_type,
        )
        data_output = DataOutputModel(**data_output.parse_pydantic_schema())

        db.add(data_output)
        db.commit()

        # config.on_create()
        RefreshInfrastructureLambda().trigger()
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
        data_output.delete()
        db.commit()

    def link_dataset_to_data_output(
        self, id: UUID, dataset_id: UUID, authenticated_user: User, db: Session
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

    def update_data_output(self, id: UUID, data_output: DataOutputUpdate, db: Session):
        current_data_output = ensure_data_output_exists(id, db)
        update_data_output = data_output.model_dump(exclude_unset=True)

        for k, v in update_data_output.items():
            setattr(current_data_output, k, v) if v else None
        db.commit()
        RefreshInfrastructureLambda().trigger()
        return {"id": current_data_output.id}
