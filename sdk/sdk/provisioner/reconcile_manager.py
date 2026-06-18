from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from sdk.api_client.models import (
    AbstractDataProductType,
    DataProductEvent,
    ExplorationEvent,
    InputPortEvent,
    OutputPortEvent,
    OutputPortTechnicalAssetLinkEvent,
    TechnicalAssetEvent,
)
from sdk.provisioner.event_handler import AbstractEventHandler
from sdk.provisioner.reconcile_queue import (
    DEFAULT_DELAY,
    DelayingDeduplicatingQueue,
    RateLimiter,
)

logger = logging.getLogger(__name__)

INITIAL_SYNC_MAX_BACKOFF: float = 60.0


class ResourceType(str, Enum):
    """The kinds of portal objects a reconciler can be registered for."""

    EXPLORATION = "exploration"
    DATA_PRODUCT = "data_product"


@dataclass(frozen=True)
class ReconcileKey:
    """A queue key identifying one instance of a resource to reconcile."""

    resource_type: ResourceType
    id: UUID


class Reconciler(ABC):
    """Level-based reconciler for a single resource type.

    Implementations receive only the resource id and are expected to re-fetch the
    current state of the resource themselves, making reconciliation idempotent and
    resilient to coalesced events.
    """

    @abstractmethod
    async def reconcile(self, resource_id: UUID):
        """Reconcile the resource identified by ``resource_id``.

        Return ``None`` on success. When an exception is raised, we will retry.
        """
        raise NotImplementedError

    async def list_ids(self) -> Iterable[UUID]:
        """Return the ids of every resource this reconciler is responsible for.

        Called once when the :class:`ReconcileManager` starts so that every existing
        resource is reconciled on startup, independent of any webhook events.
        Implementations are expected to fetch the current set of ids.

        The default returns an empty iterable, which disables the startup resync.
        """
        return []


class ReconcileManager:
    """Drives one or more :class:`Reconciler` from a shared work queue.

    Reconcilers are registered per :class:`ResourceType`. Runs a pool of worker tasks
    that each loop ``get -> dispatch -> done``; every queued key carries its resource
    type, so the manager hands it to the matching reconciler. A given key is never
    reconciled by two workers concurrently (guaranteed by the queue's in-flight
    tracking). Failures and explicit requeues are retried with exponential backoff.
    """

    def __init__(
        self,
        reconcilers: Mapping[ResourceType, Reconciler] | None = None,
        *,
        default_delay: float = DEFAULT_DELAY,
        num_workers: int = 1,
        rate_limiter: RateLimiter[ReconcileKey] | None = None,
    ) -> None:
        self._reconcilers: dict[ResourceType, Reconciler] = dict(reconcilers or {})
        self._queue: DelayingDeduplicatingQueue[ReconcileKey] = (
            DelayingDeduplicatingQueue[ReconcileKey](default_delay=default_delay)
        )

        self._rate_limiter = rate_limiter if rate_limiter else RateLimiter()
        self._workers: list[asyncio.Task[None]] = []
        self._initial_sync_task: asyncio.Task[None] | None = None
        if num_workers < 1:
            raise ValueError("num_workers must be >= 1")
        self._num_workers = num_workers

    @property
    def queue(self) -> DelayingDeduplicatingQueue[ReconcileKey]:
        return self._queue

    def has_reconciler(self, resource_type: ResourceType) -> bool:
        """Return whether a reconciler is registered for ``resource_type``."""
        return resource_type in self._reconcilers

    async def enqueue(self, resource_type: ResourceType, resource_id: UUID) -> None:
        await self._queue.add(ReconcileKey(resource_type, resource_id))

    def start(self) -> None:
        """This methods starts the reconciler and makes it active"""
        for i in range(self._num_workers):
            task = asyncio.create_task(
                self._worker_loop(), name=f"reconcile-worker-{i}"
            )
            self._workers.append(task)
        self._initial_sync_task = asyncio.create_task(
            self._initial_sync(), name="reconcile-initial-sync"
        )

    async def stop(self) -> None:
        """Gracefully shut the queue down and wait for workers to finish."""
        if self._initial_sync_task is not None:
            self._initial_sync_task.cancel()
            await asyncio.gather(self._initial_sync_task, return_exceptions=True)
            self._initial_sync_task = None
        await self._queue.shutdown()
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()

    async def _initial_sync(self) -> None:
        """Enqueue a reconcile for every existing resource when the manager starts.

        Each registered reconciler is listed in turn; listing is retried with
        exponential backoff so a transiently broken listing (e.g. the portal being
        briefly unavailable) doesn't drop the startup resync.
        """
        for resource_type, reconciler in self._reconcilers.items():
            await self._initial_sync_one(resource_type, reconciler)

    async def _initial_sync_one(
        self, resource_type: ResourceType, reconciler: Reconciler
    ) -> None:
        attempt = 0
        while True:
            try:
                ids = await reconciler.list_ids()
            except Exception:
                delay = min(2.0 ** (attempt - 1), INITIAL_SYNC_MAX_BACKOFF)
                logger.exception(
                    "Initial sync listing for %s failed (attempt %d), retrying in %.1fs",
                    resource_type.value,
                    attempt,
                    delay,
                )
                await asyncio.sleep(delay)
                attempt += 1
                continue

            count = 0
            for resource_id in ids:
                await self._queue.add(ReconcileKey(resource_type, resource_id), delay=0)
                count += 1
            logger.info(
                "Initial sync enqueued %d %s resource(s)", count, resource_type.value
            )
            return

    async def _worker_loop(self) -> None:
        while True:
            key = await self._queue.get()
            if key is None:
                return
            try:
                await self._process(key)
            finally:
                await self._queue.done(key)

    async def _process(self, key: ReconcileKey) -> None:
        reconciler = self._reconcilers.get(key.resource_type)
        if reconciler is None:
            return
        try:
            await reconciler.reconcile(key.id)
        except Exception:
            logger.exception(
                "Reconcile failed for %s %s", key.resource_type.value, key.id
            )
            await self._requeue_with_backoff(key)
            return

        self._rate_limiter.forget(key)

    async def _requeue_with_backoff(self, key: ReconcileKey) -> None:
        delay = self._rate_limiter.when(key)
        await self._queue.add_after(key, delay)


