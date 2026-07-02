"""
Regression tests for the OpenTelemetry tracing setup.

Original bug: enabling FastAPIInstrumentor caused an AttributeError on every
OPTIONS preflight request, resulting in 500 responses.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def _instrument():
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app)
    return FastAPIInstrumentor


def _uninstrument():
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.uninstrument_app(app)


class TestTracing:
    def test_tracing_setup_does_not_raise(self):
        """The full tracing setup block must complete without error."""
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        with (
            patch.object(OTLPSpanExporter, "__init__", return_value=None),
            patch.object(BatchSpanProcessor, "__init__", return_value=None),
            patch("opentelemetry.trace.set_tracer_provider"),
            patch.object(FastAPIInstrumentor, "instrument_app") as mock_instrument,
        ):
            from opentelemetry import trace
            from opentelemetry.sdk.resources import Resource

            provider = TracerProvider(
                resource=Resource.create({"service.name": "test"})
            )
            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
            trace.set_tracer_provider(provider)
            FastAPIInstrumentor.instrument_app(app)

        mock_instrument.assert_called_once()

    def test_options_preflight_does_not_500_with_tracing(self):
        """OPTIONS requests must not return 500 when FastAPIInstrumentor is active."""
        _instrument()
        try:
            with TestClient(app, raise_server_exceptions=False) as client:
                response = client.options("/api/v2/users/current")
                assert response.status_code != 500
        finally:
            _uninstrument()

    def test_options_preflight_does_not_500_without_tracing(self, client: TestClient):
        """Baseline: OPTIONS must work without tracing too."""
        response = client.options("/api/v2/users/current")
        assert response.status_code != 500
