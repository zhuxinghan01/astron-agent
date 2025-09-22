"""
初始化ma
"""

from common.examples.setup.setup_environ import (
    setup_community_env,
    setup_enterprise_env,
)
from common.initialize.initialize import initialize_services
from common.service import get_masdk_service

# 注册settings_service，确保混合配置服务生效
need_init_services = ["settings_service"]
initialize_services(services=need_init_services)


def test_ma_service_community():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["masdk_service"]
    # 设置社区版环境变量
    setup_community_env()
    initialize_services(services=need_init_services)

    #
    from common.metrology_auth import MASDKRequest

    masdk_request = MASDKRequest(
        sid="spf007b5ed9@dx19932ea7ba9a4f1782",
        appid="xxxx",
        uid="",
        channel="xxxx",
        function="xxxx",
        cnt=1,
    )

    # 计量授权
    calc_response = get_masdk_service().ma_sdk.metrology_authorization(masdk_request)
    print(calc_response)
    # 并发授权
    conc_response = get_masdk_service().ma_sdk.acquire_concurrent(masdk_request)
    print(conc_response)
    get_masdk_service().ma_sdk.release_concurrent(masdk_request)


def test_ma_service_enterprise():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["masdk_service"]
    # 设置企业版环境变量
    setup_enterprise_env()
    initialize_services(services=need_init_services)


if __name__ == "__main__":
    test_ma_service_community()