class ReconcileEventHandler(AbstractEventHandler):
    """Webhook handler that enqueues a reconcile for each supported portal event.

    Subclasses the generated :class:`~sdk.event_handler.AbstractEventHandler` and
    wires every ``created`` / ``updated`` / ``deleted`` event to a
    :class:`ReconcileManager`, routing each event to its :class:`ResourceType`. It
    returns a fast "queued" acknowledgement so the webhook responds immediately while
    reconciliation happens asynchronously. Events for a resource type without a
    registered reconciler are acknowledged as "ignored".
    """

    def __init__(self, manager: ReconcileManager) -> None:
        self._manager = manager

    @property
    def manager(self) -> ReconcileManager:
        return self._manager

    async def _enqueue(self, resource_type: ResourceType, resource_id: UUID):
        if not self._manager.has_reconciler(resource_type):
            logger.debug(f"No reconciler registered for '{resource_type.value}'")
            return
        await self._manager.enqueue(resource_type, resource_id)

    async def on_data_product_event(self, data: DataProductEvent):
        await self._enqueue(ResourceType.DATA_PRODUCT, data.id)

    async def on_exploration_event(self, data: ExplorationEvent):
        await self._enqueue(ResourceType.EXPLORATION, data.id)

    async def on_input_port_event(self, data: InputPortEvent):
        match data.consuming_abstract_data_product_type:
            case AbstractDataProductType.EXPLORATIONS:
                return await self._enqueue(
                    ResourceType.EXPLORATION, data.consuming_abstract_data_product_id
                )
            case AbstractDataProductType.DATA_PRODUCTS:
                return await self._enqueue(
                    ResourceType.DATA_PRODUCT, data.consuming_abstract_data_product_id
                )
        return None

    async def on_output_port_event(self, data: OutputPortEvent):
        await self._enqueue(ResourceType.DATA_PRODUCT, data.data_product_id)

    async def on_technical_asset_event(self, data: TechnicalAssetEvent):
        await self._enqueue(ResourceType.DATA_PRODUCT, data.data_product_id)

    async def on_output_port_technical_asset_link_event(
        self, data: OutputPortTechnicalAssetLinkEvent
    ):
        await self._enqueue(ResourceType.DATA_PRODUCT, data.data_product_id)
