"""Kubernetes-operator-style reconcile primitives for exploration events.

This module provides a small, dependency-free (pure asyncio) toolkit for building
operator-like reconcile loops on top of the generated webhook event handler:

- :class:`DelayingDeduplicatingQueue` -- a work queue keyed by exploration id that
  coalesces duplicate enqueues, applies a debounce delay before a key becomes
  eligible for processing, and guarantees a key is only handed to one worker at a
  time. A key re-enqueued while it is being processed is reconciled exactly once
  more afterwards (no lost events).
- :class:`RateLimiter` -- exponential backoff used to requeue keys after a failed
  or explicitly retried reconcile.
- :class:`Reconciler` -- abstract, level-based reconciler: it receives only the
  exploration id and is expected to re-fetch current state itself.
- :class:`ReconcileManager` -- runs a pool of workers that pull keys off the queue
  and invoke the reconciler, requeuing with backoff on failure.
- :class:`ReconcileEventHandler` -- a ready-to-use subclass of the generated
  ``AbstractEventHandler`` that enqueues the exploration id on every created,
  updated or deleted webhook.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from uuid import UUID

logger = logging.getLogger(__name__)

# Default debounce applied before an enqueued key becomes eligible for processing.
DEFAULT_DELAY: float = 15.0


class RateLimiter:
    """Per-key exponential backoff helper.

    Each failed attempt for a key increases the delay returned by :meth:`when`,
    capped at ``max_delay``. Call :meth:`forget` once a key reconciles successfully
    to reset its backoff.
    """

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        factor: float = 2.0,
    ) -> None:
        if base_delay <= 0:
            raise ValueError("base_delay must be > 0")
        if factor <= 1:
            raise ValueError("factor must be > 1")
        self._base_delay = base_delay
        if max_delay < 10:
            raise ValueError("max_delay must be >= 10")
        self._max_delay = max_delay
        self._factor = factor
        self._failures: dict[UUID, int] = {}

    def when(self, key: UUID) -> float:
        """Record a failure for ``key`` and return the delay before the next retry."""
        failures = self._failures.get(key, 0)
        self._failures[key] = failures + 1
        delay = self._base_delay * (self._factor**failures)
        return min(delay, self._max_delay)

    def failures(self, key: UUID) -> int:
        """Return how many consecutive failures have been recorded for ``key``."""
        return self._failures.get(key, 0)

    def forget(self, key: UUID) -> None:
        """Reset the backoff state for ``key`` (call on success)."""
        self._failures.pop(key, None)


class DelayingDeduplicatingQueue:
    """An asyncio work queue keyed by :class:`~uuid.UUID`.

    Semantics mirror a Kubernetes ``client-go`` delaying + deduplicating workqueue:

    - **Deduplication / coalescing**: adding a key that is already waiting is a
      no-op beyond (optionally) shortening its ready time. Two events for the same
      exploration therefore result in a single reconcile.
    - **Delay**: ``add`` schedules the key to become eligible after ``delay`` seconds.
    - **Single in-flight per key**: :meth:`get` marks a key as "processing"; it will
      not be returned again until :meth:`done` is called for it. If the key is added
      again while processing, it is remembered as "dirty" and re-queued immediately
      once :meth:`done` runs.
    """

    def __init__(self, default_delay: float = DEFAULT_DELAY) -> None:
        self._default_delay = default_delay
        # key -> time at which the key becomes eligible for processing.
        self._waiting: dict[UUID, float] = {}
        # keys currently handed out to a worker (in flight).
        self._processing: set[UUID] = set()
        # keys re-added while in flight; re-queued on done().
        self._dirty: set[UUID] = set()
        self._cond = asyncio.Condition()
        self._shutdown = False

    @property
    def default_delay(self) -> float:
        return self._default_delay

    async def add(self, key: UUID, delay: float | None = None) -> None:
        """Enqueue ``key`` to be processed after ``delay`` seconds (debounced)."""
        if delay is None:
            delay = self._default_delay
        ready_at = time.monotonic() + max(delay, 0.0)
        async with self._cond:
            if self._shutdown:
                return
            if key in self._processing:
                # Will be re-queued when the in-flight reconcile finishes.
                self._dirty.add(key)
                return
            existing = self._waiting.get(key)
            # Coalesce: keep the earliest ready time so an explicit shorter delay wins.
            if existing is None or ready_at < existing:
                self._waiting[key] = ready_at
            self._cond.notify_all()

    async def add_after(self, key: UUID, delay: float) -> None:
        """Explicit delayed add; alias for :meth:`add` used by retry/backoff paths."""
        await self.add(key, delay)

    async def get(self) -> UUID | None:
        """Block until a waiting key is eligible and return it (marked in flight).

        Returns ``None`` once the queue has been shut down and drained.
        """
        async with self._cond:
            while True:
                if self._shutdown and not self._waiting:
                    return None

                now = time.monotonic()
                ready_key: UUID | None = None
                next_ready: float | None = None
                for candidate, ready_at in self._waiting.items():
                    if ready_at <= now:
                        if ready_key is None or ready_at < self._waiting[ready_key]:
                            ready_key = candidate
                    else:
                        next_ready = (
                            ready_at
                            if next_ready is None
                            else min(next_ready, ready_at)
                        )

                if ready_key is not None:
                    del self._waiting[ready_key]
                    self._processing.add(ready_key)
                    return ready_key

                # Nothing ready yet: wait until the next ready time or a new add.
                if next_ready is not None:
                    timeout = max(next_ready - time.monotonic(), 0.0)
                    try:
                        await asyncio.wait_for(self._cond.wait(), timeout=timeout)
                    except asyncio.TimeoutError:
                        pass
                else:
                    await self._cond.wait()

    async def done(self, key: UUID) -> None:
        """Mark an in-flight ``key`` as finished.

        If the key was re-added while in flight it is immediately re-queued.
        """
        async with self._cond:
            self._processing.discard(key)
            if key in self._dirty:
                self._dirty.discard(key)
                if key not in self._waiting:
                    self._waiting[key] = time.monotonic()
                self._cond.notify_all()

    async def shutdown(self) -> None:
        """Stop the queue and wake up all waiting workers."""
        async with self._cond:
            self._shutdown = True
            self._cond.notify_all()

    def qsize(self) -> int:
        """Number of keys currently waiting (not counting in-flight keys)."""
        return len(self._waiting)
