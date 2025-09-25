"""Constants definition module.
This module defines all constants used in the RPA service.
"""

from plugin.rpa.consts.app.app_keys import (
    SERVICE_PORT_KEY,
)
from plugin.rpa.consts.log.log_keys import (
    LOG_LEVEL_KEY,
    LOG_PATH_KEY,
)
from plugin.rpa.consts.rpa.rpa_keys import (
    XIAOWU_RPA_PING_INTERVAL_KEY,
    XIAOWU_RPA_TASK_CREATE_URL_KEY,
    XIAOWU_RPA_TASK_QUERY_INTERVAL_KEY,
    XIAOWU_RPA_TASK_QUERY_URL_KEY,
    XIAOWU_RPA_TIMEOUT_KEY,
)

from plugin.rpa.consts.otlp.otlp_keys import (
    SERVICE_NAME_KEY,
    OTLP_ENABLE_KEY,
    OTLP_DC_KEY,
    OTLP_SERVICE_NAME_KEY,
    KAFKA_TOPIC_KEY
)

__all__ = [
    "SERVICE_PORT_KEY",
    "LOG_LEVEL_KEY",
    "LOG_PATH_KEY",
    "XIAOWU_RPA_PING_INTERVAL_KEY",
    "XIAOWU_RPA_TASK_CREATE_URL_KEY",
    "XIAOWU_RPA_TASK_QUERY_INTERVAL_KEY",
    "XIAOWU_RPA_TASK_QUERY_URL_KEY",
    "XIAOWU_RPA_TIMEOUT_KEY",
    "SERVICE_NAME_KEY",
    "OTLP_ENABLE_KEY",
    "OTLP_DC_KEY",
    "OTLP_SERVICE_NAME_KEY",
    "KAFKA_TOPIC_KEY"
]
