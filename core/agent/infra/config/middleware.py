from pydantic import Field
from pydantic_settings import BaseSettings


class RedisClusterConfig(BaseSettings):
    redis_nodes: str = Field(default="")
    redis_password: str = Field(default="")


class MysqlClusterConfig(BaseSettings):
    mysql_host: str = Field(default="")
    mysql_port: str = Field(default="")
    mysql_user: str = Field(default="")
    mysql_password: str = Field(default="")
    mysql_db: str = Field(default="")


class LinkConfig(BaseSettings):
    get_link_url: str = Field(default="")
    versions_link_url: str = Field(default="")
    run_link_url: str = Field(default="")


class WorkflowConfig(BaseSettings):
    get_workflows_url: str = Field(default="")
    workflow_sse_base_url: str = Field(default="")


class KnowledgeConfig(BaseSettings):
    chunk_query_url: str = Field(default="")


class McpConfig(BaseSettings):
    list_mcp_plugin_url: str = Field(default="")
    run_mcp_plugin_url: str = Field(default="")


class AppAuthConfig(BaseSettings):
    app_auth_host: str = Field(default="")
    app_auth_router: str = Field(default="")
    app_auth_prot: str = Field(default="")
    app_auth_api_key: str = Field(default="")
    app_auth_secret: str = Field(default="")


class ElkUploadConfig(BaseSettings):
    upload_node_trace: bool = Field(default=False)
    upload_metrics: bool = Field(default=False)


class MiddlewareConfig(
    RedisClusterConfig,
    MysqlClusterConfig,
    LinkConfig,
    WorkflowConfig,
    KnowledgeConfig,
    McpConfig,
    AppAuthConfig,
    ElkUploadConfig,
):
    pass
