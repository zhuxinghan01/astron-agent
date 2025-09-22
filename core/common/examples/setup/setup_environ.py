"""
模拟容器环境启动变量
"""

import os

from pydantic_settings import SettingsConfigDict

from common.initialize.initialize import initialize_services
from common.service import get_settings_service

need_init_services = ["settings_service", "otlp_sid_service"]


def setup_community_env():
    # 本地配置文件路径
    os.environ["CONFIG_ENV_PATH"] = (
        "/Users/dl/XfProjects/xfyun_webdev_gitee/openstellar/core/common/examples/setup/.env"
    )
    # 设置版本为社区版
    os.environ["ENTERPRISE_ENABLED"] = "false"  # 可省略
    initialize_services(services=need_init_services)
    # --- 以上两个环境变量可从Deployment.yaml中设置 --- #
    # class MySettings(get_settings_service().setting_base):
    #     model_config = SettingsConfigDict(
    #         env_file=os.getenv("CONFIG_ENV_PATH"),
    #         env_file_encoding="utf-8",
    #         extra="ignore",
    #     )

    # my_settings = MySettings()
    # print("all configs::")
    # for k, v in os.environ.items():
    #     print(f"{k}: {v}")
    # print("end----")


def setup_enterprise_env():
    # 本地配置文件路径
    os.environ["CONFIG_ENV_PATH"] = (
        "/Users/dl/XfProjects/xfyun_webdev_gitee/openstellar/core/common/examples/setup/.env"
    )
    # 设置版本为商业版
    os.environ["ENTERPRISE_ENABLED"] = "true"  # 可省略
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
    os.environ["POLARIS_RETRY_COUNT"] = "3"  # 获取失败后重试次数 可省略
    os.environ["POLARIS_RETRY_INTERVAL"] = "10"  # 获取失败后重试间隔 可省略

    # --- 以上多个环境变量可从Deployment.yaml中设置 --- #

    class MySettings(get_settings_service().setting_base):
        model_config = SettingsConfigDict(
            env_file=os.getenv("CONFIG_ENV_PATH"),
            env_file_encoding="utf-8",
            extra="ignore",
        )

    my_settings = MySettings()
    print(my_settings.model_dump_json())


if __name__ == "__main__":
    setup_community_env()
