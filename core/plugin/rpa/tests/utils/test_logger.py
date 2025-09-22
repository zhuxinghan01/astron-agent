"""测试日志记录模块。"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from loguru import logger

from utils.log.logger import VALID_LOG_LEVELS, patching, serialize, set_log


class TestLoggerUtilities:
    """日志工具函数的测试用例。"""

    def test_serialize_function(self) -> None:
        """测试 serialize 函数。"""
        # 模拟日志记录对象
        mock_record: Dict[str, Any] = {
            "time": MagicMock(),
            "level": "INFO",
            "message": "Test message",
        }
        mock_record["time"].timestamp.return_value = 1234567890.123

        result = serialize(mock_record)

        assert isinstance(result, bytes)
        # 验证结果包含时间戳
        import orjson

        data = orjson.loads(result)
        assert "timestamp" in data
        assert data["timestamp"] == 1234567890.123

    def test_patching_function(self) -> None:
        """测试 patching 函数。"""
        # 模拟日志记录对象
        mock_record: Dict[str, Any] = {"time": MagicMock(), "extra": {}}
        mock_record["time"].timestamp.return_value = 1234567890.123

        patching(mock_record)

        assert "serialized" in mock_record["extra"]
        assert isinstance(mock_record["extra"]["serialized"], bytes)

    def test_valid_log_levels_constant(self) -> None:
        """测试有效日志级别常量。"""
        expected_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert VALID_LOG_LEVELS == expected_levels


class TestSetLog:
    """set_log 函数的测试用例。"""

    def teardown_method(self) -> None:
        """清理方法，移除所有日志处理器。"""
        logger.remove()

    @patch("utils.log.logger.logger")
    def test_set_log_with_explicit_params(self, mock_logger: MagicMock) -> None:
        """测试使用显式参数设置日志。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "test.log")

            set_log(log_level="DEBUG", log_path=log_path)

            # 验证 logger 方法被调用
            mock_logger.remove.assert_called_once()
            mock_logger.patch.assert_called_once()
            mock_logger.add.assert_called_once()

            # 获取 add 方法的调用参数
            call_args = mock_logger.add.call_args
            assert call_args[1]["level"] == "DEBUG"
            assert log_path in call_args[1]["sink"]

    @patch("utils.log.logger.logger")
    @patch.dict(os.environ, {"LOG_LEVEL": "ERROR", "LOG_PATH": "/tmp/test_logs"})
    def test_set_log_with_env_vars(self, mock_logger: MagicMock) -> None:
        """测试使用环境变量设置日志。"""
        set_log()

        # 验证使用了环境变量中的日志级别
        call_args = mock_logger.add.call_args
        assert call_args[1]["level"] == "ERROR"
        assert "/tmp/test_logs" in call_args[1]["sink"]

    @patch("utils.log.logger.logger")
    @patch("utils.log.logger.appdirs.user_cache_dir")
    def test_set_log_default_path(
        self, mock_user_cache_dir: MagicMock, mock_logger: MagicMock
    ) -> None:
        """测试使用默认日志路径。"""
        mock_user_cache_dir.return_value = "/tmp/cache"

        with patch.dict(os.environ, {}, clear=True):
            set_log(log_level="INFO")

        # 验证使用了默认路径
        call_args = mock_logger.add.call_args
        assert "/tmp/cache/rpa-server.log" in call_args[1]["sink"]

    @patch("utils.log.logger.logger")
    def test_set_log_default_level(self, mock_logger: MagicMock) -> None:
        """测试使用默认日志级别。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "test.log")

            with patch.dict(os.environ, {}, clear=True):
                set_log(log_path=log_path)

            # 验证使用了默认级别 INFO
            call_args = mock_logger.add.call_args
            assert call_args[1]["level"] == "INFO"

    @patch("utils.log.logger.logger")
    @patch.dict(os.environ, {"LOG_LEVEL": "INVALID_LEVEL"})
    def test_set_log_invalid_env_level(self, mock_logger: MagicMock) -> None:
        """测试环境变量中的无效日志级别。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "test.log")

            set_log(log_path=log_path)

            # 应该使用默认级别 INFO，因为环境变量中的级别无效
            call_args = mock_logger.add.call_args
            assert call_args[1]["level"] == "INFO"

    @patch("utils.log.logger.logger")
    def test_set_log_creates_directory(self, mock_logger: MagicMock) -> None:
        """测试日志函数创建不存在的目录。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建一个不存在的子目录路径
            log_path = os.path.join(temp_dir, "nested", "dir", "test.log")

            set_log(log_level="DEBUG", log_path=log_path)

            # 验证目录被创建
            assert os.path.exists(os.path.dirname(log_path))

    @patch("utils.log.logger.logger")
    def test_set_log_format_and_rotation(self, mock_logger: MagicMock) -> None:
        """测试日志格式和轮转配置。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "test.log")

            set_log(log_level="WARNING", log_path=log_path)

            call_args = mock_logger.add.call_args

            # 验证日志格式
            expected_format = (
                "{level} | {time:YYYY-MM-DD HH:mm:ss} | {process} - {thread} "
                "| {file} - {function}: {line} {message}"
            )
            assert call_args[1]["format"] == expected_format

            # 验证轮转配置
            assert call_args[1]["rotation"] == "10 MB"

    @patch("utils.log.logger.logger")
    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"})
    def test_set_log_env_level_priority(self, mock_logger: MagicMock) -> None:
        """测试环境变量优先级：当显式参数为 None 时使用环境变量。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "test.log")

            set_log(log_level=None, log_path=log_path)

            call_args = mock_logger.add.call_args
            assert call_args[1]["level"] == "DEBUG"

    @patch("utils.log.logger.logger")
    @patch.dict(os.environ, {"LOG_LEVEL": "ERROR"})
    def test_set_log_explicit_level_overrides_env(self, mock_logger: MagicMock) -> None:
        """测试显式参数覆盖环境变量。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "test.log")

            set_log(log_level="WARNING", log_path=log_path)

            call_args = mock_logger.add.call_args
            assert call_args[1]["level"] == "WARNING"  # 使用显式参数，而不是环境变量
