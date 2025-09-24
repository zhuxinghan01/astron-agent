from pydantic import Field
from pydantic_settings import BaseSettings

# Use unified common package import module
from common_imports import ip


class XChenUtilsConfig(BaseSettings):
    # metrics
    METRIC_ENDPOINT: str = Field(default="127.0.0.1:4317")
    METRIC_TIMEOUT: int = Field(default=3000)
    METRIC_EXPORT_INTERVAL_MILLIS: int = Field(default=3000)
    METRIC_EXPORT_TIMEOUT_MILLIS: int = Field(default=3000)

    # sid
    SID_SUB: str = Field(default="sag")
    SID_LOCATION: str = Field(default="dx")
    SID_LOCAL_IP: str = Field(default=ip)
    SID_LOCAL_PORT: str = Field(default="17870")

    # trace
    TRACE_ENDPOINT: str = Field(default="127.0.0.1:4317")
    TRACE_TIMEOUT: int = Field(default=3000)
    TRACE_MAX_QUEUE_SIZE: int = Field(default=2048)
    TRACE_SCHEDULE_DELAY_MILLIS: int = Field(default=3000)
    TRACE_MAX_EXPORT_BATCH_SIZE: int = Field(default=500)
    TRACE_EXPORT_TIMEOUT_MILLIS: int = Field(default=3000)

    # kafka for node tracing
    NODE_TRACE_KAFKA_SERVERS: str = Field(default="")
    NODE_TRACE_KAFKA_TIMEOUT: int = Field(default=10)
    NODE_TRACE_KAFKA_TOPIC: str = Field(default="spark-agent-builder")
