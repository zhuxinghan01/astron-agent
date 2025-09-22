# pylint: disable=invalid-name
"""
Error code definitions for the workflow system.

This module defines all error codes used throughout the workflow system,
organized by functional categories. Each error code includes both a numeric
code and a descriptive message for consistent error handling and user feedback.

The error codes are structured hierarchically with specific ranges for
different functional areas, making it easy to identify and handle errors
appropriately throughout the system. This systematic organization enables:

- Easy error identification and categorization
- Consistent error handling across all system components
- Simplified debugging and troubleshooting
- Clear error reporting to users and administrators
- Integration with monitoring and alerting systems

Error Code Ranges:
- 200-500: HTTP status codes and basic system responses
- 20000-20008: Application-level errors (configuration, binding, etc.)
- 20100-20104: Protocol validation and management errors
- 20201-20209: Workflow execution and management errors
- 20301-20376: AI model service errors (Spark, WebSocket, auth, rate limiting)
- 20400: WebSocket communication errors
- 20500-20502: Knowledge base and retrieval errors
- 20600-20602: Variable system management errors
- 20700: Database operation errors
- 20804-20805: OpenAPI integration errors
- 20900-20905: Authentication and authorization errors
- 21000-21002: PostgreSQL database-specific errors
- 21100-21104: Content audit and compliance errors
- 21200-21209: AI image generation service errors
- 21500: Chat system communication errors
- 21600-21603: Code interpreter execution errors
- 21700: Node debugging and development errors
- 21800-21812: External tool integration errors (SparkLink)
- 22100-22101: Workflow engine protocol validation errors
- 22300-22303: Workflow engine execution errors
- 22500-23900: Individual node type execution errors

Error code wiki documentation:
http://wiki.iflytek.com/pages/editpage.action?pageId=573285627
"""
from enum import Enum


