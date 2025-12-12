from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource

def setup_tracing(service_name: str):

    print(f"Setting up tracing for {service_name}")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    exporter = JaegerExporter(agent_host_name="jaeger", agent_port=6831)

    span_processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(span_processor)

    return trace.get_tracer(service_name)
