"""测试 API 应用主模块。"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI

from api.app import RPAServer
from exceptions.config_exceptions import ConfigNotFoundException, EnvNotFoundException


class TestRPAServer:
    """RPAServer 类的测试用例。"""

    def test_load_env_success(self, temp_env_file: str) -> None:
        """测试成功加载环境变量文件。"""
        with patch("api.app.Path") as mock_path_class:
            mock_path_instance = MagicMock()
            mock_path_class.return_value.resolve.return_value.parent.parent.__truediv__.return_value = Path(
                temp_env_file
            )
            mock_path_instance.exists.return_value = True
            mock_path_class.return_value.resolve.return_value.parent.parent.__truediv__.return_value.exists.return_value = (  # type: ignore[attr-defined]
                True
            )

            with patch("api.app.load_dotenv") as mock_load_dotenv:
                RPAServer.load_env()
                mock_load_dotenv.assert_called_once()

    def test_load_env_file_not_found(self) -> None:
        """测试环境变量文件不存在时抛出异常。"""
        with patch.object(Path, "exists", return_value=False):
            with pytest.raises(ConfigNotFoundException):
                RPAServer.load_env()

    def test_check_env_success(self, mock_env_vars: Dict[str, str]) -> None:
        """测试所有必需的环境变量都存在时检查成功。"""
        # 由于 mock_env_vars fixture 已经设置了环境变量，直接调用即可
        RPAServer.check_env()  # 应该不抛出异常

    def test_check_env_missing_vars(self) -> None:
        """测试缺少必需环境变量时抛出异常。"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(EnvNotFoundException):
                RPAServer.check_env()

    def test_set_config(self, mock_env_vars: Dict[str, str]) -> None:
        """测试设置日志配置。"""
        with patch("api.app.set_log") as mock_set_log:
            RPAServer.set_config()
            mock_set_log.assert_called_once_with("DEBUG", "./test_logs")

    def test_start_uvicorn(self, mock_env_vars: Dict[str, str]) -> None:
        """测试启动 Uvicorn 服务器。"""
        with patch("api.app.uvicorn.Server") as mock_server_class:
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            with patch("api.app.import_module") as mock_import:
                mock_module = MagicMock()
                mock_app = MagicMock()
                # 修正属性访问方式
                setattr(mock_module, "xingchen_rap_server_app", mock_app)
                mock_import.return_value = mock_module

                RPAServer.start_uvicorn()
                mock_server.run.assert_called_once()

    def test_start_uvicorn_missing_app_var(self) -> None:
        """测试缺少 UVICORN_APP_KEY 环境变量时抛出异常。"""
        with patch.dict(os.environ, {"UVICORN_APP_KEY": ""}, clear=False):
            with pytest.raises(ValueError):
                RPAServer.start_uvicorn()

    def test_start_method(
        self, mock_env_vars: Dict[str, str], temp_env_file: str
    ) -> None:
        """测试 start 方法的完整流程。"""
        with patch.object(RPAServer, "load_env") as mock_load:
            with patch.object(RPAServer, "check_env") as mock_check:
                with patch.object(RPAServer, "set_config") as mock_set:
                    with patch.object(RPAServer, "start_uvicorn") as mock_start:
                        server = RPAServer()
                        server.start()

                        mock_load.assert_called_once()
                        mock_check.assert_called_once()
                        mock_set.assert_called_once()
                        mock_start.assert_called_once()


def test_xingchen_rap_server_app() -> None:
    """测试 FastAPI 应用创建函数。"""
    from api.app import xingchen_rap_server_app

    app = xingchen_rap_server_app()
    assert app is not None
    assert hasattr(app, "include_router")
