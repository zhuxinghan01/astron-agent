"""RPA 服务的主应用模块。
本模块定义了 FastAPI 应用的主入口，并包含了环境变量加载、
配置检查、日志设置以及 Uvicorn 服务器的启动逻辑。"""

import json
import os
from importlib import import_module
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from api.router import router
from consts import const
from exceptions.config_exceptions import ConfigNotFoundException, EnvNotFoundException
from utils.log.logger import set_log


class RPAServer:
    """RPA 服务的主类，负责加载环境变量、检查配置、设置日志并启动 Uvicorn 服务器。"""

    def start(self) -> None:
        """启动 RPA 服务。"""
        self.load_env()
        self.check_env()
        self.set_config()
        self.start_uvicorn()

    @staticmethod
    def load_env() -> None:
        """
        如果存在本地的 .env 文件，则从该文件加载环境变量。

        Returns:
            bool: 如果环境变量成功加载则返回 True，否则返回 False
            （例如，文件未找到或发生错误）。
        """
        env_file = Path(__file__).resolve().parent.parent / "config.env"

        if not env_file.exists():
            print(f"\033[91mNo local config file found at: {env_file}\033[0m")
            raise ConfigNotFoundException(str(env_file))

        load_dotenv(env_file, override=True)
        print(f"\033[94mUsing local config file: {env_file}\033[0m")

    @staticmethod
    def check_env() -> None:
        """
        检查所有必需的环境变量是否已设置。
        如果有任何必需的环境变量未设置，则抛出异常。
        """
        required_keys = [
            const.LOG_LEVEL_KEY,
            const.LOG_PATH_KEY,
            const.UVICORN_APP_KEY,
            const.UVICORN_HOST_KEY,
            const.UVICORN_PORT_KEY,
            const.UVICORN_WORKERS_KEY,
            const.UVICORN_RELOAD_KEY,
            const.UVICORN_WS_PING_INTERVAL_KEY,
            const.UVICORN_WS_PING_TIMEOUT_KEY,
            const.RPA_TIMEOUT_KEY,
            const.RPA_PING_INTERVAL_KEY,
            const.RPA_TASK_QUERY_INTERVAL_KEY,
            const.RPA_TASK_CREATE_URL_KEY,
            const.RPA_TASK_QUERY_URL_KEY,
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
        """设置日志配置。"""
        set_log(os.getenv(const.LOG_LEVEL_KEY), os.getenv(const.LOG_PATH_KEY))

    @staticmethod
    def start_uvicorn() -> None:
        """启动 Uvicorn 服务器的静态方法。

        从环境变量中读取配置，并启动 Uvicorn 服务器。
        """
        app_path = os.getenv(const.UVICORN_APP_KEY)
        if app_path:
            module_path, app_name = app_path.split(":")
            module = import_module(module_path)
            app = getattr(module, app_name)
        else:
            raise ValueError("Environment variable for UVICORN_APP_KEY is not set.")
        # assert task_create_url is not None
        uvicorn_config = uvicorn.Config(
            app=app,
            host=os.getenv(const.UVICORN_HOST_KEY, "0.0.0.0"),
            port=int(os.getenv(const.UVICORN_PORT_KEY, "19999")),
            workers=int(os.getenv(const.UVICORN_WORKERS_KEY, "20")),
            reload=json.loads(os.getenv(const.UVICORN_RELOAD_KEY, "false")),
            ws_ping_interval=float(
                json.loads(os.getenv(const.UVICORN_WS_PING_INTERVAL_KEY, "20.0"))
            ),
            ws_ping_timeout=float(
                json.loads(os.getenv(const.UVICORN_WS_PING_TIMEOUT_KEY, "20.0"))
            ),
            factory=True,
            # log_config=None
        )
        uvicorn_server = uvicorn.Server(uvicorn_config)
        uvicorn_server.run()


def xingchen_rap_server_app() -> FastAPI:
    """
    description: 创建并返回一个 FastAPI 应用实例。
    该应用实例包含了所有通过路由器注册的 API 路由。
    该函数用于 Uvicorn 服务器的应用工厂。
    :return: FastAPI 应用实例
    """

    app = FastAPI()
    app.include_router(router)
    return app
