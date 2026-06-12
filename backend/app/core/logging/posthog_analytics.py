import asyncio
from datetime import datetime, timedelta
from typing import Optional

import pytz
from posthog import Posthog
from sqlalchemy import func, select

from app.abstract_data_product.model import AbstractDataProduct, AbstractDataProductType
from app.authorization.role_assignments.enums import DecisionStatus

_ADP_TYPE_DISPLAY_NAME: dict[AbstractDataProductType, str] = {
    AbstractDataProductType.DATA_PRODUCT: "data_product",
    AbstractDataProductType.EXPLORATION: "exploration",
}
from app.core.logging import logger
from app.data_products.output_ports.input_ports.model import InputPort as InputPortModel
from app.database.database import SessionLocal
from app.settings import settings

posthog_client = None
if settings.POSTHOG_ENABLED:
    posthog_client = Posthog(
        project_api_key=settings.POSTHOG_API_KEY, host=settings.POSTHOG_HOST
    )


def get_posthog_client() -> Optional[Posthog]:
    return posthog_client


def _seconds_until_next_midnight_utc() -> float:
    now = datetime.now(tz=pytz.utc)
    next_midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    next_midnight = now + timedelta(seconds=10)
    return (next_midnight - now).total_seconds()


async def report_consumption_metrics_task() -> None:
    """
    Daily background task that reports the total number of approved input ports
    to PostHog as a consumption metric, broken down by ADP type. Fires once at
    midnight UTC regardless of how many times the app restarts during the day.

    Consumption (approved input ports) is a key success metric for the portal —
    it measures how actively data products are being used by other teams.
    """
    while True:
        await asyncio.sleep(_seconds_until_next_midnight_utc())
        try:
            posthog = get_posthog_client()
            if not posthog:
                continue

            with SessionLocal() as db:
                rows = db.execute(
                    select(
                        AbstractDataProduct.abstract_data_product_type,
                        func.count(InputPortModel.id),
                    )
                    .join(
                        AbstractDataProduct,
                        InputPortModel.consuming_abstract_data_product_id
                        == AbstractDataProduct.id,
                    )
                    .where(InputPortModel.status == DecisionStatus.APPROVED)
                    .group_by(AbstractDataProduct.abstract_data_product_type)
                ).all()

            counts_by_type = {adp_type.value: count for adp_type, count in rows}
            total = sum(counts_by_type.values())

            logger.info(
                f"Reporting daily consumption metric: {total} approved input ports"
                f" ({counts_by_type})"
            )
            posthog.capture(
                distinct_id="system",
                event="Daily Consumption Metrics",
                properties={
                    "total_approved_input_ports": total,
                    **{
                        f"approved_input_ports_{adp_type}": count
                        for adp_type, count in counts_by_type.items()
                    },
                },
            )
        except Exception as e:
            logger.warning(f"Failed to report daily consumption metrics: {e}")
