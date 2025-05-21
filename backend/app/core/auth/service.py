from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth.credentials import AWSCredentials
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.service import DataProductService
from app.environments.service import EnvironmentService
from app.users.schema import User


class AuthService:
    def get_aws_credentials(
        self,
        data_product_name: str,
        environment: str,
        authorized_user: User,
        db: Session,
    ) -> AWSCredentials:
        envs = EnvironmentService(db).get_environments()
        if environment not in [e.name for e in envs]:
            for env in envs:
                if env.is_default:
                    environment = env.name
                    break
        data_product_id = (
            db.execute(
                select(DataProductModel).where(
                    DataProductModel.namespace == data_product_name
                )
            )
            .unique()
            .scalar_one()
            .id
        )
        role_arn = DataProductService().get_data_product_role_arn(
            data_product_id, environment, db
        )
        return DataProductService().get_aws_temporary_credentials(
            role_arn, authorized_user
        )
