"""Constants module for Spark Link service.

Contains all configuration constants, environment variables, and key mappings used
throughout the Spark Link service. Constants are imported from various key modules
and used by other modules via attribute access (e.g., const.service_name_key).
"""

import os

# xingchen utils keys
# pylint: disable=unused-import  # These imports are used via module attribute access
from plugin.link.consts.polaris_keys.xc_utils_keys import (
    SERVICE_NAME_KEY,
    ENABLE_OTLP_KEY,
    METRIC_ENDPOINT_KEY,
    METRIC_TIMEOUT_KEY,
    METRIC_EXPORT_INTERVAL_MILLIS_KEY,
    METRIC_EXPORT_TIMEOUT_MILLIS_KEY,
    SID_SUB_KEY,
    SID_LOCATION_KEY,
    SID_LOCAL_PORT_KEY,
    TRACE_ENDPOINT_KEY,
    TRACE_TIMEOUT_KEY,
    TRACE_MAX_QUEUE_SIZE_KEY,
    TRACE_SCHEDULE_DELAY_MILLIS_KEY,
    TRACE_MAX_EXPORT_BATCH_SIZE_KEY,
    TRACE_EXPORT_TIMEOUT_MILLIS_KEY,
    KAFKA_SERVERS_KEY,
    KAFKA_TIMEOUT_KEY,
    KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY,
)

# uvicorn keys
# pylint: disable=unused-import  # These imports are used via module attribute access
from plugin.link.consts.polaris_keys.uvicorn_keys import (
    UVICORN_APP_KEY,
    UVICORN_HOST_KEY,
    UVICORN_PORT_KEY,
    UVICORN_WORKERS_KEY,
    UVICORN_RELOAD_KEY,
    UVICORN_WS_PING_INTERVAL_KEY,
    UVICORN_WS_PING_TIMEOUT_KEY,
)

# mysql
# pylint: disable=unused-import  # These imports are used via module attribute access
from plugin.link.consts.polaris_keys.mysql_keys import (
    MYSQL_HOST_KEY,
    MYSQL_PORT_KEY,
    MYSQL_USER_KEY,
    MYSQL_PASSWORD_KEY,
    MYSQL_DB_KEY,
)

# redis
# pylint: disable=unused-import  # These imports are used via module attribute access
from plugin.link.consts.polaris_keys.redis_keys import (
    REDIS_IS_CLUSTER_KEY,
    REDIS_CLUSTER_ADDR_KEY,
    REDIS_PASSWORD_KEY,
)

# spark
# pylint: disable=unused-import  # These imports are used via module attribute access
from plugin.link.consts.polaris_keys.spark_keys import (
    SPARK_LINK_LOG_LEVEL_KEY,
    SPARK_LINK_LOG_PATH_KEY,
    SPARK_RUN_KEY,
)

# common
# pylint: disable=unused-import  # These imports are used via module attribute access
from plugin.link.consts.polaris_keys.common_keys import (
    SEGMENT_BLACK_LIST_KEY,
    IP_BLACK_LIST_KEY,
    DOMAIN_BLACK_LIST_KEY,
    OFFICIAL_TOOL_KEY,
    THIRD_TOOL_KEY,
    APP_ID_KEY,
    DATACENTER_ID_KEY,
    WORKER_ID_KEY,
    HTTP_AUTH_QU_APP_ID_KEY,
    HTTP_AUTH_QU_APP_KEY_KEY,
    HTTP_AUTH_AWAU_APP_ID_KEY,
    HTTP_AUTH_AWAU_API_KEY_KEY,
    HTTP_AUTH_AWAU_API_SECRET_KEY,
)

# Environment variables
Env = os.getenv("ENVIRONMENT")
ENV_PRODUCTION = "production"
ENV_PRERELEASE = "prerelease"
ENV_DEVELOPMENT = "development"

# Runtime environment constants
DevelopmentEnv = "development"
ProductionEnv = "production"

# Keeping XingchenEnviron to match existing usage pattern
XingchenEnviron = (
    ProductionEnv if Env in (ENV_PRODUCTION, ENV_PRERELEASE) else DevelopmentEnv
)

