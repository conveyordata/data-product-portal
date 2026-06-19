import asyncio
import json
import uuid
from typing import Any

from fastapi import Request
from fastapi.datastructures import Headers

from sdk.provisioner.reconcile_manager import (
    ReconcileEventHandler,
    ReconcileManager,
    Reconciler,
    ResourceType,
)
from sdk.provisioner.reconcile_queue import (
    RateLimiter,
)


class RecordingReconciler(Reconciler):
    """Reconciler that records every call and supports per-key behaviour overrides."""

    def __init__(self) -> None:
        self.calls: list[uuid.UUID] = []
        self.in_flight: set[uuid.UUID] = set()
        self.max_concurrent_same_key = 0
        self.fail_times: dict[uuid.UUID, int] = {}
        self.delay: float = 0.0
        self.ids_to_list: list[uuid.UUID] = []
        self.list_ids_calls = 0
        self.list_ids_fail_times = 0
        self._lock = asyncio.Lock()

    async def list_ids(self):
        self.list_ids_calls += 1
        if self.list_ids_fail_times > 0:
            self.list_ids_fail_times -= 1
            raise RuntimeError("list boom")
        return list(self.ids_to_list)

    async def reconcile(self, resource_id: uuid.UUID):
        async with self._lock:
            self.calls.append(resource_id)
            if resource_id in self.in_flight:
                self.max_concurrent_same_key = max(self.max_concurrent_same_key, 2)
            self.in_flight.add(resource_id)
        try:
            if self.delay:
                await asyncio.sleep(self.delay)
            remaining = self.fail_times.get(resource_id, 0)
            if remaining > 0:
                self.fail_times[resource_id] = remaining - 1
                raise RuntimeError("boom")
            return None
        finally:
            async with self._lock:
                self.in_flight.discard(resource_id)


def _manager(reconciler: Reconciler, **kwargs) -> ReconcileManager:
    """Build a manager with ``reconciler`` registered for the exploration type."""
    return ReconcileManager({ResourceType.EXPLORATION: reconciler}, **kwargs)


async def _enqueue(manager: ReconcileManager, key: uuid.UUID) -> None:
    await manager.enqueue(ResourceType.EXPLORATION, key)


async def _drain(reconciler: RecordingReconciler, expected: int, timeout: float = 2.0):
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while len(reconciler.calls) < expected:
        if loop.time() > deadline:
            break
        await asyncio.sleep(0.01)


async def test_coalesces_duplicate_events():
    reconciler = RecordingReconciler()
    manager = _manager(reconciler, num_workers=2, default_delay=0.1)
    manager.start()
    key = uuid.uuid4()

    await _enqueue(manager, key)
    await _enqueue(manager, key)
    await _enqueue(manager, key)

    await _drain(reconciler, expected=1)
    await asyncio.sleep(0.2)
    await manager.stop()

    assert reconciler.calls.count(key) == 1


async def test_debounce_delay_applies():
    reconciler = RecordingReconciler()
    manager = _manager(reconciler, default_delay=0.3)
    manager.start()
    key = uuid.uuid4()

    await _enqueue(manager, key)
    await asyncio.sleep(0.1)
    assert reconciler.calls == []  # not yet eligible

    await _drain(reconciler, expected=1)
    await manager.stop()
    assert reconciler.calls == [key]


async def test_re_dirty_during_processing_reconciles_once_more():
    reconciler = RecordingReconciler()
    reconciler.delay = 0.2
    manager = _manager(reconciler, default_delay=0.2)
    manager.start()
    key = uuid.uuid4()

    await _enqueue(manager, key)
    # Wait until the reconcile is in flight, then enqueue again twice.
    while key not in reconciler.in_flight:
        await asyncio.sleep(0.005)
    await _enqueue(manager, key)
    await _enqueue(manager, key)

    await _drain(reconciler, expected=2)
    await asyncio.sleep(0.1)
    await manager.stop()

    assert reconciler.calls.count(key) == 2


async def test_same_key_never_processed_concurrently():
    reconciler = RecordingReconciler()
    reconciler.delay = 0.15
    manager = _manager(reconciler, default_delay=0.0, num_workers=4)
    manager.start()
    key = uuid.uuid4()

    await _enqueue(manager, key)
    while key not in reconciler.in_flight:
        await asyncio.sleep(0.005)
    await _enqueue(manager, key)

    await _drain(reconciler, expected=2)
    await asyncio.sleep(0.1)
    await manager.stop()

    assert reconciler.max_concurrent_same_key == 0


async def test_different_keys_processed_in_parallel():
    reconciler = RecordingReconciler()
    reconciler.delay = 0.2
    manager = _manager(reconciler, default_delay=0.0, num_workers=2)
    manager.start()
    k1, k2 = uuid.uuid4(), uuid.uuid4()

    loop = asyncio.get_running_loop()
    start = loop.time()
    await _enqueue(manager, k1)
    await _enqueue(manager, k2)
    await _drain(reconciler, expected=2)
    elapsed = loop.time() - start
    await manager.stop()

    # If serialized this would take ~0.4s; in parallel ~0.2s.
    assert elapsed < 0.35
    assert set(reconciler.calls) == {k1, k2}


async def test_initial_sync_enqueues_all_listed_ids():
    reconciler = RecordingReconciler()
    ids = [uuid.uuid4() for _ in range(3)]
    reconciler.ids_to_list = ids
    manager = _manager(reconciler, default_delay=0.0, num_workers=2)
    manager.start()

    await _drain(reconciler, expected=len(ids))
    await asyncio.sleep(0.1)
    await manager.stop()

    assert set(reconciler.calls) == set(ids)
    assert len(reconciler.calls) == len(ids)


