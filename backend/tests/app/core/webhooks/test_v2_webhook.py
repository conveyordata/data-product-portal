from unittest.mock import AsyncMock, MagicMock, patch

from tests.app.core.webhooks.helpers import webhook_v2_config


class TestCallV2Webhook:
    def test_posts_cloudevents_envelope(self):
        """call_v2_webhook sends a CloudEvents-shaped body."""
        import asyncio

        from app.core.webhooks.v2 import call_v2_webhook

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post = AsyncMock(return_value=mock_response)

        with webhook_v2_config(), patch("httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.post = mock_post
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            asyncio.get_event_loop().run_until_complete(
                call_v2_webhook("data_product.created", {"data_product": {"id": "abc"}})
            )

        mock_post.assert_awaited_once()
        body = mock_post.call_args.kwargs["json"]
        assert body["specversion"] == "1.0"
        assert body["type"] == "data_product.created"
        assert body["source"] == "data-product-portal"
        assert "id" in body
        assert "time" in body
        assert body["data"] == {"data_product": {"id": "abc"}}

    def test_does_nothing_when_url_not_configured(self):
        """call_v2_webhook is a no-op when WEBHOOK_V2_URL is None."""
        import asyncio

        from app.core.webhooks.v2 import call_v2_webhook

        with webhook_v2_config(url=None), patch("httpx.AsyncClient") as mock_cls:
            asyncio.get_event_loop().run_until_complete(
                call_v2_webhook("data_product.created", {})
            )
            mock_cls.assert_not_called()
