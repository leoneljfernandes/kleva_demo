import logging
import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

LOG_FORMAT = (
    "%(asctime)s %(levelname)s [%(name)s] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] - %(message)s"
)
PLAIN_LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] - %(message)s"


def setup_telemetry(app: FastAPI, db_engine) -> bool:
    """Tracing solo si existe OTEL_EXPORTER_OTLP_ENDPOINT: tests y ejecución local no necesitan Tempo."""
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")  # variable estándar de OTel
    if not endpoint:
        logging.basicConfig(level=logging.INFO, format=PLAIN_LOG_FORMAT)
        return False

    provider = TracerProvider(
        resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "kleva-api")})
    )
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True)))
    trace.set_tracer_provider(provider)

    LoggingInstrumentor().instrument(set_logging_format=True, logging_format=LOG_FORMAT)
    logging.getLogger().setLevel(logging.INFO)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics")
    SQLAlchemyInstrumentor().instrument(engine=db_engine.sync_engine)  # engine async → .sync_engine
    return True
