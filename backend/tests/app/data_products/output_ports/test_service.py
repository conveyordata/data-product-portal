from sqlalchemy.orm import selectinload

from app.authorization.role_assignments.enums import AssignmentFilter
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import OutputPort
from app.data_products.output_ports.service import OutputPortService
from app.settings import settings
from tests.factories import (
    DatasetRoleAssignmentFactory,
    OutputPortFactory,
    RoleFactory,
    TechnicalAssetFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)
from tests.session_util import as_user


class TestDatasetsService:
    def test_recalculate_search(self, session):
        ds = OutputPortFactory()
        OutputPortService(session).recalculate_search(ds.id)

    def test_recalculate_search_with_technical_asset(self, session):
        ds = OutputPortFactory()
        data_output = TechnicalAssetFactory(owner=ds.data_product)
        TechnicalAssetOutputPortAssociationFactory(
            data_output=data_output, output_port=ds
        )
        OutputPortService(session).recalculate_search(ds.id)

    def test_recalculate_search_for_all_output_ports(self, session):
        for i in range(51):  # Ensure we load 2 batches
            OutputPortFactory()
        OutputPortService(session).recalculate_search_for_all_output_ports()

    def test_search_output_ports_excludes_private_datasets(self, session):
        """Test that private output ports are not visible in search results to unauthorized users"""
        # Create a regular user without special permissions
        regular_user = UserFactory(external_id=settings.DEFAULT_USERNAME)

        # Create a unrestricted output port that should be visible
        unrestricted_dataset = OutputPortFactory(
            name="Public Analytics Dataset",
            access_type=OutputPortAccessType.UNRESTRICTED,
        )

        # Create a private output port that should NOT be visible
        private_dataset = OutputPortFactory(
            name="Private Sensitive Dataset", access_type=OutputPortAccessType.PRIVATE
        )

        # Create another private output port owned by a different user
        owner = UserFactory()
        owner_role = RoleFactory.dataset_owner()
        owned_private_dataset = OutputPortFactory(
            name="Owner Private Dataset", access_type=OutputPortAccessType.PRIVATE
        )
        DatasetRoleAssignmentFactory(
            role_id=owner_role.id,
            output_port_id=owned_private_dataset.id,
            user_id=owner.id,
        )

        # Recalculate search embeddings for all datasets
        OutputPortService(session).recalculate_search(unrestricted_dataset.id)
        OutputPortService(session).recalculate_search(private_dataset.id)
        OutputPortService(session).recalculate_search(owned_private_dataset.id)

        # Search as the regular user
        with as_user(session, regular_user.id):
            search_results = OutputPortService(session).search_output_ports(
                query=None,
                limit=100,
                user=regular_user,
                assignment_filter=AssignmentFilter.ALL,
            )

        # Extract dataset IDs from results
        result_ids = [ds.id for ds in search_results]

        # Assert that unrestricted dataset is visible
        assert unrestricted_dataset.id in result_ids, (
            "Unrestricted dataset should be visible to all users"
        )

        # Assert that private datasets are NOT visible
        assert private_dataset.id not in result_ids, (
            "Private dataset should not be visible to unauthorized users"
        )
        assert owned_private_dataset.id not in result_ids, (
            "Owner's private dataset should not be visible to other users"
        )

    def test_search_output_ports_owner_can_see_own_private_datasets(self, session):
        """Test that owners can see their own private output ports in search results"""
        # Create a user who will own a private dataset
        owner = UserFactory(external_id=settings.DEFAULT_USERNAME)
        owner_role = RoleFactory.dataset_owner()

        # Create a private output port owned by this user
        private_dataset = OutputPortFactory(
            name="My Private Dataset", access_type=OutputPortAccessType.PRIVATE
        )
        DatasetRoleAssignmentFactory(
            role_id=owner_role.id, output_port_id=private_dataset.id, user_id=owner.id
        )

        # Create a unrestricted dataset for comparison
        unrestricted_dataset = OutputPortFactory(
            name="Unrestricted Dataset", access_type=OutputPortAccessType.UNRESTRICTED
        )
        # Recalculate search embeddings
        OutputPortService(session).recalculate_search(private_dataset.id)
        OutputPortService(session).recalculate_search(unrestricted_dataset.id)

        with as_user(session, owner.id):
            # Search as the owner
            search_results = OutputPortService(session).search_output_ports(
                query=None,
                limit=100,
                user=owner,
                assignment_filter=AssignmentFilter.ALL,
            )

        # Extract dataset IDs from results
        result_ids = [ds.id for ds in search_results]

        # Assert that both datasets are visible to the owner
        assert private_dataset.id in result_ids, (
            "Owner should see their own private dataset"
        )
        assert unrestricted_dataset.id in result_ids, (
            "Owner should also see public datasets"
        )

    @staticmethod
    def get_output_port(output_port: OutputPort, session) -> OutputPort:
        return session.get(
            OutputPort,
            output_port.id,
            options=[selectinload(OutputPort.data_product_links)],
            populate_existing=True,
        )
