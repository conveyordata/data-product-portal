from datetime import date, datetime, timedelta

import pytz

from app.abstract_data_product.input_ports.enums import InputPortStatus, RenewalStatus
from app.authorization.role_assignments.enums import DecisionStatus
from tests.factories import InputPortFactory, InputPortRequestFactory

TODAY = date.today()
NOW = datetime.now(pytz.utc)


class TestInputPortModel:
    def test_active_grant__permanent_grant(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED, valid_until=None, decided_by=None
                )
            ],
        )
        assert port.active_grant.valid_until is None

    def test_active_grant__time_bound_grant_covering_today(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    decided_by=None,
                )
            ],
        )
        assert port.active_grant.valid_until == TODAY + timedelta(days=10)

    def test_active_grant__ignores_historical_ended_grant(self):
        ended = InputPortRequestFactory.build(
            decision=DecisionStatus.APPROVED,
            valid_until=TODAY - timedelta(days=1),
            created_on=NOW - timedelta(days=10),
            decided_by=None,
        )
        active = InputPortRequestFactory.build(
            decision=DecisionStatus.APPROVED,
            valid_until=TODAY + timedelta(days=10),
            created_on=NOW,
            decided_by=None,
        )
        port = InputPortFactory.build(request=False, requests=[ended, active])
        assert port.active_grant is active

    def test_active_grant__2_active_grants_returns_latest(self):
        active_old = InputPortRequestFactory.build(
            decision=DecisionStatus.APPROVED,
            valid_until=TODAY + timedelta(days=1),
            created_on=NOW - timedelta(days=10),
            decided_by=None,
        )
        active_new = InputPortRequestFactory.build(
            decision=DecisionStatus.APPROVED,
            valid_until=TODAY + timedelta(days=10),
            created_on=NOW - timedelta(days=1),
            decided_by=None,
        )
        port = InputPortFactory.build(request=False, requests=[active_old, active_new])
        assert port.active_grant is active_new

    def test_active_grant__excludes_past_window(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED,
                    valid_until=TODAY - timedelta(days=1),
                    decided_by=None,
                )
            ],
        )
        assert port.active_grant is None

    def test_active_grant__none_when_no_approved(self):
        port = InputPortFactory.build(
            request=False,
            requests=[InputPortRequestFactory.build(decision=DecisionStatus.PENDING)],
        )
        assert port.active_grant is None

    def test_pending_request__returns_the_pending_request(self):
        pending = InputPortRequestFactory.build(decision=DecisionStatus.PENDING)
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED, valid_until=None, decided_by=None
                ),
                pending,
            ],
        )
        assert port.pending_request is pending

    def test_pending_request__none_when_no_pending(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED, valid_until=None, decided_by=None
                )
            ],
        )
        assert port.pending_request is None

    def test_recompute_status__active_permanent_grant_is_approved(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED, valid_until=None, decided_by=None
                )
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.APPROVED

    def test_recompute_status__active_grant_wins_over_pending_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=DecisionStatus.PENDING, created_on=NOW
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.APPROVED

    def test_recompute_status__pending_only_is_pending(self):
        port = InputPortFactory.build(
            request=False,
            requests=[InputPortRequestFactory.build(decision=DecisionStatus.PENDING)],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.PENDING

    def test_recompute_status__denied_only_is_denied(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.DENIED, decided_by=None
                )
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.DENIED

    def test_recompute_status__lapsed_grant_no_pending_is_denied_not_expired(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED,
                    valid_until=TODAY - timedelta(days=1),
                    decided_by=None,
                )
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.EXPIRED

    def test_recompute_status__active_grant_survives_denied_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=DecisionStatus.DENIED,
                    created_on=NOW,
                    decided_by=None,
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.APPROVED

    def test_renewal_status__first_time_pending_is_not_a_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[InputPortRequestFactory.build(decision=DecisionStatus.PENDING)],
        )
        assert port.renewal_status is None

    def test_renewal_status__first_time_denied_is_not_a_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.DENIED, decided_by=None
                )
            ],
        )
        assert port.renewal_status is None

    def test_renewal_status__active_grant_only_has_no_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED, valid_until=None, decided_by=None
                )
            ],
        )
        assert port.renewal_status is None

    def test_renewal_status__expired_grant_only_has_no_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED,
                    valid_until=TODAY - timedelta(days=1),
                    decided_by=None,
                )
            ],
        )
        assert port.renewal_status is None

    def test_renewal_status__pending_renewal_on_active_grant(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=DecisionStatus.PENDING, created_on=NOW
                ),
            ],
        )
        assert port.renewal_status == RenewalStatus.PENDING

    def test_renewal_status__denied_renewal_on_active_grant(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=DecisionStatus.DENIED, created_on=NOW, decided_by=None
                ),
            ],
        )
        assert port.renewal_status == RenewalStatus.DENIED

    def test_renewal_status__pending_renewal_after_expired_grant(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=DecisionStatus.APPROVED,
                    valid_until=TODAY - timedelta(days=1),
                    created_on=NOW - timedelta(days=10),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=DecisionStatus.PENDING, created_on=NOW
                ),
            ],
        )
        assert port.renewal_status == RenewalStatus.PENDING
