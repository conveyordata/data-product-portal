import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional

import pytz
from posthog import Posthog
from sqlalchemy import func, select

from app.abstract_data_product.input_ports.model import InputPort as InputPortModel
from app.abstract_data_product.model import AbstractDataProduct
from app.authorization.role_assignments.enums import DecisionStatus
from app.core.logging import logger
from app.database.database import SessionLocal
from app.settings import settings


def get_posthog_client() -> Optional[Posthog]:
    if settings.POSTHOG_ENABLED:
        return Posthog(
            project_api_key=settings.POSTHOG_API_KEY,
            host=settings.POSTHOG_HOST,
            super_properties={"host": settings.HOST},
        )
    return None


def _seconds_until_next_midnight_utc() -> float:
    now = datetime.now(tz=pytz.utc)
    next_midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return (next_midnight - now).total_seconds()


def consumption_metrics() -> dict[str, Any]:
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
            .group_by(AbstractDataProduct.abstract_data_product_type),
            execution_options={"skip_data_product_visibility_filter": True},
        ).all()

    counts_by_type = {adp_type.value: count for adp_type, count in rows}
    total = sum(counts_by_type.values())
    return {
        "total_approved_input_ports": total,
        **{
            f"approved_input_ports_{adp_type}": count
            for adp_type, count in counts_by_type.items()
        },
    }


def provisioning_metrics() -> dict[str, Any]:
    with SessionLocal() as db:
        rows = db.execute(
            select(
                AbstractDataProduct.abstract_data_product_type,
                func.count(AbstractDataProduct.id),
                func.count(AbstractDataProduct.id).filter(
                    func.cardinality(AbstractDataProduct.finalizers) > 0
                ),
            ).group_by(AbstractDataProduct.abstract_data_product_type),
            execution_options={"skip_data_product_visibility_filter": True},
        ).all()

    counts_by_type = {
        adp_type.value: {
            "total": total_count,
            "with_finalizers": with_finalizers_count,
        }
        for adp_type, total_count, with_finalizers_count in rows
    }

    return {
        **{
            f"provisioned_{adp_type}": counts["with_finalizers"]
            for adp_type, counts in counts_by_type.items()
        },
        **{
            f"total_{adp_type}": counts["total"]
            for adp_type, counts in counts_by_type.items()
        },
    }


def _do_report_daily_metrics(posthog: Posthog) -> None:
    consumption = consumption_metrics()
    provisioning = provisioning_metrics()
    properties = {
        **consumption,
        **provisioning,
    }
    logger.info(f"Reporting metrics to posthog: {properties}")
    posthog.capture(
        distinct_id="system",
        event="Daily Consumption Metrics",
        properties=properties,
    )


async def report_daily_metrics() -> None:
    """
    Daily background task that reports metrics to the Data Product Portal team.
    """
    posthog = get_posthog_client()
    if not posthog:
        return
    while True:
        await asyncio.sleep(_seconds_until_next_midnight_utc())
        try:
            _do_report_daily_metrics(posthog)
        except Exception as e:
            logger.warning(f"Failed to report daily metrics: {e}")
        await asyncio.sleep(1)
