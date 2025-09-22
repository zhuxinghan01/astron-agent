# pylint: disable=invalid-name
"""
Third-party API error code definitions.

This module defines error codes returned by various third-party services
that are integrated with the workflow system. These codes represent the
raw error responses from external APIs before they are converted to
internal system error codes for consistent handling.

The error codes in this module are the original error codes returned by
external services and are used as input to the CodeConvert utility for
mapping to internal system error codes. This separation ensures that
external service changes don't directly impact the internal error handling
system.

Supported third-party services:
- Spark AI models and engines (comprehensive error coverage)
- Image generation services (format, schema, and audit errors)
- SparkLink tool services (initialization, protocol, and execution errors)
- Code execution environments (pod readiness and execution failures)
- Content audit services (compliance and violation detection)

Error Code Ranges by Service:
- Code execution: 1, 10405 (pod and execution errors)
- Image generation: 10003-10022 (format, schema, capacity, audit errors)
- SparkLink tools: 30001-30600 (initialization, protocol, execution errors)
- Spark models: 10000-11203 (WebSocket, auth, rate limiting, engine errors)
- Audit services: 999999 (internal audit service errors)

These codes are systematically organized to facilitate error mapping and
provide clear categorization for different types of external service failures.
"""
from enum import Enum


class ThirdApiCodeEnum(Enum):
    """
    Enumeration of third-party API error codes.

    Each error code is defined as a tuple containing:
    - code: Integer error code from third-party service
    - msg: Human-readable error message from the external service

    Error codes are organized by service type with specific ranges:
    - Code execution errors (10405, 1): Pod readiness and execution failures
    - Image generation errors (10003-10022): AI image generation service errors
    - SparkLink tool errors (30001-30600): External tool integration errors
    - Spark model errors (10000-11203): AI model service errors including WebSocket, auth, and rate limiting
    - Audit errors (999999): Content audit service internal errors

    These codes are used as input to the CodeConvert utility for mapping
    to internal system error codes.
    """

    Success = (0, "Success")

    # Code execution errors
    CodeExecutePodNotReadyError = (
        10405,
        "Pod is not ready yet, please try again later",
    )
    CodeExecuteError = (1, "exec code error::exit status 1")

    # Image generation errors
    ImageGenerateMsgFormatError = (10003, "User message format error")
    ImageGenerateSchemaError = (10004, "User data schema error")
    ImageGenerateParamsError = (10005, "User parameter value error")
    ImageGenerateSrvNotEnoughError = (10008, "Service capacity insufficient")
    ImageGenerateInputAuditError = (10021, "Input audit failed")
    ImageGenerateImageSensitivenessError = (
        10022,
        "Model generated image involves sensitive information, audit failed",
    )

    # SparkLink related errors
    SparkLinkAppInitErr = (30001, "Initialization failed")
    SparkLinkCommonErr = (30100, "General error")
    SparkLinkJsonProtocolParserErr = (30200, "JSON protocol parsing failed")
    SparkLinkJsonSchemaValidateErr = (30201, "Protocol validation failed")
    SparkLinkOpenapiSchemaValidateErr = (30300, "OpenAPI protocol parsing failed")
    SparkLinkOpenapiSchemaBodyTypeNotSupportErr = (30301, "Body type not supported")
    SparkLinkOpenapiSchemaServerNotExistErr = (30302, "Server does not exist")
    SparkLinkOfficialThirdApiRequestFailedErr = (30400, "Official tool request failed")
    SparkLinkThirdApiRequestFailedErr = (30403, "Third-party tool request failed")
    SparkLinkToolNotExistErr = (30500, "Tool does not exist")
    SparkLinkOperationIdNotExistErr = (30600, "Operation does not exist")

    # Spark model errors
    SparkWSError = (10000, "WebSocket upgrade error")
    SparkWSReadError = (10001, "WebSocket read user message error")
    SparkWSSendError = (10002, "WebSocket send message to user error")
    SparkMessageFormatError = (10003, "User message format error")
    SparkSchemaError = (10004, "User data schema error")
    SparkParamError = (10005, "User parameter value error")
    SparkConcurrencyError = (
        10006,
        "User concurrency error: current user is connected, same user cannot connect from multiple locations",
    )
    SparkTrafficLimitError = (
        10007,
        "User traffic limit: service is processing user's current question, wait for completion before sending new request",
    )
    SparkCapacityError = (10008, "Service capacity insufficient, contact staff")
    SparkEngineConnectionError = (10009, "Engine connection establishment failed")
    SparkEngineReceiveError = (10010, "Engine data receiving error")
    SparkEngineSendError = (10011, "Engine data sending error")
    SparkEngineInternalError = (10012, "Engine internal error")
    SparkContentAuditError = (
        10013,
        "Input content audit failed, suspected violation, please adjust input content",
    )
    SparkOutputAuditError = (
        10014,
        "Output content involves sensitive information, audit failed, results cannot be displayed to user",
    )
    SparkAppIdBlacklistError = (10015, "Appid is in blacklist")
    SparkAppIdAuthError = (
        10016,
        "Appid authorization error: feature not enabled, version not enabled, insufficient tokens, concurrency exceeds authorization",
    )
    SparkClearHistoryError = (10017, "Clear history failed")
    SparkViolationError = (
        10019,
        "Session content has violation tendency; suggest showing violation warning to user",
    )
    SparkBusyError = (10110, "Service busy, please try again later")
    SparkEngineParamsError = (
        10163,
        "Engine request parameter error, engine schema check failed",
    )
    SparkEngineNetworkError = (10222, "Engine network error")
    SparkTokenLimitError = (
        10907,
        "Token count exceeds limit, conversation history + question text too long, need to simplify input",
    )
    SparkAuthError = (
        11200,
        "Authorization error: appId has no feature authorization or business volume exceeds limit",
    )
    SparkDailyLimitError = (11201, "Authorization error: daily rate limit exceeded")
    SparkSecondLimitError = (
        11202,
        "Authorization error: second-level rate limit exceeded",
    )
    SparkConcurrencyLimitError = (
        11203,
        "Authorization error: concurrency limit exceeded",
    )

    # Audit related errors
    AuditError = (999999, "Server internal error")

    @property
    def code(self) -> int:
        """
        Get the numeric error code from third-party service.

        Returns the original integer error code as returned by the external API.
        This code is used as input to the CodeConvert utility for mapping to
        internal system error codes. The codes are organized by service type
        with specific ranges to facilitate error categorization and mapping.

        :return: Integer error code as returned by the external API
        """
        return self.value[0]

    @property
    def msg(self) -> str:
        """
        Get the error message from third-party service.

        Returns the original error message as returned by the external API.
        This message provides the raw error description from the third-party
        service and is used for reference during error mapping and debugging.
        The messages are typically in the language and format provided by
        the external service.

        :return: Error message as returned by the external API
        """
        return self.value[1]
