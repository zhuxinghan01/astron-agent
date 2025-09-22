"""全局测试配置文件。"""

import os
import tempfile
from typing import Any, Dict, Generator
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.app import xingchen_rap_server_app


@pytest.fixture(scope="session")
def temp_env_file() -> Generator[str, None, None]:
    """创建临时的环境变量文件用于测试。"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(
            """
LOG_LEVEL=DEBUG
LOG_PATH=./test_logs
UVICORN_APP=api.app:xingchen_rap_server_app
UVICORN_HOST=127.0.0.1
UVICORN_PORT=8000
UVICORN_WORKERS=1
UVICORN_RELOAD=false
UVICORN_WS_PING_INTERVAL=20.0
UVICORN_WS_PING_TIMEOUT=20.0
RPA_TIMEOUT=300
RPA_PING_INTERVAL=30
RPA_TASK_QUERY_INTERVAL=10
RPA_TASK_CREATE_URL=http://test.example.com/create
RPA_TASK_QUERY_URL=http://test.example.com/query
"""
        )
        temp_file = f.name

    yield temp_file

    # 清理
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture(scope="session")
def mock_env_vars() -> Generator[Dict[str, str], None, None]:
    """模拟环境变量。"""
    env_vars = {
        "LOG_LEVEL": "DEBUG",
        "LOG_PATH": "./test_logs",
        "UVICORN_APP": "api.app:xingchen_rap_server_app",
        "UVICORN_HOST": "127.0.0.1",
        "UVICORN_PORT": "8000",
        "UVICORN_WORKERS": "1",
        "UVICORN_RELOAD": "false",
        "UVICORN_WS_PING_INTERVAL": "20.0",
        "UVICORN_WS_PING_TIMEOUT": "20.0",
        "RPA_TIMEOUT": "300",
        "RPA_PING_INTERVAL": "30",
        "RPA_TASK_QUERY_INTERVAL": "10",
        "RPA_TASK_CREATE_URL": "http://test.example.com/create",
        "RPA_TASK_QUERY_URL": "http://test.example.com/query",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def app() -> FastAPI:
    """创建FastAPI应用实例。"""
    return xingchen_rap_server_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """创建测试客户端。"""
    return TestClient(app)


@pytest.fixture
def sample_execution_request() -> Dict[str, Any]:
    """样例执行请求数据。"""
    return {
        "access_token": "test_token",
        "project_id": "test_project_123",
        "exec_position": "test_position",
        "params": {"key1": "value1", "key2": "value2"},
        "sid": "test_session_123",
    }
