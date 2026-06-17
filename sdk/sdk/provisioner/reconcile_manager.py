from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any
from uuid import UUID

from sdk.api_client.models import (
    AbstractDataProductType,
    ExplorationCreatedEvent,
    ExplorationDeletedEvent,
    ExplorationUpdatedEvent,
    InputPortCreatedEvent,
    InputPortDeletedEvent,
    InputPortUpdatedEvent,
)
from sdk.provisioner.event_handler import AbstractEventHandler
from sdk.provisioner.reconcile_queue import (
    DEFAULT_DELAY,
    DelayingDeduplicatingQueue,
    RateLimiter,
)

logger = logging.getLogger(__name__)

INITIAL_SYNC_MAX_BACKOFF: float = 60.0


class Reconciler(ABC):
    """Level-based reconciler.

    Implementations receive only the exploration id and are expected to re-fetch
    the current state of the exploration themselves, making reconciliation
    idempotent and resilient to coalesced events.
    """

    @abstractmethod
    async def reconcile(self, exploration_id: UUID):
        """Reconcile the exploration identified by ``exploration_id``.

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
    """Drives a :class:`Reconciler` from a :class:`DelayingDeduplicatingQueue`.

    Runs a pool of worker tasks that each loop ``get -> reconcile -> done``. A given
    exploration id is never reconciled by two workers concurrently (guaranteed by the
    queue's in-flight tracking). Failures and explicit requeues are retried with
    exponential backoff.
    """

    def __init__(
        self,
        reconciler: Reconciler,
        *,
        default_delay: float = DEFAULT_DELAY,
        num_workers: int = 1,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self._reconciler = reconciler
        self._queue = DelayingDeduplicatingQueue(default_delay=default_delay)
        self._rate_limiter = rate_limiter if rate_limiter else RateLimiter()
        self._workers: list[asyncio.Task[None]] = []
        self._initial_sync_task: asyncio.Task[None] | None = None
        if num_workers < 1:
            raise ValueError("num_workers must be >= 1")
        self._num_workers = num_workers

    @property
    def queue(self) -> DelayingDeduplicatingQueue:
        return self._queue

    async def enqueue(self, exploration_id: UUID) -> None:
        await self._queue.add(exploration_id)

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

        Retries listing with exponential backoff, giving up after
        ``initial_sync_max_attempts`` consecutive failures so a permanently broken
        listing (e.g. misconfigured auth) doesn't retry forever.
        """
        attempt = 0
        while True:
            try:
                ids = await self._reconciler.list_ids()
            except Exception:
                delay = min(2.0 ** (attempt - 1), INITIAL_SYNC_MAX_BACKOFF)
                logger.exception(
                    "Initial sync listing failed (attempt %d), retrying in %.1fs",
                    attempt,
                    delay,
                )
                await asyncio.sleep(delay)
                attempt += 1
                continue

            count = 0
            for resource_id in ids:
                await self._queue.add(resource_id, delay=0)
                count += 1
            logger.info("Initial sync enqueued %d resource(s)", count)
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

    async def _process(self, key: UUID) -> None:
        try:
            await self._reconciler.reconcile(key)
        except Exception:
            logger.exception("Reconcile failed for exploration %s", key)
            await self._requeue_with_backoff(key)
            return

        self._rate_limiter.forget(key)

    async def _requeue_with_backoff(self, key: UUID) -> None:
        delay = self._rate_limiter.when(key)
        await self._queue.add_after(key, delay)


class ReconcileEventHandler(AbstractEventHandler):
    """Webhook handler that enqueues a reconcile for each exploration event.

    Subclasses the generated :class:`~sdk.event_handler.AbstractEventHandler` and wires
    every ``exploration.created`` / ``exploration.updated`` / ``exploration.deleted``
    event to a :class:`ReconcileManager`, returning a fast "queued" acknowledgement so
    the webhook responds immediately while reconciliation happens asynchronously.
    """

    def __init__(self, manager: ReconcileManager) -> None:
        self._manager = manager

    @property
    def manager(self) -> ReconcileManager:
        return self._manager

    async def _enqueue(self, exploration_id: UUID) -> dict[str, Any]:
        await self._manager.enqueue(exploration_id)
        return {"status": "queued", "exploration_id": str(exploration_id)}

    async def on_exploration_created(
        self, data: ExplorationCreatedEvent
    ) -> dict[str, Any]:
        return await self._enqueue(data.id)

    async def on_exploration_updated(self, data: ExplorationUpdatedEvent) -> Any:
        return await self._enqueue(data.id)

    async def on_exploration_deleted(self, data: ExplorationDeletedEvent) -> Any:
        return await self._enqueue(data.id)

    async def on_input_port_updated(self, data: InputPortUpdatedEvent) -> Any:
        if (
            data.consuming_abstract_data_product_type
            == AbstractDataProductType.EXPLORATIONS
        ):
            return await self._enqueue(data.consuming_abstract_data_product_id)
        return None

    async def on_input_port_created(self, data: InputPortCreatedEvent) -> Any:
        if (
            data.consuming_abstract_data_product_type
            == AbstractDataProductType.EXPLORATIONS
        ):
            return await self._enqueue(data.consuming_abstract_data_product_id)
        return None

    async def on_input_port_deleted(self, data: InputPortDeletedEvent) -> Any:
        if (
            data.consuming_abstract_data_product_type
            == AbstractDataProductType.EXPLORATIONS
        ):
            return await self._enqueue(data.consuming_abstract_data_product_id)
        return None
