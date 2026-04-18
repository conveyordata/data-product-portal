from contextlib import contextmanager

from app.settings import settings


@contextmanager
def webhook_v2_config(url: str | None = "http://test-v2.example.com/hook"):
    original = settings.WEBHOOK_V2_URL
    settings.WEBHOOK_V2_URL = url
    try:
        yield
    finally:
        settings.WEBHOOK_V2_URL = original
