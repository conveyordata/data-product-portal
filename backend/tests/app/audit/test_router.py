import pytest
from tests.factories.audit_log import AuditLogFactory

ENDPOINT = "/api/audit_logs"


class TestAuditLogsRouter:
    @pytest.mark.usefixtures("admin")
    def test_get_audit_logs(self, client):
        AuditLogFactory()
        response = self.get_audit_logs(client)
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.usefixtures("admin")
    def test_get_audit_log(self, client):
        audit_log = AuditLogFactory()
        response = self.get_audit_log(client, audit_log.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(audit_log.id)

    @staticmethod
    def get_audit_logs(client):
        return client.get(ENDPOINT)

    @staticmethod
    def get_audit_log(client, id):
        return client.get(f"{ENDPOINT}/{id}")
