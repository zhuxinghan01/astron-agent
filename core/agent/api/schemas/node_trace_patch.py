import time
from typing import Generic, TypeVar

from pydantic import ConfigDict, Field

# 使用统一的 common 包导入模块
from common_imports import NodeLog, NodeTraceLog

T = TypeVar("T", bound=NodeLog)


class NodeTracePatch(NodeTraceLog, Generic[T]):
    # Use type: ignore to handle the invariant List type incompatibility
    trace: list[T] = Field(default_factory=list)  # type: ignore[assignment]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def record_start(self):
        """记录开始时间"""
        self.start_time = int(time.time() * 1000)

    def record_end(self):
        """记录结束时间并计算持续时间"""
        self.set_end()  # 使用父类的 set_end 方法

    def upload(self, status, log_caller: str, span):
        """
        上传node trace日志
        为了兼容原有代码，提供此方法
        """
        # 设置状态
        self.set_status(status.code, status.message)

        # 返回序列化的数据
        return self.model_dump()
