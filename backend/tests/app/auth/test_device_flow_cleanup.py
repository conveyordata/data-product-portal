import datetime

import pytz
from sqlalchemy import select

from app.core.auth.device_flows.model import DeviceFlow as DeviceFlowModel
from app.core.auth.device_flows.service import DeviceFlowService, utc_now
from app.core.auth.device_flows.schema import DeviceFlowStatus


def test_device_flow_cleanup_removes_expired(db_session):
    svc = DeviceFlowService()

    # Create expired records
    expired_time = utc_now() - datetime.timedelta(hours=1)
    for _ in range(3):
        df = DeviceFlowModel(
            client_id="test-client",
            scope="openid",
            max_expiry=expired_time,
            last_checked=expired_time,
            status=DeviceFlowStatus.EXPIRED,
        )
        db_session.add(df)
    db_session.commit()

    # Sanity: records exist
    pre = db_session.scalars(select(DeviceFlowModel)).all()
    assert len(pre) >= 3

    # Run cleanup
    svc.clean_device_flows(db_session)

    # Verify expired records removed
    post = db_session.scalars(select(DeviceFlowModel)).all()
    assert len(post) <= len(pre) - 3


def test_device_flow_cleanup_does_not_remove_active(db_session):
    svc = DeviceFlowService()

    # Create active record (not yet expired)
    future_time = utc_now() + datetime.timedelta(minutes=30)
    active = DeviceFlowModel(
        client_id="test-client",
        scope="openid",
        max_expiry=future_time,
        last_checked=utc_now(),
        status=DeviceFlowStatus.AUTHORIZATION_PENDING,
    )
    db_session.add(active)
    db_session.commit()

    svc.clean_device_flows(db_session)

    # Active record should remain
    remaining = db_session.scalars(select(DeviceFlowModel).where(DeviceFlowModel.device_code == active.device_code)).all()
    assert len(remaining) == 1
