"""
base.py
"""

import asyncio
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from common.audit_system.audit_api.base import ContentType, ContextList, Stage
from common.audit_system.enums import Status
from common.exceptions.errs import AuditServiceException

# 使用TYPE_CHECKING避免循环导入
if TYPE_CHECKING:
    from common.otlp.trace.span import Span


class BaseFrameAudit(BaseModel):
    """
    基础帧审核对象，包含通用属性。
    """

    # 审核内容，需要送审的文本。
    content: str

    # 当前送审内容状态
    status: Status = Status.STOP


class InputFrameAudit(BaseFrameAudit):
    """
    输入帧送审
    """

    content_type: ContentType = ContentType.TEXT
    context_list: list[ContextList] = Field(default_factory=list)


class OutputFrameAudit(BaseFrameAudit):
    """
    输出帧送审
    """

    # 送审帧的ID，可以不传，如果使用该ID，需要保证唯一
    frame_id: str = ""

    stage: Stage

    # 原始帧内容
    source_frame: Any

    # 不需要分句
    not_need_submit: bool = False

    # 针对空针是否需要送审
    none_need_audit: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FrameAuditResult(BaseFrameAudit):
    """
    帧审核结果对象，包含审核状态和内容。
    """

    # 原始帧内容
    source_frame: Any = None

    error: Optional[AuditServiceException] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class AuditContext(BaseModel):
    """
    审核上下文，维护当前会话状态，包括：
    - 所有帧拼接内容
    - 当前首句缓存
    - 是否因某一帧审核失败而停止帧审核
    """

    chat_sid: str

    # 模板ID，用于管理控制台配置的审核策略模板，一个大模型场景使用一个模板ID，缺省则使用默认的标准策略模版。
    template_id: str = ""

    # 大模型应用ID，透传参数，上游分配给大模型调用方的账号标识，用于区分调用方。
    chat_app_id: str = ""

    # 用户ID，透传参数，用于区分指定的用户。
    uid: str = ""

    # 输出队列，队列中存储的数据结构为 FrameAuditResult，针对流式输出内容，需要监听该队列
    output_queue: asyncio.Queue[Any] = Field(default_factory=asyncio.Queue)  # type: ignore[misc]

    # 审核结果异常包装
    error: Optional[AuditServiceException] = None

    # 输出文本片段索引，表明当前文本是第几片文本，从1开始，建议业务方按照结束标点或段落拆分片段。
    pindex: int = 1

    # 是否已经首句送审
    first_sentence_audited: bool = False

    # 是否被某帧命中敏感词阻断
    frame_blocked: bool = False

    # 待送审内容
    remaining_content: str = ""

    # 所有送审数据
    all_content_frame_ids: List[str] = Field(default_factory=list)  # type: ignore[misc]
    all_source_frames: Dict[str, OutputFrameAudit] = Field(default_factory=dict)  # type: ignore[misc]

    # 审核完成的内容
    audited_content: str = ""
    # 审核完成的帧ID列表
    audited_content_frame_ids: List[str] = Field(default_factory=list)  # type: ignore[misc]

    # 帧送审上屏完成的帧ID
    frame_ids_on_screen: List[str] = Field(default_factory=list)  # type: ignore[misc]

    # 上一次送审类型
    last_content_stage: Optional[Stage] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def add_source_content(self, output_frame: OutputFrameAudit):
        """
        添加原始帧内容到上下文中。
        :param output_frame: 输出帧送审对象
        """
        if output_frame.frame_id not in self.all_content_frame_ids:
            self.all_content_frame_ids.append(output_frame.frame_id)
            self.audited_content_frame_ids.append(output_frame.frame_id)
            self.all_source_frames[output_frame.frame_id] = output_frame

    async def add_audited_content(self, span: "Span"):
        """
        添加已审核完成的内容
        :param status: 当前状态
        :param span: Span对象，用于跟踪请求的上下文信息
        """
        is_all_consumer = True
        for idx, frame_id in enumerate(self.audited_content_frame_ids):
            output_frame_audit = self.all_source_frames[frame_id]
            if (
                output_frame_audit.content
                == self.audited_content[: len(output_frame_audit.content)]
            ):
                if output_frame_audit.frame_id not in self.frame_ids_on_screen:
                    frame_audit_result = FrameAuditResult(
                        content=output_frame_audit.content,
                        source_frame=output_frame_audit.source_frame,
                    )
                    await self.output_queue_put(frame_audit_result, span)
                self.audited_content = self.audited_content[
                    len(output_frame_audit.content) :
                ]
            else:
                self.audited_content_frame_ids = self.audited_content_frame_ids[idx:]
                is_all_consumer = False
                break
        if is_all_consumer:
            self.audited_content_frame_ids = []

    async def output_queue_put(
        self, frame_audit_result: FrameAuditResult, span: "Span"
    ):
        """
        将审核结果放入输出队列。
        :param frame_audit_result: 帧审核结果对象
        """
        # print(id(self.output_queue))
        # print(f"当前可上屏内容: {frame_audit_result.content}")
        event = f"当前可上屏内容: {frame_audit_result.content}"
        if frame_audit_result.error:
            event = f"{event}, 该上屏存在风险，风险信息: {frame_audit_result.error}"
        span.add_info_event(event)
        await self.output_queue.put(frame_audit_result)