class CodeEnum(Enum):
    """
    Enumeration of all error codes used in the workflow system.

    Each error code is defined as a tuple containing:
    - code: Integer error code for programmatic identification
    - msg: Human-readable error message for user feedback

    Error codes are organized by functional categories with specific ranges:
    - HTTP status codes (200, 500): Basic HTTP response codes
    - Application errors (20000-20008): Application-level configuration and binding issues
    - Protocol errors (20100-20104): Protocol validation and management errors
    - Flow errors (20201-20209): Workflow execution and management errors
    - Spark model errors (20301-20376): AI model service errors including WebSocket, auth, and rate limiting
    - WebSocket errors (20400): Real-time communication errors
    - Knowledge base errors (20500-20502): Knowledge retrieval and processing errors
    - Variable pool errors (20600-20602): Variable system management errors
    - Database errors (20700): Database operation errors
    - OpenAPI errors (20804-20805): OpenAPI integration errors
    - Authentication errors (20900-20905): Authentication and authorization errors
    - PostgreSQL errors (21000-21002): Database-specific errors
    - Audit errors (21100-21104): Content audit and compliance errors
    - Image generation errors (21200-21209): AI image generation service errors
    - Chat errors (21500): Chat system communication errors
    - Code execution errors (21600-21603): Code interpreter execution errors
    - Node debug errors (21700): Node debugging and development errors
    - SparkLink tool errors (21800-21812): External tool integration errors
    - Engine protocol errors (22100-22101): Workflow engine protocol validation errors
    - Engine errors (22300-22303): Workflow engine execution errors
    - Node-specific errors (22500-23900): Individual node type execution errors
    """

    HttpSuccess = (200, "success")
    HttpError = (500, "Server error")

    Successes = (0, "Success")

    ParamError = (460, "Parameter validation error")

    # Application errors
    AppNotFound = (20000, "Application not found")
    AppGetWithRemoteFailed = (
        20001,
        "Failed to get application from management platform",
    )
    AppTenantNotFound = (20002, "Application tenant not found")
    AppTenantPlatformUnauthorized = (
        20003,
        "Application tenant has no platform permission",
    )
    AppFlowNotAuthBondErr = (20004, "Application not bound to workflow")
    AppFlowNoLicenseErr = (20005, "Appid is prohibited from using this workflow")
    AppPlatNotReleaseOpr = (20006, "Platform has no corresponding operation")
    AppFlowAuthBondErr = (20007, "Application binding failed")
    AppUnknownSourceErr = (20008, "Unknown application source")

    # Protocol errors
    ProtocolValidationErr = (20100, "Protocol validation failed")
    ProtocolParameterError = (20101, "Protocol parameter error")
    ProtocolCreateError = (20102, "Protocol creation error")
    ProtocolDeleteError = (20103, "Protocol deletion error")
    ProtocolUpdateError = (20104, "Protocol update failed")
    ProtocolBuildError = (20104, "Protocol build failed")

    # Flow errors
    FlowIDNotFound = (20201, "Flow ID not found")
    FlowIDTypeErr = (20202, "Invalid Flow ID")
    FlowHChatFailed = (20203, "Chat error")
    FlowNotPublish = (20204, "Workflow not published")
    FlowNoAppID = (20205, "Workflow has no appid")
    FlowPublishErr = (20206, "Workflow publish failed")
    OpenApiFlowStatusError = (20207, "Workflow is in draft status")
    FlowVersionError = (20208, "Flow version not found")
    FlowGetError = (20209, "Workflow retrieval failed")

    # Spark model errors
    SparkFunctionNotChoiceError = (20301, "Model did not select valid function")
    SparkQuickRepairError = (20302, "Model hit specific issue")
    SparkRequestError = (20303, "Model request failed")
    # Spark service error code mapping 20350-20376
    SparkWSError = (20350, "Model request upgrade to WebSocket error")
    SparkWSReadError = (20351, "Model request WebSocket read user message error")
    SparkWSSendError = (20352, "Model request WebSocket send message to user error")
    SparkMessageFormatError = (20353, "Model request user message format error")
    SparkSchemaError = (20354, "Model request user data schema error")
    SparkParamError = (20355, "Model request user parameter value error")
    SparkConcurrencyError = (
        20356,
        "Model service user concurrency error: current user is connected, same user cannot connect from multiple locations",
    )
    SparkTrafficLimitError = (
        20357,
        "Model service user traffic limit: service is processing user's current question, wait for completion before sending new request",
    )
    SparkCapacityError = (20358, "Model service capacity insufficient, contact staff")
    SparkEngineConnectionError = (
        20359,
        "Model and engine connection establishment failed",
    )
    SparkEngineReceiveError = (20360, "Model receiving engine data error")
    SparkEngineSendError = (20361, "Model service sending data to engine error")
    SparkEngineInternalError = (20362, "Model engine internal error")
    SparkContentAuditError = (
        20363,
        "Model input content audit failed, suspected violation, please adjust input content",
    )
    SparkOutputAuditError = (
        20364,
        "Model output content involves sensitive information, audit failed, results cannot be displayed to user",
    )
    SparkAppIdBlacklistError = (20365, "Appid is in model service blacklist")
    SparkAppIdAuthError = (
        20366,
        "Model service appid authorization error: feature not enabled, version not enabled, insufficient tokens, concurrency exceeds authorization",
    )
    SparkClearHistoryError = (20367, "Model clear history failed")
    SparkViolationError = (
        20368,
        "Model service indicates session content has violation tendency; suggest showing violation warning to user",
    )
    SparkBusyError = (20369, "Model service busy, please try again later")
    SparkEngineParamsError = (
        20370,
        "Model service request engine parameter error, engine schema check failed",
    )
    SparkEngineNetworkError = (20371, "Model service engine network error")
    SparkTokenLimitError = (
        20372,
        "Model request token count exceeds limit, conversation history + question text too long, need to simplify input",
    )
    SparkAuthError = (
        20373,
        "Model authorization error: appId has no feature authorization or business volume exceeds limit",
    )
    SparkDailyLimitError = (
        20374,
        "Model authorization error: daily rate limit exceeded",
    )
    SparkSecondLimitError = (
        20375,
        "Model authorization error: second-level rate limit exceeded",
    )
    SparkConcurrencyLimitError = (
        20376,
        "Model authorization error: concurrency limit exceeded",
    )

    OpenAIRequestError = (20380, "External large model request failed")

    # WebSocket errors
    WebSocketConnectionError = (20400, "WebSocket connection error")

    # Knowledge base errors
    KnowledgeRequestError = (20500, "Knowledge base request error")
    KnowledgeNodeExecutionError = (20501, "Knowledge base node execution error")
    KnowledgeParamError = (20502, "Knowledge base parameter error")

    # Variable pool errors
    VariablePoolGetParameterError = (
        20600,
        "Variable system parameter retrieval failed",
    )
    VariablePoolSetParameterError = (20601, "Variable system parameter setting failed")
    VariableParseError = (20602, "Variable name parsing failed")

    # Database errors
    DatabaseCommitErr = (20700, "Database commit error")

    OpenApiStreamQueueTimeoutError = (20804, "OpenAPI output timeout")
    OpenApiError = (20805, "OpenAPI output error")

    # Authentication and rate limiting errors
    MASDKLiccLimitError = (
        20900,
        "Authentication failed: authorization limit, service not authorized or authorization expired",
    )
    MASDKOverLimitError = (
        20901,
        "Authentication failed: service limit exceeded, business session total limit or daily rate limit exceeded",
    )
    MASDKOverQPSLimitError = (
        20902,
        "Authentication failed: service limit exceeded, QPS second-level rate limit exceeded",
    )
    MASDKOverConcLimitError = (
        20903,
        "Concurrency authentication failed: service limit exceeded, concurrency limit exceeded",
    )
    MASDKConnectError = (
        20904,
        "Authentication SDK error, non-success status no log returned",
    )
    MASDKUnknownError = (20905, "Authentication failed, unknown error")

    # PostgreSQL node errors
    PGSqlRequestError = (21000, "PostgreSQL node request error")
    PGSqlNodeExecutionError = (21001, "PostgreSQL node execution error")
    PGSqlParamError = (21002, "PostgreSQL node request parameter error")

    # Audit errors
    AuditError = (21100, "Audit error")
    AuditServerError = (21101, "Audit service error")
    AuditInputError = (
        21102,
        "Workflow input content audit failed, suspected violation, please adjust input content",
    )
    AuditOutputError = (
        21103,
        "Workflow output content involves sensitive information, audit failed, results cannot be displayed to user",
    )
    AuditQAError = (21104, "Question-answer node does not support audit yet")

    # Image generation errors
    ImageGenerateError = (21200, "Image generation failed")
    ImageStorageError = (21201, "Image storage failed")
    ImageGenerateMsgFormatError = (21203, "User message format error")
    ImageGenerateSchemaError = (21204, "User data schema error")
    ImageGenerateParamsError = (21205, "User parameter value error")
    ImageGenerateSrvNotEnoughError = (
        21206,
        "Image generation service capacity insufficient",
    )
    ImageGenerateInputAuditError = (
        21207,
        "Image generation service input audit failed",
    )
    ImageGenerateImageSensitivenessError = (
        21208,
        "Model generated image involves sensitive information, audit failed",
    )
    ImageGenerateImageTimeoutError = (21209, "Image generation timeout")

    # Chat related errors
    ChatFieldConnectionError = (21500, "Chat connection establishment failed")

    # Code interpreter errors
    CodeExecutionError = (21600, "Code execution failed")
    CodeBuildError = (21601, "Code interpreter node build failed")
    CodeNodeResultTypeError = (
        21602,
        "Code node return result type does not meet requirements",
    )
    CodeExecutionTimeoutError = (21603, "Code execution timeout")

    # Node debug related errors
    NodeDebugError = (21700, "Node debug failed")

    # SparkLink related errors
    SparkLinkActionError = (21800, "Tool request failed")
    SparkLinkAppInitErr = (21801, "Tool initialization failed")
    SparkLinkJsonProtocolParserErr = (21802, "Tool JSON protocol parsing failed")
    SparkLinkJsonSchemaValidateErr = (21803, "Tool protocol validation failed")
    SparkLinkOpenapiSchemaValidateErr = (21804, "Tool OpenAPI protocol parsing failed")
    SparkLinkOpenapiSchemaBodyTypeNotSupportErr = (
        21805,
        "Tool body type not supported",
    )
    SparkLinkOpenapiSchemaServerNotExistErr = (21806, "Tool server does not exist")
    SparkLinkOfficialThirdApiRequestFailedErr = (21807, "Official tool request failed")
    SparkLinkToolNotExistErr = (21808, "Tool does not exist")
    SparkLinkOperationIdNotExistErr = (21809, "Tool operation does not exist")
    SparkLinkConnectionErr = (21810, "Tool request failed, connection error")
    SparkLinkExecuteErr = (21811, "Third-party tool execution failed")
    SparkLinkThirdApiRequestFailedErr = (21812, "Third-party tool request failed")

    # Protocol validation errors
    EngProtocolValidateErr = (22100, "Workflow engine protocol validation failed")
    EngNodeProtocolValidateErr = (
        22101,
        "Workflow engine node protocol validation failed",
    )

    # Engine errors
    EngBuildErr = (22300, "Workflow engine build failed")
    EngRunErr = (22301, "Workflow engine run failed")
    NodeRunErr = (22302, "Node execution failed")

    NodeOutputValidateErr = (22303, "Node output validation failed")

    # Start node errors
    StartNodeSchemaError = (22500, "Start node protocol error")

    # End node errors
    EndNodeSchemaError = (22600, "End node protocol error")
    EndNodeExecutionError = (22601, "End node execution failed")

    # Message node errors
    MessageNodeExecutionError = (22701, "Message node execution failed")

    # Parameter extractor errors
    ExtractExecutionError = (21900, "Parameter extraction failed")

    # Workflow node errors
    WorkflowExecutionError = (22801, "Workflow node execution failed")
    WorkflowExecRespFormatError = (
        22802,
        "Workflow node execution response format error",
    )

    # Variable node errors
    VariableNodeExecutionError = (22900, "Variable node execution failed")

    # Branch node errors
    IfElseNodeExecutionError = (23100, "Branch node execution failed")

    # Iteration node errors
    IterationExecutionError = (23200, "Iteration node execution failed")

    # LLM node errors
    LLMNodeExecutionError = (23300, "LLM node execution failed")

    # Plugin node errors
    PluginNodeExecutionError = (23400, "Plugin node execution failed")

    # Text joiner node errors
    TextJoinerNodeExecutionError = (23500, "Text joiner node execution failed")

    # File type errors
    FileInvalidError = (23601, "Invalid file")
    FileVariableProtocolError = (23602, "File variable protocol error")
    FileInvalidTypeError = (23603, "Invalid file link")
    FileStorageError = (23604, "File storage failed")

    # Agent node errors
    AgentNodeExecutionError = (23700, "Agent node execution failed")

    # Question-answer node errors
    QuestionAnswerNodeExecutionError = (23800, "Question-answer node execution failed")
    QuestionAnswerNodeProtocolError = (23801, "Question-answer node protocol error")
    QuestionAnswerResumeDataError = (
        23802,
        "Question-answer node data retrieval timeout",
    )
    QuestionAnswerHandlerResponseError = (
        23803,
        "Question-answer node user response handling error",
    )

    # Event management errors
    EventRegistryNotFoundError = (23900, "Conversation has timed out or does not exist")

    @property
    def code(self) -> int:
        """
        Get the numeric error code.

        Returns the integer error code that can be used for programmatic error
        identification, logging, and error handling logic. The error codes are
        organized in specific ranges to facilitate error categorization and
        systematic error handling across the workflow system.

        :return: Integer error code for programmatic identification and categorization
        """
        return self.value[0]

    @property
    def msg(self) -> str:
        """
        Get the human-readable error message.

        Returns the descriptive error message that provides clear information
        about the error for user feedback, logging, and debugging purposes.
        The messages are designed to be informative yet user-friendly, helping
        both developers and end-users understand what went wrong.

        :return: Descriptive error message for user feedback and system logging
        """
        return self.value[1]
