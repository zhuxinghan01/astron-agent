"""
初始化设置
"""

import os

from pydantic import Field

# 本地配置地址，请根据实际情况修改，如果只使用远程可不设置
os.environ["CONFIG_ENV_PATH"] = (
    "/Users/dl/XfProjects/xfyun_webdev_gitee/openstellar/core/common/examples/init_service/.env"
)
# 设置版本为社区版
# os.environ["ENTERPRISE_ENABLED"] = "false"
# 设置版本为商业版
# os.environ["ENTERPRISE_ENABLED"] = "true"
# 设置为使用北极星配置中心
os.environ["POLARIS_ENABLED"] = "true"
os.environ["POLARIS_BASE_URL"] = "http://172.30.209.27:8090/"
os.environ["POLARIS_USERNAME"] = "mingduan"
os.environ["POLARIS_PASSWORD"] = "123456"
os.environ["POLARIS_PROJECT"] = "hy-spark-agent-builder"
os.environ["POLARIS_CLUSTER"] = "dev"
os.environ["POLARIS_SERVICE"] = "spark-agent"
os.environ["POLARIS_VERSION"] = "1.0.0"
os.environ["POLARIS_CONFIG_FILE"] = "spark-agent.env"
os.environ["POLARIS_RETRY_COUNT"] = "3"  # 获取失败后重试次数，非必须
os.environ["POLARIS_RETRY_INTERVAL"] = "10"  # 获取失败后重试间隔，必须


# need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
need_init_services = ["settings_service"]


def test_settings_services():
    from common.initialize.initialize import initialize_services

    initialize_services(services=need_init_services)


def test_use_settings_service():
    from pydantic_settings import BaseSettings, SettingsConfigDict

    from common.service import get_settings_service

    # .env配置
    class ArkLLMSettings(BaseSettings):
        ark_base_url: str = Field(
            default="https://api.ark.com/v1",
            env="ARK_BASE_URL",
            description="火山方舟LLM服务地址",
        )

    class OpenAILLMSettings(BaseSettings):
        openai_base_url: str = Field(
            default="https://api.openai.com/v1",
            env="OPENAI_BASE_URL",
            description="Openai LLM服务地址",
        )

    class ServiceInfoSettings(BaseSettings):
        # polaris
        service_name: str = Field(default="", description="服务名称")

        # .env
        service_version: str = Field(default="1.0.0", description="服务版本号")

    class LLMSettings(ArkLLMSettings, OpenAILLMSettings):
        general_temperature: float = Field(
            default=0.7, env="GENERAL_TEMPERATURE", description="通用温度参数"
        )

    class MySettings(
        get_settings_service().setting_base, LLMSettings, ServiceInfoSettings
    ):
        model_config = SettingsConfigDict(
            env_file=os.getenv("CONFIG_ENV_PATH"),
            env_file_encoding="utf-8",
            extra="ignore",
        )
        pass

    my_settings = MySettings()
    return my_settings


if __name__ == "__main__":
    # init
    test_settings_services()

    # use
    project_settings = test_use_settings_service()
    print("service name:", project_settings.service_name)
    print("service version:", project_settings.service_version)
    print("------- ")
    print("ark_base_url:", project_settings.ark_base_url)
    print("openai_base_url:", project_settings.openai_base_url)
    print("general_temperature:", project_settings.general_temperature)
    print("------- ")
    print("os.environ 'ARK_BASE_URL':", os.getenv("ARK_BASE_URL"))
    print("os.environ 'ark_base_url':", os.getenv("ark_base_url"))
    print("------- ")
    for k, v in os.environ.items():
        print(f"{k}: {v}")
