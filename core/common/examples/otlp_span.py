import time

from opentelemetry.trace import Status, StatusCode

from common.examples.setup.setup_environ import (
    setup_community_env,
    setup_enterprise_env,
)
from common.initialize.initialize import initialize_services
from common.service import get_otlp_span_service

# 注册settings_service，确保混合配置服务生效
# need_init_services = ["settings_service", "otlp_sid_service"]
# initialize_services(services=need_init_services)


def test_span():

    from common.otlp.log_trace.node_log import NodeLog
    from common.otlp.trace.span import Span

    node_log = NodeLog("1", "2", "3", "4")

    def do_work1():
        span_service = get_otlp_span_service()
        # 从全局跟踪器提供者创建一个跟踪器
        span = span_service.get_span()()
        # span = Span()
        # 当 'with' 代码块超出其作用域时，'span' 被关闭
        with span.start() as current_span:
            current_span.set_attribute("operation.value", "chain1", node_log)
            current_span.set_attribute("operation.name", "Saying hello!", node_log)
            current_span.set_attribute("operation.other-stuff", [1, 2, 3], node_log)
            current_span.set_status(Status(StatusCode.ERROR))
            current_span.set_attributes(
                attributes={"info1": "chain1 info1", "info2": "chain1 info2"},
                node_log=node_log,
            )
            current_span.add_error_event("error event content", node_log)
            # current_span.record_exception(ex)
            time.sleep(1)
            do_work2(current_span)

    def do_work2(span: Span):
        with span.start(func_name="do_work222") as current_span:
            time.sleep(1)
            do_work3(current_span)

    def do_work3(span: Span):
        with span.start(attributes={"do work3": "do something"}) as current_span:
            time.sleep(1)
            current_span.set_attribute("test log", "do_work3", node_log)
            current_span.set_attribute("operation.name", "Saying hello!", node_log)
            current_span.add_event(
                name="event test",
                attributes={"event content": "success"},
                node_log=node_log,
            )
            print("Hello world from OpenTelemetry Python!")

    def test_do_work():
        do_work1()
        print(node_log.model_dump_json(indent=2))

    test_do_work()


def test_otlp_span_service_community():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["otlp_sid_service", "otlp_span_service"]
    # 设置社区版环境变量
    setup_community_env()
    initialize_services(services=need_init_services)
    test_span()


def test_otlp_span_service_enterprise():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["otlp_span_service"]
    # 设置企业版环境变量
    setup_enterprise_env()
    initialize_services(services=need_init_services)


if __name__ == "__main__":
    test_otlp_span_service_community()
