import os
from typing import Optional
from plugin.link.domain.models.utils import DatabaseService, RedisService
from plugin.link.domain.entity.tool_schema import Tools
from plugin.link.consts import const

data_base_singleton: Optional[DatabaseService] = None
redis_singleton: Optional[RedisService] = None


def init_data_base():
    """
    Initialize the database.
    """
    # Use global statement to modify module-level singleton instance
    global data_base_singleton
    mysql_host = os.getenv(const.mysql_host_key)
    mysql_port = os.getenv(const.mysql_port_key)
    user = os.getenv(const.mysql_user_key)
    password = os.getenv(const.mysql_password_key)
    db = os.getenv(const.mysql_db_key)
    db_url = (
        f"mysql+pymysql://{user}:{password}@{mysql_host}:{mysql_port}/{db}"
        "?charset=utf8mb4"
    )
    data_base_singleton = DatabaseService(database_url=db_url)
    data_base_singleton.create_db_and_tables()

    # Initialize Redis service using global singleton pattern
    # Use global statement to modify module-level singleton instance
    global redis_singleton
    redis_cluster_addr = os.getenv(const.REDIS_CLUSTER_ADDR_KEY)
    password = os.getenv(const.REDIS_PASSWORD_KEY)
    redis_singleton = RedisService(cluster_addr=redis_cluster_addr, password=password)


def get_db_engine():
    """
    Get the global database service singleton instance.

    Returns:
        DatabaseService: The initialized database service instance
    """
    return data_base_singleton


def get_redis_engine():
    """
    Get the global Redis service singleton instance.

    Returns:
        RedisService: The initialized Redis service instance
    """
    return redis_singleton


if __name__ == "__main__":
    os.environ[const.mysql_host_key] = "mysql.mysql-hf04-2oc97b.svc.hfb.ipaas.cn"
    os.environ[const.mysql_port_key] = "8066"
    os.environ[const.mysql_user_key] = "admin"
    os.environ[const.mysql_password_key] = "EdgeAIGo!"
    os.environ[const.mysql_db_key] = "spark_link"

    os.environ[const.REDIS_CLUSTER_ADDR_KEY] = (
        "172.29.100.22:7301,172.29.100.23:7301,172.29.100.24:7301,"
        "172.29.100.22:7302,172.29.100.23:7302,172.29.100.24:7302"
    )
    os.environ[const.REDIS_PASSWORD_KEY] = "0EHYkZSsk1NoQQGH"

    init_data_base()
    add_test1 = Tools(
        app_id="123231",
        tool_id="tool@1q331",
        name="航班查询",
        description="查询航班信息",
        open_api_schema="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )

    redis_engine = get_redis_engine()
    res = redis_engine.get("spark_bot:bot_config:0059649e52bb4c97a9f32a4d4bfcceea")
    print(res)
