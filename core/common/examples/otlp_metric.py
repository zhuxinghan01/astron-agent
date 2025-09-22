from common.examples.setup.setup_environ import (
    setup_community_env,
    setup_enterprise_env,
)
from common.initialize.initialize import initialize_services
from common.service import get_otlp_metric_service

# 注册settings_service，确保混合配置服务生效
need_init_services = ["settings_service"]
initialize_services(services=need_init_services)


def test_otlp_metric_service_community():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["otlp_metric_service"]
    # 设置社区版环境变量
    setup_community_env()
    initialize_services(services=need_init_services)
    metric_service = get_otlp_metric_service()
    print("metric service:", metric_service)
    m = metric_service.get_meter()(app_id="test_app_id", func="test_func")
    import time

    time.sleep(0.2)
    m.in_success_count()


def test_otlp_metric_service_enterprise():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["oss_service"]
    # 设置企业版环境变量
    setup_enterprise_env()
    initialize_services(services=need_init_services)


if __name__ == "__main__":
    test_otlp_metric_service_community()
