"""
初始化cache
"""

from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel

from common.examples.setup.setup_environ import (
    setup_community_env,
    setup_enterprise_env,
)
from common.initialize.initialize import initialize_services
from common.service import get_db_service
from common.service.db.db_service import session_getter


class App(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    name: str = Field(default="")
    alias_id: str = Field(default="")
    api_key: str = Field(default="")
    api_secret: str = Field(default="")
    description: str = Field(default="")
    create_by: int = Field(default=None)
    update_by: int = Field(default=None)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)


# 注册settings_service，确保混合配置服务生效
need_init_services = ["settings_service"]
initialize_services(services=need_init_services)


def test_use_database_service_community():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["database_service"]
    # 设置社区版环境变量
    setup_community_env()
    initialize_services(services=need_init_services)
    try:
        with session_getter(get_db_service()) as session:
            app = session.query(App).filter(App.alias_id == "4eea957b").first()
            print(app)
            print("Database service connected")
    except Exception:
        assert False, "Database service connection failed"


def test_use_database_service_enterprise():
    # need_init_services = ["cache_service", "database_service", "log_service", "kafka_producer_service", "oss_service", "masdk_service", "otlp_metric_service", "otlp_span_service", "otlp_node_log_service", "settings_service"]
    need_init_services = ["cache_service"]
    # 设置企业版环境变量
    setup_enterprise_env()
    initialize_services(services=need_init_services)
    try:
        with session_getter(get_db_service()) as session:
            result = session.execute("SELECT 1").fetchone()
            assert result[0] == 1
            print("Database service connected, test query result: {result}")
    except Exception:
        assert False, "Database service connection failed"


if __name__ == "__main__":
    test_use_database_service_community()
