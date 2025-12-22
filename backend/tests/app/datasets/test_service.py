import pytest
from sqlalchemy.orm import selectinload

from app.authorization.roles import ADMIN_UUID
from app.authorization.roles.schema import Prototype, Scope
from app.data_outputs.model import DataOutput
from app.data_outputs.service import DataOutputService
from app.datasets.enums import OutputPortAccessType
from app.datasets.model import Dataset
from app.datasets.service import DatasetService
from app.settings import settings
from tests import test_session
from tests.factories import (
    DataOutputFactory,
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)


class TestDatasetsService:
    def test_private_dataset_not_visible(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert DatasetService(test_session).is_visible_to_user(ds, user) is False

    def test_get_private_dataset_by_owner(self):
        owner = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.DATASET, prototype=Prototype.OWNER)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(
            role_id=role.id, dataset_id=ds.id, user_id=owner.id
        )
        ds = self.get_dataset(ds)
        assert DatasetService(test_session).is_visible_to_user(ds, owner) is True

    def test_get_private_dataset_by_admin(self):
        admin = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.GLOBAL, prototype=Prototype.ADMIN, id=ADMIN_UUID)
        GlobalRoleAssignmentFactory(role_id=role.id, user_id=admin.id)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert DatasetService(test_session).is_visible_to_user(ds, admin) is True

    def test_get_private_dataset_by_member_of_consuming_data_product(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        dp = DataProductFactory()
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            role_id=role.id, data_product_id=dp.id, user_id=user.id
        )
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)
        ds = self.get_dataset(ds)
        assert DatasetService(test_session).is_visible_to_user(ds, user) is True

    def test_create_search_vector_dataset(self):
        settings.SEARCH_INDEXING_DISABLED = False
        ds = DatasetFactory()

        updated_rows = DatasetService(test_session).recalculate_search_vector_for(ds.id)

        assert updated_rows == 1

    def test_create_search_vector_indexing_disabled(self):
        settings.SEARCH_INDEXING_DISABLED = True
        ds = DatasetFactory()

        updated_rows = DatasetService(test_session).recalculate_search_vector_for(ds.id)

        assert updated_rows == 0

    def test_create_search_vector_all_datasets(self):
        settings.SEARCH_INDEXING_DISABLED = False
        DatasetFactory()
        DatasetFactory()

        updated_rows = DatasetService(test_session).recalculate_search_vector_datasets()

        assert updated_rows == 2

    def test_create_search_vector_all_datasets_indexing_disabled(self):
        settings.SEARCH_INDEXING_DISABLED = True
        DatasetFactory()
        DatasetFactory()

        updated_rows = DatasetService(test_session).recalculate_search_vector_datasets()

        assert updated_rows == 0

    def test_search_dataset_matching_description(self):
        settings.SEARCH_INDEXING_DISABLED = False
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(
            name="dataset name", description="Clinical dataset patient information"
        )
        DatasetService(test_session).recalculate_search_vector_for(ds.id)

        results = DatasetService(test_session).search_datasets("patient", 10, user)

        assert len(results) == 1
        assert results[0].id == ds.id
        assert results[0].description == ds.description
        assert results[0].rank == pytest.approx(0.2857143)

    def test_search_dataset_matching_name(self):
        settings.SEARCH_INDEXING_DISABLED = False
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(
            name="Clinical dataset patient information", description="description"
        )
        DatasetService(test_session).recalculate_search_vector_for(ds.id)

        results = DatasetService(test_session).search_datasets("patient", 10, user)

        assert len(results) == 1
        assert results[0].id == ds.id
        assert results[0].description == ds.description
        assert results[0].rank == pytest.approx(0.5)

    def test_search_dataset_matching_name_and_description(self):
        settings.SEARCH_INDEXING_DISABLED = False
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(name="Clinical dataset", description="clinical studies")
        DatasetService(test_session).recalculate_search_vector_for(ds.id)

        results = DatasetService(test_session).search_datasets("clinical", 10, user)

        assert len(results) == 1
        assert results[0].id == ds.id
        assert results[0].description == ds.description
        assert results[0].rank == pytest.approx(0.5833333)

    def test_search_dataset_infix_matches(self):
        settings.SEARCH_INDEXING_DISABLED = False
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(name="Clinical dataset", description="Some details")
        DatasetService(test_session).recalculate_search_vector_for(ds.id)

        # Partial token 'inica' should match 'Clinical' via infix (substring) search
        results = DatasetService(test_session).search_datasets("inica", 10, user)

        assert len(results) == 1
        assert results[0].id == ds.id
    
    # Add test for multi-word matching and/or matching in both title and description    
    def test_search_dataset_multi_word_query_matches_multiple_words(self):
        """Test that multi-word query 'clin data' matches 'Clinical dataset'."""
        settings.SEARCH_INDEXING_DISABLED = False
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(
            name="Clinical dataset",
            description="Patient information and medical records"
        )
        DatasetService(test_session).recalculate_search_vector_for(ds.id)

        # 'clin data' should match 'Clinical dataset' (both words present)
        results = DatasetService(test_session).search_datasets("clin data", 10, user)
        assert len(results) == 1
        assert results[0].id == ds.id
        assert results[0].name == ds.name

    def test_search_dataset_query_matches_in_both_title_and_description(self):
        """Test that query matches content in both title/name and description."""
        settings.SEARCH_INDEXING_DISABLED = False
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        
        # Dataset with 'patient' in name and 'clinical' in description
        ds = DatasetFactory(
            name="Patient data records", 
            description="Clinical information and medical history"
        )
        DatasetService(test_session).recalculate_search_vector_for(ds.id)
        # Search for 'patient' - should match (in name)
        results_patient = DatasetService(test_session).search_datasets("patient", 10, user)
        assert len(results_patient) == 1
        assert results_patient[0].id == ds.id
    
        # Search for 'clinical' - should match (in description)
        results_clinical = DatasetService(test_session).search_datasets("clinical", 10, user)
        assert len(results_clinical) == 1
        assert results_clinical[0].id == ds.id
    
        # Search for 'patient clinical' - should match (one in name, one in description)
        results_both = DatasetService(test_session).search_datasets("patient clinical", 10, user)
        assert len(results_both) == 1
        assert results_both[0].id == ds.id
    def test_search_dataset_matching_data_output_name(self):
        settings.SEARCH_INDEXING_DISABLED = False
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        do, ds = self.create_datasets_with_data_output(
            data_output_name="Patient data", dataset_name="dataset name"
        )
        DataOutputService(test_session).link_dataset_to_data_output(
            id=do.id, dataset_id=ds.id, actor=user
        )
        DatasetService(test_session).recalculate_search_vector_for(ds.id)

        results = DatasetService(test_session).search_datasets("patient", 10, user)

        assert len(results) == 1
        assert results[0].id == ds.id
        assert results[0].description == ds.description
        assert results[0].rank == pytest.approx(0.5)

    def test_search_dataset_matching_data_output_description(self):
        settings.SEARCH_INDEXING_DISABLED = False
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        do, ds = self.create_datasets_with_data_output(
            data_output_name="data output",
            dataset_name="dataset",
            data_output_description="patient info",
        )
        DataOutputService(test_session).link_dataset_to_data_output(
            id=do.id, dataset_id=ds.id, actor=user
        )
        DatasetService(test_session).recalculate_search_vector_for(ds.id)

        results = DatasetService(test_session).search_datasets("patient", 10, user)

        assert len(results) == 1
        assert results[0].id == ds.id
        assert results[0].description == ds.description
        assert results[0].rank == pytest.approx(0.2857143)

    def test_search_dataset_unexisting_word(self):
        settings.SEARCH_INDEXING_DISABLED = False
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(description="Clinical dataset for patient information")
        DatasetService(test_session).recalculate_search_vector_for(ds.id)

        results = DatasetService(test_session).search_datasets("CRM details", 10, user)

        assert len(results) == 0

    def create_datasets_with_data_output(
        self, data_output_name, dataset_name, data_output_description=""
    ) -> tuple[DataOutputFactory, DatasetFactory]:
        data_product = DataProductFactory()
        do = DataOutputFactory(
            name=data_output_name,
            owner=data_product,
            description=data_output_description,
        )
        ds = DatasetFactory(name=dataset_name, data_product=data_product)
        test_session.get(
            DataOutput,
            do.id,
            options=[selectinload(DataOutput.dataset_links)],
            populate_existing=True,
        )
        return do, ds

    @staticmethod
    def get_dataset(dataset: Dataset) -> Dataset:
        return test_session.get(
            Dataset,
            dataset.id,
            options=[selectinload(Dataset.data_product_links)],
            populate_existing=True,
        )

    # Unit tests for _build_prefix_tsquery function
    def test_build_prefix_tsquery_basic(self):
        """Test basic query with two words."""
        result = DatasetService._build_prefix_tsquery("Hello world")
        assert result == "hello:* & world:*"

    def test_build_prefix_tsquery_with_special_characters(self):
        """Test query with special characters."""
        result = DatasetService._build_prefix_tsquery("Hello, world!")
        assert result == "hello:* & world:*"

    def test_build_prefix_tsquery_filters_short_tokens(self):
        """Test that single character tokens are filtered out."""
        result = DatasetService._build_prefix_tsquery("a b cd")
        assert result == "*cd:*"

    def test_build_prefix_tsquery_all_short_tokens(self):
        """Test that None is returned when all tokens are too short."""
        result = DatasetService._build_prefix_tsquery("a b c")
        assert result is None

    def test_build_prefix_tsquery_empty_string(self):
        """Test that None is returned for empty string."""
        result = DatasetService._build_prefix_tsquery("")
        assert result is None

    def test_build_prefix_tsquery_none_input(self):
        """Test that None is returned for None input."""
        result = DatasetService._build_prefix_tsquery(None)
        assert result is None

    def test_build_prefix_tsquery_whitespace_only(self):
        """Test that None is returned for whitespace only."""
        result = DatasetService._build_prefix_tsquery("   ")
        assert result is None

    def test_build_prefix_tsquery_multiple_words_with_numbers(self):
        """Test query with words and numbers."""
        result = DatasetService._build_prefix_tsquery("dataset123 test456")
        assert result == "*dataset123:* & *test456:*"

    def test_build_prefix_tsquery_case_insensitive(self):
        """Test that query is converted to lowercase."""
        result = DatasetService._build_prefix_tsquery("Hello WORLD Test")
        assert result == "hello:* & world:* & test:*"
    def test_build_prefix_tsquery_hyphens_and_underscores(self):
        """Test that hyphens and underscores are treated as word boundaries."""
        result = DatasetService._build_prefix_tsquery("test-data_set")
        assert result == "test:* & data:* & set:*"
