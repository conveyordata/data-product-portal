import uuid

from sdk.provisioner.reconcile_queue import (
    DEFAULT_DELAY,
    DelayingDeduplicatingQueue,
    RateLimiter,
)


def test_rate_limiter_backoff_progression():
    rl = RateLimiter(base_delay=1.0, max_delay=10.0, factor=2.0)
    key = uuid.uuid4()
    assert rl.when(key) == 1.0
    assert rl.when(key) == 2.0
    assert rl.when(key) == 4.0
    assert rl.when(key) == 8.0
    assert rl.when(key) == 10.0  # capped
    rl.forget(key)
    assert rl.when(key) == 1.0


def test_queue_default_delay():
    q = DelayingDeduplicatingQueue()
    assert q.default_delay == DEFAULT_DELAY
