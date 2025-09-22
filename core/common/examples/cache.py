"""
初始化cache
"""

from common.examples.setup.setup_environ import (
    setup_community_env,
    setup_enterprise_env,
)
from common.initialize.initialize import initialize_services
from common.service import get_cache_service

# 注册settings_service，确保混合配置服务生效
need_init_services = ["settings_service"]
initialize_services(services=need_init_services)


def test_use_cache_service_community():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["cache_service"]
    # 设置社区版环境变量  -- 单机版
    setup_community_env()
    initialize_services(services=need_init_services)
    cache_service = get_cache_service()
    connect_status = cache_service.is_connected()
    print(f"Cache service connected: {connect_status}")


def test_use_cache_service_enterprise():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["cache_service"]
    # 设置企业版环境变量
    setup_enterprise_env()
    initialize_services(services=need_init_services)
    cache_service = get_cache_service()
    connect_status = cache_service.is_connected()
    print(f"Cache service connected: {connect_status}")


if __name__ == "__main__":
    test_use_cache_service_community()
