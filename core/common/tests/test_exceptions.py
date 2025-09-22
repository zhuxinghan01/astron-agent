"""
Unit tests for common.exceptions module.
"""

import pytest

from common.exceptions.base import BaseExc
from common.exceptions.codes import c9000, c9001, c9010, c9020, c9021, c9022, c9023
from common.exceptions.errs import (
    AuditServiceException,
    BaseCommonException,
    OssServiceException,
)


class TestBaseExc:
    """Test BaseExc exception class."""

    def test_init_basic(self):
        """Test basic initialization."""
        exc = BaseExc(40021, "LLM结果解析异常")
        assert exc.c == 40021
        assert exc.m == "LLM结果解析异常"
        assert exc.oc == 0
        assert exc.om == ""
        assert exc.on == ""
        assert exc.kwargs == {}

    def test_init_with_origin(self):
        """Test initialization with origin parameters."""
        exc = BaseExc(
            c=40021,
            m="LLM结果解析异常",
            oc=50001,
            om="原始错误信息",
            on="原始系统",
            extra="test",
        )
        assert exc.c == 40021
        assert exc.m == "LLM结果解析异常"
        assert exc.oc == 50001
        assert exc.om == "原始错误信息"
        assert exc.on == "原始系统"
        assert exc.kwargs == {"extra": "test"}

    def test_call_with_append_message(self):
        """Test __call__ method with append message."""
        exc = BaseExc(40021, "LLM结果解析异常")
        new_exc = exc("大模型推理格式不正确")

        assert new_exc.c == 40021
        assert new_exc.m == "LLM结果解析异常,大模型推理格式不正确"
        assert new_exc.oc == 0
        assert new_exc.om == ""
        assert new_exc.on == ""

    def test_call_with_override_parameters(self):
        """Test __call__ method with parameter override."""
        exc = BaseExc(40021, "LLM结果解析异常")
        new_exc = exc(
            c=40022, m="新的错误信息", oc=50002, om="新的原始错误", on="新的原始系统"
        )

        assert new_exc.c == 40021  # c should not be overridden
        assert new_exc.m == "LLM结果解析异常"  # m should not be overridden
        assert new_exc.oc == 0  # oc should not be overridden
        assert new_exc.om == ""  # om should not be overridden
        assert new_exc.on == ""  # on should not be overridden

    def test_call_with_kwargs(self):
        """Test __call__ method with additional kwargs."""
        exc = BaseExc(40021, "LLM结果解析异常")
        new_exc = exc(extra_param="test_value", another_param=123)

        assert new_exc.kwargs == {"extra_param": "test_value", "another_param": 123}

    def test_repr(self):
        """Test __repr__ method."""
        exc = BaseExc(40021, "LLM结果解析异常")
        assert repr(exc) == "40021: LLM结果解析异常"

    def test_str(self):
        """Test __str__ method."""
        exc = BaseExc(40021, "LLM结果解析异常")
        assert str(exc) == "40021: LLM结果解析异常"


class TestExceptionCodes:
    """Test exception codes."""

    def test_c9000(self):
        """Test c9000 code."""
        assert c9000 == (9000, "登录polaris失败")

    def test_c9001(self):
        """Test c9001 code."""
        assert c9001 == (9001, "未知异常")

    def test_c9010(self):
        """Test c9010 code."""
        assert c9010 == (9010, "oss服务失败")

    def test_c9020(self):
        """Test c9020 code."""
        assert c9020 == (9020, "审核异常")

    def test_c9021(self):
        """Test c9021 code."""
        assert c9021 == (9021, "审核服务异常")

    def test_c9022(self):
        """Test c9022 code."""
        assert c9022 == (9022, "输入内容审核不通过，涉嫌违规，请重新调整输入内容")

    def test_c9023(self):
        """Test c9023 code."""
        assert c9023 == (
            9023,
            "输出内容涉及敏感信息，审核不通过，后续结果无法展示给用户",
        )


class TestCommonExceptions:
    """Test common exception classes."""

    def test_base_common_exception(self):
        """Test BaseCommonException."""
        exc = BaseCommonException(40021, "测试异常")
        assert isinstance(exc, BaseExc)
        assert exc.c == 40021
        assert exc.m == "测试异常"

    def test_oss_service_exception(self):
        """Test OssServiceException."""
        exc = OssServiceException(40021, "OSS服务异常")
        assert isinstance(exc, BaseCommonException)
        assert isinstance(exc, BaseExc)
        assert exc.c == 40021
        assert exc.m == "OSS服务异常"

    def test_audit_service_exception(self):
        """Test AuditServiceException."""
        exc = AuditServiceException(40021, "审核服务异常")
        assert isinstance(exc, BaseCommonException)
        assert isinstance(exc, BaseExc)
        assert exc.c == 40021
        assert exc.m == "审核服务异常"

    def test_exception_inheritance(self):
        """Test exception inheritance chain."""
        oss_exc = OssServiceException(40021, "OSS异常")
        audit_exc = AuditServiceException(40022, "审核异常")

        assert isinstance(oss_exc, BaseCommonException)
        assert isinstance(oss_exc, BaseExc)
        assert isinstance(audit_exc, BaseCommonException)
        assert isinstance(audit_exc, BaseExc)

        # Test that they are different types
        assert type(oss_exc) != type(audit_exc)
