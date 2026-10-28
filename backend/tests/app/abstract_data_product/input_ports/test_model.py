from datetime import date, datetime, timedelta

import pytz

from app.abstract_data_product.input_ports.enums import (
    InputPortRequestDecision,
    InputPortStatus,
    RenewalStatus,
)
from tests.factories import InputPortFactory, InputPortRequestFactory

TODAY = date.today()
NOW = datetime.now(pytz.utc)


class TestInputPortModel:
    def test_active_grant__permanent_grant(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    decided_by=None,
                )
            ],
        )
        assert port.active_grant.valid_until is None

    def test_active_grant__time_bound_grant_covering_today(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    decided_by=None,
                )
            ],
        )
        assert port.active_grant.valid_until == TODAY + timedelta(days=10)

    def test_active_grant__ignores_historical_ended_grant(self):
        ended = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.APPROVED,
            valid_until=TODAY - timedelta(days=1),
            created_on=NOW - timedelta(days=10),
            decided_by=None,
        )
        active = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.APPROVED,
            valid_until=TODAY + timedelta(days=10),
            created_on=NOW,
            decided_by=None,
        )
        port = InputPortFactory.build(request=False, requests=[ended, active])
        assert port.active_grant is active

    def test_active_grant__2_active_grants_returns_latest(self):
        active_old = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.APPROVED,
            valid_until=TODAY + timedelta(days=1),
            created_on=NOW - timedelta(days=10),
            decided_by=None,
        )
        active_new = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.APPROVED,
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
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY - timedelta(days=1),
                    decided_by=None,
                )
            ],
        )
        assert port.active_grant is None

    def test_active_grant__excludes_revoked_grant(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    decided_by=None,
                    revoked_at=NOW,
                    revoked_by=None,
                )
            ],
        )
        assert port.active_grant is None

    def test_active_grant__none_when_no_approved(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(decision=InputPortRequestDecision.PENDING)
            ],
        )
        assert port.active_grant is None

    def test_pending_request__returns_the_pending_request(self):
        pending = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.PENDING
        )
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    decided_by=None,
                ),
                pending,
            ],
        )
        assert port.pending_request is pending

    def test_pending_request__excludes_cancelled_request(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.CANCELLED,
                )
            ],
        )
        assert port.pending_request is None

    def test_pending_request__none_when_no_pending(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    decided_by=None,
                )
            ],
        )
        assert port.pending_request is None

    def test_recompute_status__active_permanent_grant_is_approved(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    decided_by=None,
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
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.PENDING, created_on=NOW
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.APPROVED

    def test_recompute_status__pending_only_is_pending(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(decision=InputPortRequestDecision.PENDING)
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.PENDING

    def test_recompute_status__cancelled_pending_is_cancelled(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.CANCELLED,
                )
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.CANCELLED

    def test_recompute_status__pending_renewal_after_expiry_stays_expired(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY - timedelta(days=1),
                    created_on=NOW - timedelta(days=10),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.PENDING,
                    created_on=NOW,
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.EXPIRED

    def test_recompute_status__pending_request_after_revoke_stays_revoked(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    created_on=NOW - timedelta(days=10),
                    decided_by=None,
                    revoked_at=NOW - timedelta(days=5),
                    revoked_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.PENDING,
                    created_on=NOW,
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.REVOKED

    def test_recompute_status__pending_reask_after_denial_is_pending(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.DENIED,
                    created_on=NOW - timedelta(days=10),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.PENDING,
                    created_on=NOW,
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.PENDING

    def test_recompute_status__cancelled_renewal_falls_back_to_expired(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY - timedelta(days=1),
                    created_on=NOW - timedelta(days=10),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.CANCELLED,
                    created_on=NOW,
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.EXPIRED

    def test_recompute_status__cancelled_renewal_falls_back_to_revoked(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    created_on=NOW - timedelta(days=10),
                    decided_by=None,
                    revoked_at=NOW - timedelta(days=5),
                    revoked_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.CANCELLED,
                    created_on=NOW,
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.REVOKED

    def test_recompute_status__cancelled_renewal_falls_back_to_denied(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.DENIED,
                    created_on=NOW - timedelta(days=10),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.CANCELLED,
                    created_on=NOW,
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.DENIED

    def test_recompute_status__active_grant_survives_cancelled_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.CANCELLED,
                    created_on=NOW,
                ),
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.APPROVED

    def test_recompute_status__denied_only_is_denied(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.DENIED, decided_by=None
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
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY - timedelta(days=1),
                    decided_by=None,
                )
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.EXPIRED

    def test_recompute_status__revoked_grant_no_pending_is_revoked(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    decided_by=None,
                    revoked_at=NOW,
                    revoked_by=None,
                )
            ],
        )
        port.recompute_status()
        assert port.status == InputPortStatus.REVOKED

    def test_recompute_status__active_grant_survives_denied_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.DENIED,
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
            requests=[
                InputPortRequestFactory.build(decision=InputPortRequestDecision.PENDING)
            ],
        )
        assert port.renewal_status is None

    def test_renewal_status__first_time_denied_is_not_a_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.DENIED, decided_by=None
                )
            ],
        )
        assert port.renewal_status is None

    def test_renewal_status__active_grant_only_has_no_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    decided_by=None,
                )
            ],
        )
        assert port.renewal_status is None

    def test_renewal_status__expired_grant_only_has_no_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
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
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.PENDING, created_on=NOW
                ),
            ],
        )
        assert port.renewal_status == RenewalStatus.PENDING

    def test_renewal_status__cancelled_renewal_on_active_grant_has_no_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.CANCELLED,
                    created_on=NOW,
                ),
            ],
        )
        assert port.renewal_status is None

    def test_renewal_status__denied_renewal_on_active_grant(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY + timedelta(days=10),
                    created_on=NOW - timedelta(days=1),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.DENIED,
                    created_on=NOW,
                    decided_by=None,
                ),
            ],
        )
        assert port.renewal_status == RenewalStatus.DENIED

    def test_renewal_status__revoked_grant_only_has_no_renewal(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=None,
                    decided_by=None,
                    revoked_at=NOW,
                    revoked_by=None,
                )
            ],
        )
        assert port.renewal_status is None

    def test_renewal_status__pending_renewal_after_expired_grant(self):
        port = InputPortFactory.build(
            request=False,
            requests=[
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.APPROVED,
                    valid_until=TODAY - timedelta(days=1),
                    created_on=NOW - timedelta(days=10),
                    decided_by=None,
                ),
                InputPortRequestFactory.build(
                    decision=InputPortRequestDecision.PENDING, created_on=NOW
                ),
            ],
        )
        assert port.renewal_status == RenewalStatus.PENDING

    def test_current_request__active_grant_wins_over_pending_renewal(self):
        active = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.APPROVED,
            valid_until=TODAY + timedelta(days=10),
            created_on=NOW - timedelta(days=1),
            decided_by=None,
        )
        renewal = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.PENDING, created_on=NOW
        )
        port = InputPortFactory.build(request=False, requests=[active, renewal])
        assert port.current_request is active

    def test_current_request__fresh_pending_request_returns_itself(self):
        pending = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.PENDING
        )
        port = InputPortFactory.build(request=False, requests=[pending])
        assert port.current_request is pending

    def test_current_request__pending_renewal_after_expiry_returns_expired_grant(self):
        expired = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.APPROVED,
            valid_until=TODAY - timedelta(days=1),
            created_on=NOW - timedelta(days=10),
            decided_by=None,
        )
        renewal = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.PENDING, created_on=NOW
        )
        port = InputPortFactory.build(request=False, requests=[expired, renewal])
        assert port.current_request is expired

    def test_current_request__pending_request_after_revoke_returns_revoked_grant(self):
        revoked = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.APPROVED,
            valid_until=None,
            created_on=NOW - timedelta(days=10),
            decided_by=None,
            revoked_at=NOW - timedelta(days=5),
            revoked_by=None,
        )
        renewal = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.PENDING, created_on=NOW
        )
        port = InputPortFactory.build(request=False, requests=[revoked, renewal])
        assert port.current_request is revoked

    def test_current_request__pending_reask_after_initial_denial_returns_itself(self):
        denied = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.DENIED,
            created_on=NOW - timedelta(days=10),
            decided_by=None,
        )
        reask = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.PENDING, created_on=NOW
        )
        port = InputPortFactory.build(request=False, requests=[denied, reask])
        assert port.current_request is reask

    def test_current_request__cancelled_renewal_returns_prior_expired_grant(self):
        expired = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.APPROVED,
            valid_until=TODAY - timedelta(days=1),
            created_on=NOW - timedelta(days=10),
            decided_by=None,
        )
        cancelled = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.CANCELLED, created_on=NOW
        )
        port = InputPortFactory.build(request=False, requests=[expired, cancelled])
        assert port.current_request is expired

    def test_current_request__all_cancelled_falls_back_to_latest(self):
        first = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.CANCELLED,
            created_on=NOW - timedelta(days=1),
        )
        second = InputPortRequestFactory.build(
            decision=InputPortRequestDecision.CANCELLED, created_on=NOW
        )
        port = InputPortFactory.build(request=False, requests=[first, second])
        assert port.current_request is second
