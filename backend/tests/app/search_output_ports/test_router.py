from sqlalchemy import text

from app.authorization.roles.service import RoleService
from app.data_products.output_ports.service import DatasetService
from tests.factories import DatasetFactory


class TestOutputPortSearchRouter:
    def test_search_datasets(self, session, client):
        ds_1, ds_2, ds_3 = self.setup(session)

        response = client.get("/api/datasets/search", params={"query": "Data"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 3
        returned_ids = {item["id"] for item in data}
        expected_ids = {str(ds_1.id), str(ds_2.id), str(ds_3.id)}
        assert returned_ids == expected_ids

    def test_search_output_ports(self, session, client):
        ds_1, ds_2, ds_3 = self.setup(session)

        response = client.get("/api/v2/search/output_ports", params={"query": "Data"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["output_ports"]) == 3
        returned_ids = {item["id"] for item in data["output_ports"]}
        expected_ids = {str(ds_1.id), str(ds_2.id), str(ds_3.id)}
        assert returned_ids == expected_ids

    def test_benchmark_output_ports(self, session, client):
        self.reseed(session)

        response = client.get(
            "/api/v2/search/output_ports",
            params={"query": "Data"},
        )
        assert response.status_code == 200, response.text

    def setup(self, session):
        RoleService(db=session).initialize_prototype_roles()
        ds_1 = DatasetFactory(name="Customer Data")
        ds_2 = DatasetFactory(name="Sales Data")
        ds_3 = DatasetFactory(name="Internal Metrics")
        DatasetService(db=session).recalculate_all_embeddings()
        return ds_1, ds_2, ds_3

    def reseed(self, session):
        from app.database.database import Base
        from app.db_tool import seed_cmd

        tables_list = ", ".join(
            [str(name) for name in reversed(Base.metadata.sorted_tables)]
        )
        session.execute(text(f"TRUNCATE TABLE {tables_list} RESTART IDENTITY CASCADE;"))
        session.commit()

        seed_cmd(path="./sample_data.sql")
        RoleService(db=session).initialize_prototype_roles()
        DatasetService(db=session).recalculate_all_embeddings()
