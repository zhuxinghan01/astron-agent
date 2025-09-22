"""测试配置异常模块。"""

import pytest

from exceptions.config_exceptions import (
    ConfigNotFoundException,
    CreatTaskException,
    EnvNotFoundException,
    InvalidConfigException,
    QueryTaskException,
)


class TestConfigNotFoundException:
    """ConfigNotFoundException 的测试用例。"""

    def test_config_not_found_exception_creation(self) -> None:
        """测试创建 ConfigNotFoundException。"""
        path = "/path/to/config.env"
        exception = ConfigNotFoundException(path)

        assert isinstance(exception, Exception)
        assert exception.message == f"Configuration file not found at path: {path}"
        assert (
            str(exception)
            == f"[Exception] Configuration file not found at path: {path}"
        )

    def test_config_not_found_exception_inheritance(self) -> None:
        """测试 ConfigNotFoundException 继承。"""
        path = "/path/to/config.env"
        exception = ConfigNotFoundException(path)

        assert isinstance(exception, Exception)
        assert isinstance(exception, ConfigNotFoundException)

    def test_config_not_found_exception_with_different_paths(self) -> None:
        """测试不同路径的 ConfigNotFoundException。"""
        paths = [
            "/home/user/.env",
            "C:\\config\\app.env",
            "./relative/path.env",
            "/very/long/path/to/configuration/file.env",
        ]

        for path in paths:
            exception = ConfigNotFoundException(path)
            assert path in exception.message
            assert path in str(exception)

    def test_config_not_found_exception_message_format(self) -> None:
        """测试 ConfigNotFoundException 消息格式。"""
        path = "/test/path"
        exception = ConfigNotFoundException(path)

        assert exception.message.startswith("Configuration file not found at path:")
        assert str(exception).startswith("[Exception]")


class TestEnvNotFoundException:
    """EnvNotFoundException 的测试用例。"""

    def test_env_not_found_exception_creation(self) -> None:
        """测试创建 EnvNotFoundException。"""
        env_key = "DATABASE_URL"
        exception = EnvNotFoundException(env_key)

        assert isinstance(exception, Exception)
        assert exception.message == f"Environment not found at key: {env_key}"
        assert str(exception) == f"[Exception] Environment not found at key: {env_key}"

    def test_env_not_found_exception_with_different_keys(self) -> None:
        """测试不同环境变量键的 EnvNotFoundException。"""
        keys = [
            "LOG_LEVEL",
            "API_SECRET_KEY",
            "REDIS_URL",
            "SMTP_PASSWORD",
            "JWT_SECRET",
        ]

        for key in keys:
            exception = EnvNotFoundException(key)
            assert key in exception.message
            assert key in str(exception)

    def test_env_not_found_exception_message_format(self) -> None:
        """测试 EnvNotFoundException 消息格式。"""
        env_key = "TEST_KEY"
        exception = EnvNotFoundException(env_key)

        assert exception.message.startswith("Environment not found at key:")
        assert str(exception).startswith("[Exception]")


class TestInvalidConfigException:
    """InvalidConfigException 的测试用例。"""

    def test_invalid_config_exception_creation(self) -> None:
        """测试创建 InvalidConfigException。"""
        details = "Port number must be between 1 and 65535"
        exception = InvalidConfigException(details)

        assert isinstance(exception, Exception)
        assert exception.message == f"Invalid configuration: {details}"
        assert str(exception) == f"[Exception] Invalid configuration: {details}"

    def test_invalid_config_exception_with_different_details(self) -> None:
        """测试不同详情的 InvalidConfigException。"""
        details_list = [
            "URL is not valid",
            "Database connection failed",
            "Missing required field: username",
            "Invalid JSON format in config file",
            "Timeout value cannot be negative",
        ]

        for details in details_list:
            exception = InvalidConfigException(details)
            assert details in exception.message
            assert details in str(exception)

    def test_invalid_config_exception_message_format(self) -> None:
        """测试 InvalidConfigException 消息格式。"""
        details = "Test details"
        exception = InvalidConfigException(details)

        assert exception.message.startswith("Invalid configuration:")
        assert str(exception).startswith("[Exception]")


