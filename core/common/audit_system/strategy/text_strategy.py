import asyncio
from typing import Literal

from common.audit_system.audit_api.base import ContentType, Stage
from common.audit_system.base import (
    FrameAuditResult,
    InputFrameAudit,
    OutputFrameAudit,
)
from common.audit_system.enums import Status
from common.audit_system.strategy.base_strategy import AuditStrategy
from common.audit_system.utils import ALL_SENTENCE_LEN, Sentence
from common.exceptions.codes import c9020
from common.exceptions.errs import AuditServiceException
from common.otlp.trace.span import Span

WORKFLOW_MAX_SENTENCE_LEN = 1500


class TextAuditStrategy(AuditStrategy):
    """
    文本送审策略实现，包括帧送审和首句送审。
    """

    async def input_review(self, input_frame: InputFrameAudit, span: Span):
        """
        输入内容审核逻辑。
        :param input_frame:
        :param span:         Span对象，用于跟踪请求的上下文信息。
        :return:
        """
        # 文本审核
        if input_frame.content_type == ContentType.TEXT:
            for audit_api in self.audit_apis:
                # 调用审核API进行内容审核
                await audit_api.input_text(
                    content=input_frame.content,
                    chat_sid=self.context.chat_sid,
                    span=span,
                    chat_app_id=self.context.chat_app_id,
                    uid=self.context.uid,
                    template_id=self.context.template_id,
                    context_list=input_frame.context_list,
                )
        else:
            raise ValueError("Unsupported content type for input review")

    async def output_review(self, output_frame: OutputFrameAudit, span: Span):
        """
        文本送审逻辑，分为首句送审和分句送审。
        :param output_frame
        :param span
        :return:
        """

        if not self.context.last_content_stage:
            self.context.last_content_stage = output_frame.stage

        if self.context.last_content_stage == output_frame.stage:
            self.context.remaining_content += output_frame.content

        self.context.add_source_content(output_frame)

        # 首句未送审，进行中间帧送审
        if not self.context.first_sentence_audited:
            span.add_info_event("↓↓↓↓↓↓↓↓↓↓↓ 首句送审 ↓↓↓↓↓↓↓↓↓↓↓")
            await self._first_sentence_audit(output_frame, span)

        # 首句送审完，走分句送审
        else:
            span.add_info_event("↓↓↓↓↓↓↓↓↓↓↓ 分句送审 ↓↓↓↓↓↓↓↓↓↓↓")
            await self._sentence_audit(output_frame, span)

    async def _first_sentence_audit(self, output_frame: OutputFrameAudit, span: Span):
        """
        首句送审逻辑。

        1. 在answer和reasoning_content转变时，置相应is_stage_end参数为1
        2. 在answer和reasoning_content转变时，如果answer或者reasoning_content所有内容返回
           不包含结束性标点符号甚至也没有非结束性标点符号，则拼接前面的answer或reasoning_content内容，
           组成首句或者分句送审。该情况会存在漏审情况。如示例中的“敏感词”则会正常上屏。

        :param output_frame:
        :return:
        """

        # 如果首句判断条件：有结束性标点，或者内容长度超过阈值，或者当前帧送审阶段和上次送审阶段不一致
        first_sentence_conditions = (
            Sentence.has_end_symbol(self.context.remaining_content)
            or len(self.context.remaining_content) > WORKFLOW_MAX_SENTENCE_LEN
            or self.context.last_content_stage != output_frame.stage
            or output_frame.status == Status.STOP
        )

        if self.context.last_content_stage == output_frame.stage:
            fallback_length = (
                WORKFLOW_MAX_SENTENCE_LEN
                if output_frame.status != Status.STOP
                else ALL_SENTENCE_LEN
            )
        else:
            fallback_length = ALL_SENTENCE_LEN

        # 中间帧被审核，后续帧不再送审，直到获取首帧
        if self.context.frame_blocked:
            span.add_info_event("中间帧被审核，后续帧不再送审，直到获取首帧")
            if first_sentence_conditions:
                await self.__first_sentence_audit(output_frame, span, fallback_length)
            else:
                pass

        # 取非结束性标志符号，送审
        elif first_sentence_conditions:
            await self.__first_sentence_audit(output_frame, span, fallback_length)

        # 如果没有达到首句送审条件，继续拼接内容，进行中间帧送审
        else:
            span.add_info_event("首句送审条件不满足，继续拼接内容，进行中间帧送审")
            frame_audit_result = FrameAuditResult(
                content=output_frame.content, source_frame=output_frame.source_frame
            )
            span.add_info_event(f"送审帧内容：{output_frame}")
            try:
                for audit_api in self.audit_apis:
                    span.add_info_event(f"当前审核API: {audit_api.audit_name}")
                    await audit_api.output_text(
                        stage=output_frame.stage,
                        content=self.context.remaining_content,
                        pindex=self.context.pindex,
                        span=span,
                        is_pending=1,  # 片段送审
                        is_stage_end=0,  # 当前阶段没有结束
                        is_end=0,  # 整体没有结束
                        chat_sid=self.context.chat_sid,
                        chat_app_id=self.context.chat_app_id,
                        uid=self.context.uid,
                    )
                self.context.frame_ids_on_screen.append(output_frame.frame_id)
                self.context.pindex += 1
                await self.context.output_queue_put(frame_audit_result, span)
            except Exception:
                self.context.frame_blocked = True

        if self.context.last_content_stage != output_frame.stage:
            self.context.last_content_stage = output_frame.stage
            await self.output_review(output_frame, span)

    async def __first_sentence_audit(
        self, output_frame: OutputFrameAudit, span: Span, fallback_length: int
    ):
        span.add_info_event("首句送审条件满足，进行首句送审")
        # 当前帧不需要分句，则全部送审
        if output_frame.not_need_submit:
            sentences = [self.context.remaining_content]
            self.context.remaining_content = ""
        else:
            sentences, self.context.remaining_content = Sentence.find_valid_sentence(
                self.context.remaining_content, fallback_length=fallback_length
            )
        sentences = (
            [""]
            if (
                (
                    # 结束帧或者reasoning和answer帧发生变化，但是分句内容为空，需要单独给个空句送审
                    output_frame.status == Status.STOP
                    or self.context.last_content_stage != output_frame.stage
                )
                and not sentences
            )
            else sentences
        )
        span.add_info_event("分句结果如下：")
        span.add_info_events(
            {
                "sentences": sentences,
                "remaining_content": self.context.remaining_content,
            }
        )
        # 首句送审时，pindex需要重置为1
        self.context.pindex = 1
        await self._audit_api_output_text_async(sentences, output_frame, span)
        self.context.first_sentence_audited = True

    async def _sentence_audit(self, output_frame: OutputFrameAudit, span: Span):
        """
        分句送审。
        :param output_frame:
        :return:
        """

        # 送审content
        if (
            Sentence.has_end_symbol(self.context.remaining_content)
            or len(self.context.remaining_content) > WORKFLOW_MAX_SENTENCE_LEN
            or self.context.last_content_stage != output_frame.stage
            or output_frame.status == Status.STOP
        ):
            sentences = []

            # 当前帧不需要分句，则全部送审
            if output_frame.not_need_submit:
                sentences = [self.context.remaining_content]
                self.context.remaining_content = ""

            # 如果当前帧送审阶段和上次送审阶段不一致，需要把剩余的文本分句后全部送审
            elif (
                self.context.last_content_stage != output_frame.stage
                or output_frame.status == Status.STOP
            ):
                while True:
                    sentences_temp, self.context.remaining_content = (
                        Sentence.find_valid_sentence(
                            self.context.remaining_content, WORKFLOW_MAX_SENTENCE_LEN
                        )
                    )
                    sentences.extend(sentences_temp)
                    if not self.context.remaining_content:
                        break
                # 当前帧送审阶段和上次送审阶段不一致，也没有送审内容，需要补上空帧，用于is stage end送审
                if not sentences:
                    sentences.append("")
            else:
                sentences, self.context.remaining_content = (
                    Sentence.find_valid_sentence(
                        self.context.remaining_content, WORKFLOW_MAX_SENTENCE_LEN
                    )
                )

            # 结束帧送审内容可能为空，需要增加空字符串
            if (
                output_frame.status == Status.STOP
                and not sentences
                and not self.context.remaining_content
            ):
                sentences.append("")

            await self._audit_api_output_text_async(sentences, output_frame, span)

        # 不一致的stage全部送审完，在送审当前的送审帧
        if self.context.last_content_stage != output_frame.stage:
            self.context.last_content_stage = output_frame.stage
            await self.output_review(output_frame, span)

    async def _audit_api_output_text_async(
        self, sentences: list[str], output_frame: OutputFrameAudit, span: Span
    ):
        """
        异步文本输出审核API调用
        :param sentences:       分句
        :param output_frame:    当前帧信息
        :param span:
        :return:
        """
        current_status = output_frame.status
        pindex = self.context.pindex
        audit_tasks = []

        for idx, sentence in enumerate(sentences):
            # 如果当前帧是结束帧，则最后一个分句需要标记为结束帧
            if current_status == Status.STOP:
                output_frame.status = (
                    Status.STOP if idx == len(sentences) - 1 else Status.NONE
                )

            audit_tasks.append(
                asyncio.create_task(
                    self._audit_api_output_text(
                        output_frame.stage,
                        sentence,
                        span,
                        pindex + idx + 1,
                        current_status=output_frame.status,
                    ),
                )
            )
        _ = await asyncio.gather(*audit_tasks)
        self.context.pindex += len(sentences)
        self.context.audited_content += "".join(sentences)
        for _ in range(len(sentences)):
            await self.context.add_audited_content(span)

    async def _audit_api_output_text(
        self,
        current_stage: Stage,
        need_audit_content: str,
        span: Span,
        pindex: int,
        current_status: Status = Status.NONE,
    ):
        """
        文本输出审核API调用
        :param current_stage:
        :param need_audit_content:
        :param span:
        :param pindex:
        :param current_status:
        :return:
        """
        if self.context.error:
            span.add_info_event(f"审核上下文错误: {self.context.error}, 后续帧不再送审")
            return

        span.add_info_event(f"当前送审内容: {need_audit_content}")
        frame_audit_result = FrameAuditResult(
            content=need_audit_content, status=current_status
        )

        is_end: Literal[0, 1] = 0
        is_stage_end: Literal[0, 1] = 0

        if self.context.last_content_stage == current_stage:
            is_end = 1 if current_status == Status.STOP else 0

            if current_status == Status.STOP:
                is_stage_end = 1

        if self.context.last_content_stage != current_stage:
            is_stage_end = 1

        try:
            for audit_api in self.audit_apis:
                span.add_info_event(f"当前审核API: {audit_api.audit_name}")
                stage_arg = (
                    current_stage
                    if self.context.last_content_stage == current_stage
                    else self.context.last_content_stage
                )

                if stage_arg is None:
                    raise AuditServiceException(*c9020)("stage不可为空")
                await audit_api.output_text(
                    stage=stage_arg,
                    content=need_audit_content,
                    pindex=pindex,
                    span=span,
                    is_pending=0,  # 首句送审不需要标记为不完整
                    is_stage_end=is_stage_end,
                    is_end=is_end,
                    chat_sid=self.context.chat_sid,
                    chat_app_id=self.context.chat_app_id,
                    uid=self.context.uid,
                )
        except AuditServiceException as e:
            frame_audit_result.error = e
            span.add_error_event(f"审核API调用异常: {str(e)}")
            await self.context.output_queue_put(frame_audit_result, span)
        except Exception as e:
            span.add_error_event(f"审核API调用异常: {str(e)}")
            frame_audit_result.error = AuditServiceException(*c9020)(
                f"审核结果异常: {str(e)}"
            )
            await self.context.output_queue_put(frame_audit_result, span)
        finally:
            if frame_audit_result.error:
                self.context.error = frame_audit_result.error
