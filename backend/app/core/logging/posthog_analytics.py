from typing import Optional

from posthog import Posthog

from app.settings import settings

posthog_client = None
if settings.POSTHOG_ENABLED:
    posthog_client = Posthog(
        project_api_key=settings.POSTHOG_API_KEY, host=settings.POSTHOG_HOST
    )


def get_posthog_client() -> Optional[Posthog]:
    return posthog_client