class TestCreatTaskException:
    """CreatTaskException 的测试用例。"""

    def test_create_task_exception_creation(self) -> None:
        """测试创建 CreatTaskException。"""
        details = "API endpoint returned 500 error"
        exception = CreatTaskException(details)

        assert isinstance(exception, Exception)
        assert exception.message == f"Task creation failed: {details}"
        assert str(exception) == f"[Exception] Task creation failed: {details}"

    def test_create_task_exception_with_different_details(self) -> None:
        """测试不同详情的 CreatTaskException。"""
        details_list = [
            "Network timeout occurred",
            "Invalid project ID provided",
            "Insufficient permissions",
            "Rate limit exceeded",
            "Server maintenance in progress",
        ]

        for details in details_list:
            exception = CreatTaskException(details)
            assert details in exception.message
            assert details in str(exception)

    def test_create_task_exception_message_format(self) -> None:
        """测试 CreatTaskException 消息格式。"""
        details = "Test error details"
        exception = CreatTaskException(details)

        assert exception.message.startswith("Task creation failed:")
        assert str(exception).startswith("[Exception]")


class TestQueryTaskException:
    """QueryTaskException 的测试用例。"""

    def test_query_task_exception_creation(self) -> None:
        """测试创建 QueryTaskException。"""
        details = "Task ID not found in database"
        exception = QueryTaskException(details)

        assert isinstance(exception, Exception)
        assert exception.message == f"Querying task status failed: {details}"
        assert str(exception) == f"[Exception] Querying task status failed: {details}"

    def test_query_task_exception_with_different_details(self) -> None:
        """测试不同详情的 QueryTaskException。"""
        details_list = [
            "Database connection lost",
            "Task has been deleted",
            "Invalid task ID format",
            "Access denied for this task",
            "Query timeout exceeded",
        ]

        for details in details_list:
            exception = QueryTaskException(details)
            assert details in exception.message
            assert details in str(exception)

    def test_query_task_exception_message_format(self) -> None:
        """测试 QueryTaskException 消息格式。"""
        details = "Test query error"
        exception = QueryTaskException(details)

        assert exception.message.startswith("Querying task status failed:")
        assert str(exception).startswith("[Exception]")


class TestExceptionInteroperability:
    """测试异常之间的互操作性。"""

    def test_all_exceptions_are_exception_subclasses(self) -> None:
        """测试所有自定义异常都继承自 Exception。"""
        exceptions = [
            ConfigNotFoundException("test"),
            EnvNotFoundException("test"),
            InvalidConfigException("test"),
            CreatTaskException("test"),
            QueryTaskException("test"),
        ]

        for exception in exceptions:
            assert isinstance(exception, Exception)

    def test_exception_catching_with_base_exception(self) -> None:
        """测试使用基类 Exception 捕获自定义异常。"""
        exceptions = [
            ConfigNotFoundException("test"),
            EnvNotFoundException("test"),
            InvalidConfigException("test"),
            CreatTaskException("test"),
            QueryTaskException("test"),
        ]

        for exception in exceptions:
            try:
                raise exception
            except Exception as e:
                assert isinstance(e, type(exception))

    def test_exception_message_consistency(self) -> None:
        """测试异常消息的一致性。"""
        exceptions = [
            ConfigNotFoundException("test_path"),
            EnvNotFoundException("test_key"),
            InvalidConfigException("test_details"),
            CreatTaskException("test_details"),
            QueryTaskException("test_details"),
        ]

        for exception in exceptions:
            # 所有异常都应该有 message 属性
            assert hasattr(exception, "message")
            assert isinstance(exception.message, str)
            assert len(exception.message.strip()) > 0

            # 所有异常的 __str__ 方法都应该返回格式化的字符串
            str_repr = str(exception)
            assert str_repr.startswith("[Exception]")
            assert exception.message in str_repr

    def test_exception_args_parameter(self) -> None:
        """测试异常的 args 参数传递。"""
        test_message = "test message"
        exceptions = [
            ConfigNotFoundException("test_path"),
            EnvNotFoundException("test_key"),
            InvalidConfigException(test_message),
            CreatTaskException(test_message),
            QueryTaskException(test_message),
        ]

        for exception in exceptions:
            # 异常应该正确传递消息给父类
            assert len(exception.args) >= 1
            assert exception.message in exception.args[0]  # type: ignore[attr-defined]
