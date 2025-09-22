import os
import json
import threading
import time
from pathlib import Path

import uvicorn
from api.router import router
from consts import const
from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger
from xingchen_utils import init
from xingchen_utils.otlp.util.ip import ip
from xingchen_utils.polaris.client import Polaris, ConfigFilter
from domain.models.manager import init_data_base
from utils.log.logger import configure
from utils.sid.sid_generator2 import spark_link_init_sid
from utils.json_schemas.read_json_schemas import (
    load_create_tool_schema,
    load_update_tool_schema,
    load_http_run_schema,
    load_tool_debug_schema,
    load_mcp_register_schema,
)


class SparkLinkServer:

    def start(self):
        """
        Start the Spark Link server by setting up the environment,
        configuring the server, and launching Uvicorn.

        This method orchestrates the complete server startup process including
        environment configuration, server setup, and HTTP server initialization.
        """
        self.set_env()
        self.setup_server()
        self.start_uvicorn()

    def set_env(self):
        """
        Configure the environment by loading settings from local files or
        remotePolaris configuration.

        This method attempts to load environment variables from a local .env.example
        file first. If the local file doesn't exist, it falls back to loading
        configuration from the Polaris configuration service and starts a background
        watcher to periodically update the configuration.
        """
        try:

            env_file = Path(__file__).parent.parent / "config.env"
            if os.path.exists(env_file):
                load_dotenv(env_file, override=True)
                print(f"Using local cfg file: {env_file}")
                print(
                    f"env {const.enable_otlp_key}: {os.getenv(const.enable_otlp_key)}"
                )
            else:
                self.load_config()  # Main thread configuration loading initialization
                self.start_config_watcher()  # Start configuration loading polling thread
                print("Using polaris online configuration file.")
        except Exception as e:
            print("Load config file failed.", e)

    def start_config_watcher(self):
        """Start a background thread to pull configuration every 5 minutes"""

        def config_watcher():
            while True:
                try:
                    self.load_config()
                except Exception as e:
                    logger.error(f"Configuration pull failed: {e}")
                time.sleep(300)

        thread = threading.Thread(target=config_watcher, daemon=True)
        thread.start()

    @staticmethod
    def load_config():
        """Load configuration"""
        if const.Env == const.ENV_PRODUCTION:
            base_url = const.POLARIS_PRO_URL
            cluster_group = const.POLARIS_PRO_CLUSTER_GROUP
        elif const.Env == const.ENV_PRERELEASE:
            base_url = const.POLARIS_PRE_URL
            cluster_group = const.POLARIS_PRE_CLUSTER_GROUP
        else:
            base_url = const.POLARIS_DEV_URL
            cluster_group = const.POLARIS_DEV_CLUSTER_GROUP

        polaris = Polaris(
            base_url=base_url,
            username=os.getenv(const.POLARIS_USERNAME_KEY),
            password=os.getenv(const.POLARIS_PASSWORD_KEY),
        )
        config_filter = ConfigFilter(
            project_name=const.POLARIS_PROJECT_NAME,
            cluster_group=cluster_group,
            service_name=const.POLARIS_SERVICE_NAME,
            version=const.POLARIS_VERSION,
            config_file=const.POLARIS_CONFIG_FILE,
        )

        _ = polaris.pull(
            config_filter=config_filter, retry_count=3, retry_interval=5, set_env=True
        )

    @staticmethod
    def setup_server():
        """Initialize service suite"""
        if os.getenv(const.enable_otlp_key, "false").lower() == "true":
            init(
                environ=const.XingchenEnviron,
                service_name=os.getenv(const.service_name_key),
                metric_endpoint=os.getenv(const.metric_endpoint_key),
                metric_timeout=int(os.getenv(const.metric_timeout_key)),
                metric_export_interval_millis=int(
                    os.getenv(const.metric_export_interval_millis_key)
                ),
                metric_export_timeout_millis=int(
                    os.getenv(const.metric_export_timeout_millis_key)
                ),
                sid_sub=os.getenv(const.sid_sub_key),
                sid_location=os.getenv(const.sid_location_key),
                sid_local_ip=ip,
                sid_local_port=os.getenv(const.sid_local_port_key),
                trace_endpoint=os.getenv(const.trace_endpoint_key),
                trace_timeout=int(os.getenv(const.trace_timeout_key)),
                trace_max_queue_size=int(os.getenv(const.trace_max_queue_size_key)),
                trace_schedule_delay_millis=int(
                    os.getenv(const.trace_schedule_delay_millis_key)
                ),
                trace_max_export_batch_size=int(
                    os.getenv(const.trace_max_export_batch_size_key)
                ),
                trace_export_timeout_millis=int(
                    os.getenv(const.trace_export_timeout_millis_key)
                ),
            )

    @staticmethod
    def start_uvicorn():
        """
        Start the Uvicorn ASGI server with configuration loaded from environment
        variables.

        This method creates and starts a Uvicorn server instance using configuration
        parameters such as host, port, worker count, reload settings, and WebSocket
        ping intervals retrieved from environment variables.
        """
        uvicorn_config = uvicorn.Config(
            app=os.getenv(const.UVICORN_APP_KEY),
            host=os.getenv(const.UVICORN_HOST_KEY),
            port=int(os.getenv(const.UVICORN_PORT_KEY)),
            workers=int(os.getenv(const.UVICORN_WORKERS_KEY)),
            reload=json.loads(os.getenv(const.UVICORN_RELOAD_KEY)),
            ws_ping_interval=json.loads(os.getenv(const.UVICORN_WS_PING_INTERVAL_KEY)),
            ws_ping_timeout=json.loads(os.getenv(const.UVICORN_WS_PING_TIMEOUT_KEY)),
            factory=True,
            # log_config=None
        )
        uvicorn_server = uvicorn.Server(uvicorn_config)
        uvicorn_server.run()


def spark_link_app():
    """
    Create Spark Link app.

    Returns:
        FastAPI: The configured FastAPI application instance
    """
    configure(
        os.getenv(const.SPARK_LINK_LOG_LEVEL_KEY),
        Path(__file__).parent.parent / os.getenv(const.SPARK_LINK_LOG_PATH_KEY),
    )
    init_data_base()
    load_create_tool_schema()
    load_update_tool_schema()
    load_http_run_schema()
    load_tool_debug_schema()
    load_mcp_register_schema()
    spark_link_init_sid()
    app = FastAPI()
    app.include_router(router)
    logger.error("init success")
    return app