async def test_no_initial_sync_without_listed_ids():
    reconciler = RecordingReconciler()
    manager = _manager(reconciler, default_delay=0.0, num_workers=1)
    manager.start()

    await asyncio.sleep(0.1)
    await manager.stop()

    assert reconciler.calls == []


async def test_initial_sync_retries_listing_then_succeeds():
    reconciler = RecordingReconciler()
    ids = [uuid.uuid4()]
    reconciler.ids_to_list = ids
    reconciler.list_ids_fail_times = 1
    # Use base_delay so the backoff (2**0 = 1s capped by max_delay) stays short.
    manager = _manager(reconciler, default_delay=0.0, num_workers=1)
    # Shrink the backoff by monkeypatching the cap is overkill; instead rely on the
    # first retry delay being 2**0 = 1.0s, so allow enough time below.
    manager.start()

    await _drain(reconciler, expected=1, timeout=3.0)
    await asyncio.sleep(0.1)
    await manager.stop()

    assert reconciler.list_ids_calls == 2
    assert set(reconciler.calls) == set(ids)


async def test_failure_requeues_with_backoff_then_succeeds():
    reconciler = RecordingReconciler()
    key = uuid.uuid4()
    reconciler.fail_times[key] = 2
    rate_limiter = RateLimiter(base_delay=0.05, max_delay=10, factor=2.0)
    manager = _manager(
        reconciler, default_delay=0.0, rate_limiter=rate_limiter, num_workers=1
    )
    manager.start()

    await _enqueue(manager, key)
    await _drain(reconciler, expected=3, timeout=3.0)
    await asyncio.sleep(0.1)
    await manager.stop()

    assert reconciler.calls.count(key) == 3


async def test_manager_dispatches_to_correct_reconciler():
    exploration = RecordingReconciler()
    data_product = RecordingReconciler()
    manager = ReconcileManager(
        {
            ResourceType.EXPLORATION: exploration,
            ResourceType.DATA_PRODUCT: data_product,
        },
        default_delay=0.0,
        num_workers=2,
    )
    manager.start()

    exp_id = uuid.uuid4()
    dp_id = uuid.uuid4()
    await manager.enqueue(ResourceType.EXPLORATION, exp_id)
    await manager.enqueue(ResourceType.DATA_PRODUCT, dp_id)

    await _drain(exploration, expected=1)
    await _drain(data_product, expected=1)
    await manager.stop()

    assert exploration.calls == [exp_id]
    assert data_product.calls == [dp_id]


async def test_same_id_different_types_do_not_collide():
    exploration = RecordingReconciler()
    data_product = RecordingReconciler()
    manager = ReconcileManager(
        {
            ResourceType.EXPLORATION: exploration,
            ResourceType.DATA_PRODUCT: data_product,
        },
        default_delay=0.0,
        num_workers=2,
    )
    manager.start()

    shared_id = uuid.uuid4()
    await manager.enqueue(ResourceType.EXPLORATION, shared_id)
    await manager.enqueue(ResourceType.DATA_PRODUCT, shared_id)

    await _drain(exploration, expected=1)
    await _drain(data_product, expected=1)
    await manager.stop()

    assert exploration.calls == [shared_id]
    assert data_product.calls == [shared_id]


def _build_request(envelope: dict[str, Any]) -> Request:
    async def receive() -> dict[str, Any]:
        return {
            "type": "http.request",
            "body": json.dumps(envelope).encode(),
            "more_body": False,
        }

    return Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/webhook",
            "headers": Headers().raw,
        },
        receive=receive,
    )


def _envelope(event_type: str, resource_id: uuid.UUID) -> dict[str, Any]:
    return {
        "specversion": "1.0",
        "id": str(uuid.uuid4()),
        "source": "data-product-portal",
        "type": event_type,
        "time": "2026-06-17T00:00:00Z",
        "data": {
            "id": str(resource_id),
        },
    }


async def test_event_handler_enqueues_exploration():
    reconciler = RecordingReconciler()
    manager = _manager(reconciler, default_delay=0.0, num_workers=1)
    manager.start()
    handler = ReconcileEventHandler(manager)
    exploration_id = uuid.uuid4()

    await handler.dispatch_routing(
        _build_request(_envelope("exploration.event", exploration_id))
    )

    await _drain(reconciler, expected=1)
    await manager.stop()
    assert reconciler.calls == [exploration_id]


async def test_event_handler_enqueues_data_product():
    reconciler = RecordingReconciler()
    manager = ReconcileManager(
        {ResourceType.DATA_PRODUCT: reconciler}, default_delay=0.0, num_workers=1
    )
    manager.start()
    handler = ReconcileEventHandler(manager)
    data_product_id = uuid.uuid4()

    await handler.dispatch_routing(
        _build_request(_envelope("data_product.event", data_product_id))
    )

    await _drain(reconciler, expected=1)
    await manager.stop()
    assert reconciler.calls == [data_product_id]


async def test_event_handler_ignores_unregistered_resource_type():
    # Only an exploration reconciler is registered; data product events are ignored.
    reconciler = RecordingReconciler()
    manager = _manager(reconciler, default_delay=0.0, num_workers=1)
    manager.start()
    handler = ReconcileEventHandler(manager)

    await handler.dispatch_routing(
        _build_request(_envelope("data_product.created", uuid.uuid4()))
    )
    assert manager.queue.qsize() == 0
    await manager.stop()
