"""
初始化log
"""

from common.examples.setup.setup_environ import (
    setup_community_env,
    setup_enterprise_env,
)
from common.initialize.initialize import initialize_services

# 注册settings_service，确保混合配置服务生效
need_init_services = ["settings_service"]
initialize_services(services=need_init_services)


def test_log_service_community():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["log_service"]
    # 设置社区版环境变量
    setup_community_env()
    initialize_services(services=need_init_services)


def test_log_service_enterprise():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["log_service"]
    # 设置企业版环境变量
    setup_enterprise_env()
    initialize_services(services=need_init_services)


def print_log():
    from loguru import logger

    logger.debug("this is a debug message.")
    logger.info("this is a info message.")
    logger.warning("this is a warning message.")
    logger.error("this is a error message.")


if __name__ == "__main__":
    test_log_service_community()
    print_log()
