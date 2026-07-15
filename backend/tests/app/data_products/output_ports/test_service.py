from sqlalchemy.orm import selectinload

from app.authorization.roles.schema import Scope
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import Dataset
from app.data_products.output_ports.service import OutputPortService
from app.settings import settings
from tests import test_session
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    GlobalRoleAssignmentFactory,
    InputPortFactory,
    RoleFactory,
    TechnicalAssetFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)

SEARCH_EMBEDDING = [1.0, *([0.0] * 383)]


class StaticEmbeddingModel:
    def embed(self, query):
        return [SEARCH_EMBEDDING]


class TestDatasetsService:
    def test_private_dataset_not_visible(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert OutputPortService(test_session).is_visible_to_user(ds, user) is False

    def test_get_private_dataset_by_owner(self):
        owner = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory.dataset_owner()
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(
            role_id=role.id, dataset_id=ds.id, user_id=owner.id
        )
        ds = self.get_dataset(ds)
        assert OutputPortService(test_session).is_visible_to_user(ds, owner) is True

    def test_get_private_dataset_by_admin(self):
        admin = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory.admin()
        GlobalRoleAssignmentFactory(role_id=role.id, user_id=admin.id)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert OutputPortService(test_session).is_visible_to_user(ds, admin) is True

    def test_get_private_dataset_by_member_of_consuming_data_product(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        dp = DataProductFactory()
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            role_id=role.id, data_product_id=dp.id, user_id=user.id
        )
        InputPortFactory(consuming_abstract_data_product=dp, dataset=ds)
        ds = self.get_dataset(ds)
        assert OutputPortService(test_session).is_visible_to_user(ds, user) is True

    def test_recalculate_search(self):
        ds = DatasetFactory()
        OutputPortService(test_session).recalculate_search(ds.id)

    def test_recalculate_search_with_technical_asset(self):
        ds = DatasetFactory()
        data_output = TechnicalAssetFactory(owner=ds.data_product)
        TechnicalAssetOutputPortAssociationFactory(data_output=data_output, dataset=ds)
        OutputPortService(test_session).recalculate_search(ds.id)

    def test_recalculate_search_for_all_output_ports(self):
        for i in range(51):  # Ensure we load 2 batches
            DatasetFactory()
        OutputPortService(test_session).recalculate_search_for_all_output_ports()

    def test_search_output_ports_excludes_private_datasets(self):
        """Test that private output ports are not visible in search results to unauthorized users"""
        # Create a regular user without special permissions
        regular_user = UserFactory(external_id=settings.DEFAULT_USERNAME)

        # Create a unrestricted output port that should be visible
        unrestricted_dataset = DatasetFactory(
            name="Public Analytics Dataset",
            access_type=OutputPortAccessType.UNRESTRICTED,
        )

        # Create a private output port that should NOT be visible
        private_dataset = DatasetFactory(
            name="Private Sensitive Dataset", access_type=OutputPortAccessType.PRIVATE
        )

        # Create another private output port owned by a different user
        owner = UserFactory()
        owner_role = RoleFactory.dataset_owner()
        owned_private_dataset = DatasetFactory(
            name="Owner Private Dataset", access_type=OutputPortAccessType.PRIVATE
        )
        DatasetRoleAssignmentFactory(
            role_id=owner_role.id, dataset_id=owned_private_dataset.id, user_id=owner.id
        )

        # Recalculate search embeddings for all datasets
        OutputPortService(test_session).recalculate_search(unrestricted_dataset.id)
        OutputPortService(test_session).recalculate_search(private_dataset.id)
        OutputPortService(test_session).recalculate_search(owned_private_dataset.id)

        # Search as the regular user
        search_results = OutputPortService(test_session).search_output_ports(
            query=None, limit=100, user=regular_user, current_user_assigned=False
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

    def test_search_output_ports_owner_can_see_own_private_datasets(self):
        """Test that owners can see their own private output ports in search results"""
        # Create a user who will own a private dataset
        owner = UserFactory(external_id=settings.DEFAULT_USERNAME)
        owner_role = RoleFactory.dataset_owner()

        # Create a private output port owned by this user
        private_dataset = DatasetFactory(
            name="My Private Dataset", access_type=OutputPortAccessType.PRIVATE
        )
        DatasetRoleAssignmentFactory(
            role_id=owner_role.id, dataset_id=private_dataset.id, user_id=owner.id
        )

        # Create a unrestricted dataset for comparison
        unrestricted_dataset = DatasetFactory(
            name="Unrestricted Dataset", access_type=OutputPortAccessType.UNRESTRICTED
        )

        # Recalculate search embeddings
        OutputPortService(test_session).recalculate_search(private_dataset.id)
        OutputPortService(test_session).recalculate_search(unrestricted_dataset.id)

        # Search as the owner
        search_results = OutputPortService(test_session).search_output_ports(
            query=None, limit=100, user=owner, current_user_assigned=False
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

    def test_search_output_ports_matches_partial_prefix(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        wind_dataset = DatasetFactory(
            name="Wind Turbine Output", description="Renewable generation metrics"
        )
        unrelated_dataset = DatasetFactory(
            name="Finance Budget", description="Quarterly accounting metrics"
        )
        self.set_search_state(wind_dataset, unrelated_dataset)

        partial_results = self.search_with_static_embeddings("win", user, limit=1)
        full_word_results = self.search_with_static_embeddings("wind", user, limit=1)

        assert [result.id for result in partial_results] == [wind_dataset.id]
        assert [result.id for result in full_word_results] == [wind_dataset.id]

    def test_search_output_ports_matches_multi_word_partial_prefix_case_insensitive(
        self,
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        clinical_dataset = DatasetFactory(
            name="Clinical Dataset", description="Patient outcome measures"
        )
        unrelated_dataset = DatasetFactory(
            name="Marketing Metrics", description="Campaign performance"
        )
        self.set_search_state(clinical_dataset, unrelated_dataset)

        results = self.search_with_static_embeddings("CLIN DATA", user, limit=1)

        assert [result.id for result in results] == [clinical_dataset.id]

    def test_search_output_ports_preserves_or_operator(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        finance_dataset = DatasetFactory(
            name="Finance Ledger", description="Accounting metrics"
        )
        budget_dataset = DatasetFactory(
            name="Budget Forecast", description="Planning metrics"
        )
        unrelated_dataset = DatasetFactory(
            name="Telemetry Events", description="Device metrics"
        )
        self.set_search_state(finance_dataset, budget_dataset, unrelated_dataset)

        results = self.search_with_static_embeddings(
            "finance OR budget", user, limit=2
        )

        assert {result.id for result in results} == {
            finance_dataset.id,
            budget_dataset.id,
        }

    def test_search_output_ports_preserves_exclusion_operator(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        excluded_dataset = DatasetFactory(
            name="Finance Budget", description="Restricted budget planning"
        )
        matching_dataset = DatasetFactory(
            name="Finance Forecast", description="Revenue planning"
        )
        unrelated_dataset = DatasetFactory(
            name="Marketing Leads", description="Pipeline metrics"
        )
        self.set_search_state(excluded_dataset, matching_dataset, unrelated_dataset)

        results = self.search_with_static_embeddings("finance -budget", user, limit=1)

        assert [result.id for result in results] == [matching_dataset.id]

    def test_search_output_ports_preserves_quoted_phrase_operator(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        reversed_dataset = DatasetFactory(
            name="Alpha Data Customer", description="Reversed word order"
        )
        phrase_dataset = DatasetFactory(
            name="Zulu Customer Data", description="Customer data mart"
        )
        self.set_search_state(reversed_dataset, phrase_dataset)

        results = self.search_with_static_embeddings('"customer data"', user, limit=1)

        assert [result.id for result in results] == [phrase_dataset.id]

    def test_search_output_ports_preserves_accented_unicode_terms(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        unrelated_dataset = DatasetFactory(
            name="Aachen Mobility", description="Regional transport metrics"
        )
        unicode_dataset = DatasetFactory(
            name="München Mobility", description="Regional transport metrics"
        )
        self.set_search_state(unrelated_dataset, unicode_dataset)

        results = self.search_with_static_embeddings("München", user, limit=1)

        assert [result.id for result in results] == [unicode_dataset.id]

    def test_search_output_ports_handles_empty_punctuation_and_stop_word_queries(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        alpha_dataset = DatasetFactory(name="Alpha Dataset")
        zulu_dataset = DatasetFactory(name="Zulu Dataset")
        self.set_search_state(alpha_dataset, zulu_dataset)

        whitespace_results = self.search_with_static_embeddings("   ", user, limit=2)
        punctuation_results = self.search_with_static_embeddings("?!...", user, limit=2)
        stop_word_results = self.search_with_static_embeddings("the and", user, limit=2)

        expected_default_order = [alpha_dataset.id, zulu_dataset.id]
        assert [result.id for result in whitespace_results] == expected_default_order
        assert [result.id for result in punctuation_results] == expected_default_order
        assert {result.id for result in stop_word_results} == set(expected_default_order)

    @staticmethod
    def get_dataset(dataset: Dataset) -> Dataset:
        return test_session.get(
            Dataset,
            dataset.id,
            options=[selectinload(Dataset.data_product_links)],
            populate_existing=True,
        )

    @staticmethod
    def set_search_state(*datasets: Dataset) -> None:
        for dataset in datasets:
            dataset.embeddings = SEARCH_EMBEDDING
            OutputPortService._recalculate_search_vector(dataset)
            test_session.add(dataset)
        test_session.commit()

    @staticmethod
    def search_with_static_embeddings(query: str, user, limit: int):
        service = OutputPortService(test_session)
        service.embedding_model = StaticEmbeddingModel()
        return service.search_output_ports(
            query=query, limit=limit, user=user, current_user_assigned=False
        )
