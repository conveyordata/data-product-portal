from datetime import date, timedelta

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPort, InputPortRequest
from app.authorization.role_assignments.enums import DecisionStatus

TODAY = date.today()


def _req(decision, *, valid_until=None):
    return InputPortRequest(decision=decision, valid_until=valid_until)


def _port(*requests):
    port = InputPort()
    port.requests = list(requests)
    return port


class TestInputPortModel:
    def test_active_grant__permanent_grant(self):
        port = _port(_req(DecisionStatus.APPROVED, valid_until=None))
        assert port.active_grant.valid_until is None

    def test_active_grant__time_bound_grant_covering_today(self):
        port = _port(
            _req(DecisionStatus.APPROVED, valid_until=TODAY + timedelta(days=10)),
        )
        assert port.active_grant.valid_until == TODAY + timedelta(days=10)

    def test_active_grant__ignores_historical_ended_grant(self):
        ended = _req(DecisionStatus.APPROVED, valid_until=TODAY - timedelta(days=1))
        active = _req(DecisionStatus.APPROVED, valid_until=TODAY + timedelta(days=10))
        port = _port(ended, active)
        assert port.active_grant is active

    def test_active_grant__excludes_past_window(self):
        port = _port(
            _req(DecisionStatus.APPROVED, valid_until=TODAY - timedelta(days=1))
        )
        assert port.active_grant is None

    def test_active_grant__none_when_no_approved(self):
        port = _port(_req(DecisionStatus.PENDING))
        assert port.active_grant is None

    def test_pending_request__returns_the_pending_request(self):
        pending = _req(DecisionStatus.PENDING)
        port = _port(_req(DecisionStatus.APPROVED, valid_until=None), pending)
        assert port.pending_request is pending

    def test_pending_request__none_when_no_pending(self):
        port = _port(_req(DecisionStatus.APPROVED, valid_until=None))
        assert port.pending_request is None

    def test_recompute_status__active_permanent_grant_is_approved(self):
        port = _port(_req(DecisionStatus.APPROVED, valid_until=None))
        port.recompute_status()
        assert port.status == InputPortStatus.APPROVED

    def test_recompute_status__active_grant_wins_over_pending_renewal(self):
        port = _port(
            _req(DecisionStatus.APPROVED, valid_until=TODAY + timedelta(days=10)),
            _req(DecisionStatus.PENDING),
        )
        port.recompute_status()
        assert port.status == InputPortStatus.APPROVED

    def test_recompute_status__pending_only_is_pending(self):
        port = _port(_req(DecisionStatus.PENDING))
        port.recompute_status()
        assert port.status == InputPortStatus.PENDING

    def test_recompute_status__denied_only_is_denied(self):
        port = _port(_req(DecisionStatus.DENIED))
        port.recompute_status()
        assert port.status == InputPortStatus.DENIED

    def test_recompute_status__lapsed_grant_no_pending_is_denied_not_expired(self):
        port = _port(
            _req(DecisionStatus.APPROVED, valid_until=TODAY - timedelta(days=1))
        )
        port.recompute_status()
        assert port.status == InputPortStatus.DENIED

    def test_recompute_status__active_grant_survives_denied_renewal(self):
        port = _port(
            _req(DecisionStatus.APPROVED, valid_until=TODAY + timedelta(days=10)),
            _req(DecisionStatus.DENIED),
        )
        port.recompute_status()
        assert port.status == InputPortStatus.APPROVED

    def test_active_grant__excludes_not_yet_started_grant(self):
        future = _req(DecisionStatus.APPROVED, valid_until=TODAY + timedelta(days=40))
        future.valid_from = TODAY + timedelta(days=11)
        assert _port(future).active_grant is None
