import datetime

import pytz
from sqlalchemy import select

from app.core.auth.device_flows.background_tasks import cleanup_device_flow_table
from app.core.auth.device_flows.model import DeviceFlow as DeviceFlowModel
from app.core.auth.device_flows.schema import DeviceFlowStatus


def test_device_flow_cleanup_removes_expired(session):
    expired_time = datetime.datetime.now(tz=pytz.utc).replace(
        tzinfo=None
    ) - datetime.timedelta(hours=24)
    for _ in range(3):
        df = DeviceFlowModel(
            client_id="test-client",
            scope="openid",
            max_expiry=expired_time,
            last_checked=expired_time,
            status=DeviceFlowStatus.EXPIRED,
        )
        session.add(df)
    session.flush()
    pre = session.scalars(select(DeviceFlowModel)).all()
    assert len(pre) >= 3

    cleanup_device_flow_table(session)

    post = session.scalars(select(DeviceFlowModel)).all()
    assert len(post) == len(pre) - 3


def test_device_flow_cleanup_does_not_remove_active(session):
    now = datetime.datetime.now(tz=pytz.utc).replace(tzinfo=None)
    future_expiry_time = now + datetime.timedelta(minutes=30)
    active = DeviceFlowModel(
        client_id="test-client",
        scope="openid",
        max_expiry=future_expiry_time,
        last_checked=now,
        status=DeviceFlowStatus.AUTHORIZATION_PENDING,
    )
    session.add(active)
    session.flush()

    cleanup_device_flow_table(session)

    remaining = session.scalars(
        select(DeviceFlowModel).where(DeviceFlowModel.device_code == active.device_code)
    ).all()
    assert len(remaining) == 1
