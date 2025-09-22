"""测试常量定义模块。"""

import pytest

from consts import const


class TestConstModule:
    """常量模块的测试用例。"""

    def test_uvicorn_constants_exist(self) -> None:
        """测试 Uvicorn 相关常量存在。"""
        uvicorn_constants = [
            "UVICORN_APP_KEY",
            "UVICORN_HOST_KEY",
            "UVICORN_PORT_KEY",
            "UVICORN_RELOAD_KEY",
            "UVICORN_WORKERS_KEY",
            "UVICORN_WS_PING_INTERVAL_KEY",
            "UVICORN_WS_PING_TIMEOUT_KEY",
        ]

        for constant in uvicorn_constants:
            assert hasattr(const, constant), f"Constant {constant} should exist"
            value = getattr(const, constant)
            assert isinstance(value, str), f"Constant {constant} should be a string"
            assert len(value.strip()) > 0, f"Constant {constant} should not be empty"

    def test_log_constants_exist(self) -> None:
        """测试日志相关常量存在。"""
        log_constants = ["LOG_LEVEL_KEY", "LOG_PATH_KEY"]

        for constant in log_constants:
            assert hasattr(const, constant), f"Constant {constant} should exist"
            value = getattr(const, constant)
            assert isinstance(value, str), f"Constant {constant} should be a string"
            assert len(value.strip()) > 0, f"Constant {constant} should not be empty"

    def test_rpa_constants_exist(self) -> None:
        """测试 RPA 相关常量存在。"""
        rpa_constants = [
            "RPA_PING_INTERVAL_KEY",
            "RPA_TASK_CREATE_URL_KEY",
            "RPA_TASK_QUERY_INTERVAL_KEY",
            "RPA_TASK_QUERY_URL_KEY",
            "RPA_TIMEOUT_KEY",
        ]

        for constant in rpa_constants:
            assert hasattr(const, constant), f"Constant {constant} should exist"
            value = getattr(const, constant)
            assert isinstance(value, str), f"Constant {constant} should be a string"
            assert len(value.strip()) > 0, f"Constant {constant} should not be empty"

    def test_all_constants_in_all_list(self) -> None:
        """测试所有常量都在 __all__ 列表中。"""
        expected_constants = [
            "UVICORN_APP_KEY",
            "UVICORN_HOST_KEY",
            "UVICORN_PORT_KEY",
            "UVICORN_RELOAD_KEY",
            "UVICORN_WS_PING_INTERVAL_KEY",
            "UVICORN_WS_PING_TIMEOUT_KEY",
            "UVICORN_WORKERS_KEY",
            "LOG_LEVEL_KEY",
            "LOG_PATH_KEY",
            "RPA_PING_INTERVAL_KEY",
            "RPA_TASK_CREATE_URL_KEY",
            "RPA_TASK_QUERY_INTERVAL_KEY",
            "RPA_TASK_QUERY_URL_KEY",
            "RPA_TIMEOUT_KEY",
        ]

        assert hasattr(const, "__all__"), "Module should have __all__ list"
        assert isinstance(const.__all__, list), "__all__ should be a list"

        for constant in expected_constants:
            assert (
                constant in const.__all__
            ), f"Constant {constant} should be in __all__"

    def test_all_list_completeness(self) -> None:
        """测试 __all__ 列表的完整性。"""
        # 获取模块中所有公共属性（不以下划线开头）
        public_attributes = [attr for attr in dir(const) if not attr.startswith("_")]

        # 过滤掉导入的模块和其他非常量属性
        constants = [
            attr
            for attr in public_attributes
            if attr.isupper() and attr.endswith("_KEY")
        ]

        for constant in constants:
            assert (
                constant in const.__all__
            ), f"Public constant {constant} should be in __all__"

    def test_constant_naming_convention(self) -> None:
        """测试常量命名约定。"""
        for constant_name in const.__all__:
            # 常量应该全部大写
            assert (
                constant_name.isupper()
            ), f"Constant {constant_name} should be uppercase"

            # 常量应该以 _KEY 结尾
            assert constant_name.endswith(
                "_KEY"
            ), f"Constant {constant_name} should end with _KEY"

            # 常量名应该包含下划线分隔符
            assert (
                "_" in constant_name
            ), f"Constant {constant_name} should contain underscores"

    def test_constant_values_uniqueness(self) -> None:
        """测试常量值的唯一性。"""
        values = []
        for constant_name in const.__all__:
            value = getattr(const, constant_name)
            values.append(value)

        # 检查是否有重复值
        unique_values = set(values)
        assert len(values) == len(unique_values), "All constant values should be unique"

    def test_constant_values_format(self) -> None:
        """测试常量值的格式。"""
        for constant_name in const.__all__:
            value = getattr(const, constant_name)

            # 所有常量值都应该是字符串
            assert isinstance(
                value, str
            ), f"Constant {constant_name} value should be a string"

            # 常量值不应该为空
            assert (
                len(value.strip()) > 0
            ), f"Constant {constant_name} value should not be empty"

            # 常量值应该是有效的环境变量名格式
            assert (
                value.replace("_", "").replace("-", "").isalnum()
            ), f"Constant {constant_name} value should be a valid environment variable name"

    def test_import_structure(self) -> None:
        """测试导入结构的正确性。"""
        # 验证可以从子模块导入常量
        from consts.app.uvicorn_keys import UVICORN_APP_KEY
        from consts.log.log_keys import LOG_LEVEL_KEY
        from consts.rpa.rpa_keys import RPA_TIMEOUT_KEY

        # 验证导入的常量与主模块中的常量一致
        assert UVICORN_APP_KEY == const.UVICORN_APP_KEY
        assert LOG_LEVEL_KEY == const.LOG_LEVEL_KEY
        assert RPA_TIMEOUT_KEY == const.RPA_TIMEOUT_KEY

    def test_module_docstring(self) -> None:
        """测试模块文档字符串。"""
        assert const.__doc__ is not None, "Module should have a docstring"
        assert (
            "常量定义模块" in const.__doc__
        ), "Docstring should describe the module purpose"
