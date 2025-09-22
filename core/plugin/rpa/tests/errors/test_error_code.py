"""测试错误码定义模块。"""

import pytest

from errors.error_code import ErrorCode


class TestErrorCode:
    """ErrorCode 枚举的测试用例。"""

    def test_success_error_code(self) -> None:
        """测试成功错误码。"""
        assert ErrorCode.SUCCESS.code == 0
        assert ErrorCode.SUCCESS.message == "Success"
        assert str(ErrorCode.SUCCESS) == "code: 0, msg: Success"

    def test_failure_error_code(self) -> None:
        """测试失败错误码。"""
        assert ErrorCode.FAILURE.code == 55000
        assert ErrorCode.FAILURE.message == "Failure"
        assert str(ErrorCode.FAILURE) == "code: 55000, msg: Failure"

    def test_create_task_error_code(self) -> None:
        """测试创建任务错误码。"""
        assert ErrorCode.CREATE_TASK_ERROR.code == 55001
        assert ErrorCode.CREATE_TASK_ERROR.message == "Create task error"
        assert str(ErrorCode.CREATE_TASK_ERROR) == "code: 55001, msg: Create task error"

    def test_query_task_error_code(self) -> None:
        """测试查询任务错误码。"""
        assert ErrorCode.QUERY_TASK_ERROR.code == 55002
        assert ErrorCode.QUERY_TASK_ERROR.message == "Query task error"
        assert str(ErrorCode.QUERY_TASK_ERROR) == "code: 55002, msg: Query task error"

    def test_timeout_error_code(self) -> None:
        """测试超时错误码。"""
        assert ErrorCode.TIMEOUT_ERROR.code == 55003
        assert ErrorCode.TIMEOUT_ERROR.message == "Timeout error"
        assert str(ErrorCode.TIMEOUT_ERROR) == "code: 55003, msg: Timeout error"

    def test_unknown_error_code(self) -> None:
        """测试未知错误码。"""
        assert ErrorCode.UNKNOWN_ERROR.code == 55999
        assert ErrorCode.UNKNOWN_ERROR.message == "Unknown error"
        assert str(ErrorCode.UNKNOWN_ERROR) == "code: 55999, msg: Unknown error"

    def test_error_code_range(self) -> None:
        """测试错误码在预期范围内。"""
        # 除了成功代码(0)外，所有错误码应该在 55000-59999 范围内
        for error_code in ErrorCode:
            if error_code != ErrorCode.SUCCESS:
                assert (
                    55000 <= error_code.code <= 59999
                ), f"Error code {error_code.code} is out of range"

    def test_error_code_uniqueness(self) -> None:
        """测试错误码的唯一性。"""
        codes = [error_code.code for error_code in ErrorCode]
        assert len(codes) == len(set(codes)), "Error codes should be unique"

    def test_error_code_properties_not_none(self) -> None:
        """测试错误码属性不为空。"""
        for error_code in ErrorCode:
            assert error_code.code is not None
            assert error_code.message is not None
            assert error_code.message.strip() != ""

    def test_error_code_enum_values(self) -> None:
        """测试枚举值结构。"""
        for error_code in ErrorCode:
            assert isinstance(error_code.value, tuple)
            assert len(error_code.value) == 2
            assert isinstance(error_code.value[0], int)  # code
            assert isinstance(error_code.value[1], str)  # message

    def test_error_code_comparison(self) -> None:
        """测试错误码比较。"""
        assert ErrorCode.SUCCESS == ErrorCode.SUCCESS
        assert ErrorCode.SUCCESS != ErrorCode.FAILURE
        assert ErrorCode.CREATE_TASK_ERROR != ErrorCode.QUERY_TASK_ERROR

    def test_error_code_in_collection(self) -> None:
        """测试错误码在集合中的使用。"""
        error_codes = {ErrorCode.SUCCESS, ErrorCode.FAILURE, ErrorCode.TIMEOUT_ERROR}
        assert ErrorCode.SUCCESS in error_codes
        assert ErrorCode.CREATE_TASK_ERROR not in error_codes

    def test_all_error_codes_accessible(self) -> None:
        """测试所有错误码都可以访问。"""
        expected_error_codes = [
            "SUCCESS",
            "FAILURE",
            "CREATE_TASK_ERROR",
            "QUERY_TASK_ERROR",
            "TIMEOUT_ERROR",
            "UNKNOWN_ERROR",
        ]

        for error_name in expected_error_codes:
            assert hasattr(
                ErrorCode, error_name
            ), f"ErrorCode.{error_name} should exist"
            error_code = getattr(ErrorCode, error_name)
            assert isinstance(error_code, ErrorCode)
