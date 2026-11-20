from sqlalchemy.orm import selectinload

from app.authorization.role_assignments.enums import AssignmentFilter
from app.core.context import close_event_context, open_event_context, pop_events
from app.data_products.output_ports.enums import OutputPortAccessFunction
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

SEARCH_EMBEDDING = [1.0, *([0.0] * 383)]


class StaticEmbeddingModel:
    def embed(self, query):
        return [SEARCH_EMBEDDING]


class TestDatasetsService:
    def test_recalculate_search(self, session):
        ds = OutputPortFactory()
        OutputPortService(session).recalculate_search(ds.id)

    def test_recalculate_search__queues_no_events(self, session):
        ds = OutputPortFactory()
        token = open_event_context()
        try:
            OutputPortService(session).recalculate_search(ds.id)
            session.flush()
            assert pop_events() == []
        finally:
            close_event_context(token)

    def test_recalculate_search__keeps_events_of_pending_changes(self, session):
        ds = OutputPortFactory()
        token = open_event_context()
        try:
            ds.name = "Renamed"
            OutputPortService(session).recalculate_search(ds.id)
            assert len(pop_events()) == 1
        finally:
            close_event_context(token)

    def test_recalculate_search_with_technical_asset(self, session):
        ds = OutputPortFactory()
        technical_asset = TechnicalAssetFactory(owner=ds.data_product)
        TechnicalAssetOutputPortAssociationFactory(
            technical_asset=technical_asset, output_port=ds
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
            access_function=OutputPortAccessFunction.UNRESTRICTED,
        )

        # Create a private output port that should NOT be visible
        private_dataset = OutputPortFactory(
            name="Private Sensitive Dataset",
            access_function=OutputPortAccessFunction.PRIVATE,
        )

        # Create another private output port owned by a different user
        owner = UserFactory()
        owner_role = RoleFactory.dataset_owner()
        owned_private_dataset = OutputPortFactory(
            name="Owner Private Dataset",
            access_function=OutputPortAccessFunction.PRIVATE,
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
            name="My Private Dataset", access_function=OutputPortAccessFunction.PRIVATE
        )
        DatasetRoleAssignmentFactory(
            role_id=owner_role.id, output_port_id=private_dataset.id, user_id=owner.id
        )

        # Create a unrestricted dataset for comparison
        unrestricted_dataset = OutputPortFactory(
            name="Unrestricted Dataset",
            access_function=OutputPortAccessFunction.UNRESTRICTED,
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

    def test_search_output_ports__matches_partial_prefix(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        wind_output_port = OutputPortFactory(
            name="Wind Turbine Output", description="Renewable generation metrics"
        )
        unrelated_output_port = OutputPortFactory(
            name="Finance Budget", description="Quarterly accounting metrics"
        )
        self.set_search_state(session, wind_output_port, unrelated_output_port)

        partial_results = self.search_with_static_embeddings(
            session, "win", user, limit=1
        )
        full_word_results = self.search_with_static_embeddings(
            session, "wind", user, limit=1
        )

        assert [result.id for result in partial_results] == [wind_output_port.id]
        assert [result.id for result in full_word_results] == [wind_output_port.id]

    def test_search_output_ports__matches_multi_word_partial_prefix_case_insensitive(
        self, session
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        clinical_output_port = OutputPortFactory(
            name="Clinical Dataset", description="Patient outcome measures"
        )
        unrelated_output_port = OutputPortFactory(
            name="Marketing Metrics", description="Campaign performance"
        )
        self.set_search_state(session, clinical_output_port, unrelated_output_port)

        results = self.search_with_static_embeddings(
            session, "CLIN DATA", user, limit=1
        )

        assert [result.id for result in results] == [clinical_output_port.id]

    def test_search_output_ports__preserves_or_operator(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        finance_output_port = OutputPortFactory(
            name="Finance Ledger", description="Accounting metrics"
        )
        budget_output_port = OutputPortFactory(
            name="Budget Forecast", description="Planning metrics"
        )
        unrelated_output_port = OutputPortFactory(
            name="Telemetry Events", description="Device metrics"
        )
        self.set_search_state(
            session, finance_output_port, budget_output_port, unrelated_output_port
        )

        results = self.search_with_static_embeddings(
            session, "finance OR budget", user, limit=2
        )

        assert {result.id for result in results} == {
            finance_output_port.id,
            budget_output_port.id,
        }

    def test_search_output_ports__preserves_exclusion_operator(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        excluded_output_port = OutputPortFactory(
            name="Finance Budget", description="Restricted budget planning"
        )
        matching_output_port = OutputPortFactory(
            name="Finance Forecast", description="Revenue planning"
        )
        unrelated_output_port = OutputPortFactory(
            name="Marketing Leads", description="Pipeline metrics"
        )
        self.set_search_state(
            session, excluded_output_port, matching_output_port, unrelated_output_port
        )

        results = self.search_with_static_embeddings(
            session, "finance -budget", user, limit=1
        )

        assert [result.id for result in results] == [matching_output_port.id]

    def test_search_output_ports__prefixes_terms_after_leading_exclusion(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        excluded_output_port = OutputPortFactory(
            name="Finance Budget", description="Restricted budget planning"
        )
        matching_output_port = OutputPortFactory(
            name="Finance Forecast", description="Revenue planning"
        )
        self.set_search_state(session, excluded_output_port, matching_output_port)

        results = self.search_with_static_embeddings(
            session, "-budget fin", user, limit=1
        )

        assert [result.id for result in results] == [matching_output_port.id]

    def test_search_output_ports__does_not_prefix_excluded_quoted_phrase(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        excluded_output_port = OutputPortFactory(
            name="Finance Budget Plan", description="Yearly figures"
        )
        matching_output_port = OutputPortFactory(
            name="Finance Budget Planner", description="Yearly figures"
        )
        unrelated_output_port = OutputPortFactory(
            name="Marketing Leads", description="Pipeline metrics"
        )
        self.set_search_state(
            session, excluded_output_port, matching_output_port, unrelated_output_port
        )

        results = self.search_with_static_embeddings(
            session, 'fin -"budget plan"', user, limit=1
        )

        assert [result.id for result in results] == [matching_output_port.id]

    def test_search_output_ports__preserves_quoted_phrase_operator(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        reversed_output_port = OutputPortFactory(
            name="Alpha Data Customer", description="Reversed word order"
        )
        phrase_output_port = OutputPortFactory(
            name="Zulu Customer Data", description="Customer data mart"
        )
        self.set_search_state(session, reversed_output_port, phrase_output_port)

        results = self.search_with_static_embeddings(
            session, '"customer data"', user, limit=1
        )

        assert [result.id for result in results] == [phrase_output_port.id]

    def test_search_output_ports__preserves_accented_unicode_terms(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        unrelated_output_port = OutputPortFactory(
            name="Aachen Mobility", description="Regional transport metrics"
        )
        unicode_output_port = OutputPortFactory(
            name="München Mobility", description="Regional transport metrics"
        )
        self.set_search_state(session, unrelated_output_port, unicode_output_port)

        results = self.search_with_static_embeddings(session, "München", user, limit=1)

        assert [result.id for result in results] == [unicode_output_port.id]

    def test_search_output_ports__handles_empty_punctuation_and_stop_word_queries(
        self, session
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        alpha_output_port = OutputPortFactory(name="Alpha Dataset")
        zulu_output_port = OutputPortFactory(name="Zulu Dataset")
        self.set_search_state(session, alpha_output_port, zulu_output_port)

        whitespace_results = self.search_with_static_embeddings(
            session, "   ", user, limit=2
        )
        punctuation_results = self.search_with_static_embeddings(
            session, "?!...", user, limit=2
        )
        stop_word_results = self.search_with_static_embeddings(
            session, "the and", user, limit=2
        )

        expected_default_order = [alpha_output_port.id, zulu_output_port.id]
        assert [result.id for result in whitespace_results] == expected_default_order
        assert [result.id for result in punctuation_results] == expected_default_order
        assert {result.id for result in stop_word_results} == set(
            expected_default_order
        )

    @staticmethod
    def get_output_port(output_port: OutputPort, session) -> OutputPort:
        return session.get(
            OutputPort,
            output_port.id,
            options=[selectinload(OutputPort.data_product_links)],
            populate_existing=True,
        )

    @staticmethod
    def set_search_state(session, *output_ports: OutputPort) -> None:
        for output_port in output_ports:
            output_port.embeddings = SEARCH_EMBEDDING
            OutputPortService._recalculate_search_vector(output_port)
            session.add(output_port)
        session.flush()

    @staticmethod
    def search_with_static_embeddings(session, query: str, user, limit: int):
        service = OutputPortService(session)
        service.embedding_model = StaticEmbeddingModel()
        return service.search_output_ports(
            query=query,
            limit=limit,
            user=user,
            assignment_filter=AssignmentFilter.ALL,
        )
