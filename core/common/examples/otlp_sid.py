from common.examples.setup.setup_environ import (
    setup_community_env,
    setup_enterprise_env,
)
from common.initialize.initialize import initialize_services
from common.service import get_oltp_sid_service

# 注册settings_service，确保混合配置服务生效
need_init_services = ["settings_service"]
initialize_services(services=need_init_services)


def test_otlp_sid_service_community():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_sid_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["otlp_sid_service"]
    # 设置社区版环境变量
    setup_community_env()
    initialize_services(services=need_init_services)
    sid_service = get_oltp_sid_service()
    sid = sid_service.sid()
    print("sid:", sid)


def test_otlp_sid_service_enterprise():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["otlp_sid_service"]
    # 设置企业版环境变量
    setup_enterprise_env()
    initialize_services(services=need_init_services)


if __name__ == "__main__":
    test_otlp_sid_service_community()