# Configuration center connection
POLARIS_USERNAME_KEY = "PolarisUsername"
POLARIS_PASSWORD_KEY = "PolarisPassword"
POLARIS_PRO_URL = "http://cynosure.xfyun.cn"
POLARIS_PRE_URL = "http://cynosure.xfyun.cn"
POLARIS_DEV_URL = "http://172.30.209.27:8090"
POLARIS_PRO_CLUSTER_GROUP = "pro"
POLARIS_PRE_CLUSTER_GROUP = "pre"
POLARIS_DEV_CLUSTER_GROUP = "dev"
POLARIS_PROJECT_NAME = "hy-spark-agent-builder"
POLARIS_SERVICE_NAME = "spark-link"
POLARIS_VERSION = "1.0.0"
POLARIS_CONFIG_FILE = "config.env"

# Default tool version and deletion flag value
DEF_VER = "V1.0"
DEF_DEL = 0

# Legacy lowercase attribute aliases for backward compatibility
# These are needed for existing code that uses const.lowercase_name format
service_name_key = SERVICE_NAME_KEY
enable_otlp_key = ENABLE_OTLP_KEY
metric_endpoint_key = METRIC_ENDPOINT_KEY
metric_timeout_key = METRIC_TIMEOUT_KEY
metric_export_interval_millis_key = METRIC_EXPORT_INTERVAL_MILLIS_KEY
metric_export_timeout_millis_key = METRIC_EXPORT_TIMEOUT_MILLIS_KEY
sid_sub_key = SID_SUB_KEY
sid_location_key = SID_LOCATION_KEY
sid_local_port_key = SID_LOCAL_PORT_KEY
trace_endpoint_key = TRACE_ENDPOINT_KEY
trace_timeout_key = TRACE_TIMEOUT_KEY
trace_max_queue_size_key = TRACE_MAX_QUEUE_SIZE_KEY
trace_schedule_delay_millis_key = TRACE_SCHEDULE_DELAY_MILLIS_KEY
trace_max_export_batch_size_key = TRACE_MAX_EXPORT_BATCH_SIZE_KEY
trace_export_timeout_millis_key = TRACE_EXPORT_TIMEOUT_MILLIS_KEY
kafka_server_key = KAFKA_SERVERS_KEY
kafka_timeout_key = KAFKA_TIMEOUT_KEY
kafka_topic_sparklink_log_trace_key = KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY

uvicorn_app_key = UVICORN_APP_KEY
uvicorn_host_key = UVICORN_HOST_KEY
uvicorn_port_key = UVICORN_PORT_KEY
uvicorn_workers_key = UVICORN_WORKERS_KEY
uvicorn_reload_key = UVICORN_RELOAD_KEY
uvicorn_ws_ping_interval_key = UVICORN_WS_PING_INTERVAL_KEY
uvicorn_ws_ping_timeout_key = UVICORN_WS_PING_TIMEOUT_KEY

mysql_host_key = MYSQL_HOST_KEY
mysql_port_key = MYSQL_PORT_KEY
mysql_user_key = MYSQL_USER_KEY
mysql_password_key = MYSQL_PASSWORD_KEY
mysql_db_key = MYSQL_DB_KEY

redis_is_cluster_key = REDIS_IS_CLUSTER_KEY
redis_cluster_addr_key = REDIS_CLUSTER_ADDR_KEY
redis_password_key = REDIS_PASSWORD_KEY

spark_link_log_level_key = SPARK_LINK_LOG_LEVEL_KEY
spark_link_log_path_key = SPARK_LINK_LOG_PATH_KEY
spark_run_key = SPARK_RUN_KEY

segment_black_list_key = SEGMENT_BLACK_LIST_KEY
ip_black_list_key = IP_BLACK_LIST_KEY
domain_black_list_key = DOMAIN_BLACK_LIST_KEY
official_tool_key = OFFICIAL_TOOL_KEY
third_tool_key = THIRD_TOOL_KEY
app_id_key = APP_ID_KEY
datacenter_id_key = DATACENTER_ID_KEY
worker_id_key = WORKER_ID_KEY
http_auth_qu_app_id_key = HTTP_AUTH_QU_APP_ID_KEY
http_auth_qu_app_key_key = HTTP_AUTH_QU_APP_KEY_KEY
http_auth_awau_app_id_key = HTTP_AUTH_AWAU_APP_ID_KEY
http_auth_awau_api_key_key = HTTP_AUTH_AWAU_API_KEY_KEY
http_auth_awau_api_secret_key = HTTP_AUTH_AWAU_API_SECRET_KEY
