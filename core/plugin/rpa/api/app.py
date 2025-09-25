"""Main application module for RPA service.
This module defines the main entry point of the FastAPI application and includes
environment variable loading, configuration checking, logging setup, and Uvicorn server startup logic."""

import json
import os
from importlib import import_module
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from plugin.rpa.api.router import router
from consts import const
from plugin.rpa.exceptions.config_exceptions import EnvNotFoundException
from plugin.rpa.utils.log.logger import set_log
from common.initialize.initialize import initialize_services


class RPAServer:
    """Main class for RPA service, responsible for loading environment variables, checking configuration, setting up logging, and starting the Uvicorn server."""

    def start(self) -> None:
        """Start the RPA service."""
        self.setup_server()
        self.check_env()
        self.set_config()
        self.start_uvicorn()

    @staticmethod
    def setup_server():
        """Initialize service suite"""
        need_init_services = ["settings_service", "log_service", "otlp_sid_service", "otlp_span_service", "otlp_metric_service", "kafka_producer_service"]
        initialize_services(services=need_init_services)

    @staticmethod
    def check_env() -> None:
        """
        Check if all required environment variables are set.
        Raise an exception if any required environment variables are not set.
        """
        required_keys = [
            const.LOG_LEVEL_KEY,
            const.LOG_PATH_KEY,
            const.XIAOWU_RPA_TIMEOUT_KEY,
            const.XIAOWU_RPA_PING_INTERVAL_KEY,
            const.XIAOWU_RPA_TASK_QUERY_INTERVAL_KEY,
            const.XIAOWU_RPA_TASK_CREATE_URL_KEY,
            const.XIAOWU_RPA_TASK_QUERY_URL_KEY,
        ]

        missing_keys = [key for key in required_keys if os.getenv(key) is None]

        if missing_keys:
            print(
                f"\033[91mMissing required environment variables: "
                f"{', '.join(missing_keys)}\033[0m"
            )
            raise EnvNotFoundException(str(missing_keys))

        print("\033[94mAll required environment variables are set.\033[0m")

    @staticmethod
    def set_config() -> None:
        """Set up logging configuration."""
        set_log(os.getenv(const.LOG_LEVEL_KEY), os.getenv(const.LOG_PATH_KEY))

    @staticmethod
    def start_uvicorn() -> None:
        """Static method to start the Uvicorn server.

        Read configuration from environment variables and start the Uvicorn server.
        """
        # assert task_create_url is not None
        uvicorn_config = uvicorn.Config(
            app=xingchen_rap_server_app(),
            host="0.0.0.0",
            port=int(os.getenv(const.SERVICE_PORT_KEY, "19999")),
            workers=20,
            reload=False,
            # log_config=None
        )
        uvicorn_server = uvicorn.Server(uvicorn_config)
        uvicorn_server.run()


def xingchen_rap_server_app() -> FastAPI:
    """
    description: Create and return a FastAPI application instance.
    This application instance contains all API routes registered through the router.
    This function is used as an application factory for the Uvicorn server.
    :return: FastAPI application instance
    """

    app = FastAPI()
    app.include_router(router)
    return app

if __name__ == "__main__":
    RPAServer().start()
