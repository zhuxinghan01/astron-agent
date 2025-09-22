"""错误码定义模块。
本模块定义了 RPA 服务中使用的所有错误码。"""

from enum import Enum


class ErrorCode(Enum):
    """RPA 服务的错误码定义。"""

    # 定义成功和失败的错误码
    SUCCESS = (0, "Success")
    FAILURE = (55000, "Failure")
    # 错误码范围, 55000 - 59999

    CREATE_TASK_ERROR = (55001, "Create task error")
    QUERY_TASK_ERROR = (55002, "Query task error")
    TIMEOUT_ERROR = (55003, "Timeout error")

    UNKNOWN_ERROR = (55999, "Unknown error")

    # 返回错误码
    @property
    def code(self) -> int:
        """返回错误码。"""
        return self.value[0]

    # 返回错误信息
    @property
    def message(self) -> str:
        """返回错误信息。"""
        return self.value[1]

    def __str__(self) -> str:
        return f"code: {self.code}, msg: {self.message}"
