# pylint: disable=invalid-name
"""
Error code conversion utilities for third-party APIs.

This module provides conversion functions to map third-party API error codes
to internal system error codes for consistent error handling across the
workflow system. It acts as a translation layer between external services
and the internal error management system, ensuring that all errors are
handled uniformly regardless of their source.

Key Features:
- Standardized error code mapping from external services to internal codes
- Support for multiple third-party service types (Spark, image generation, tools)
- Fallback handling for unknown or unrecognized error codes
- Consistent error categorization across different service providers
- Integration with the workflow system's error handling framework

The conversion utilities ensure that external service errors are properly
categorized and handled according to the workflow system's error management
standards, providing consistent error reporting and handling across all
integrated services.
"""
from workflow.exception.errors.err_code import CodeEnum
from workflow.exception.errors.third_api_code import ThirdApiCodeEnum


class CodeConvert:
    """
    Third-party API error code conversion utility.

    This class provides static methods to convert error codes from various
    third-party services to internal system error codes. It ensures consistent
    error handling by mapping external service errors to standardized internal
    error codes with appropriate fallback handling for unknown error codes.

    Supported services:
    - Image generation services
    - SparkLink tool services
    - Spark model services
    """

    @staticmethod
    def imageGeneratorCode(code: int) -> CodeEnum:
        """
        Convert image generation service error codes to internal error codes.

        Maps various image generation service errors to standardized internal
        error codes. This method handles errors from AI image generation services,
        including format errors, schema validation failures, parameter issues,
        service capacity problems, and content audit failures.

        The method provides a comprehensive mapping that covers:
        - Message format validation errors
        - Data schema validation failures
        - Parameter value validation issues
        - Service capacity and availability problems
        - Input and output content audit failures

        If the provided code is not recognized, returns a generic image generation
        error to ensure consistent error handling.

        :param code: Third-party image generation service error code (integer)
        :return: Corresponding internal error code enum for consistent handling
        """
        match code:
            case ThirdApiCodeEnum.ImageGenerateMsgFormatError.code:
                return CodeEnum.ImageGenerateMsgFormatError
            case ThirdApiCodeEnum.ImageGenerateSchemaError.code:
                return CodeEnum.ImageGenerateSchemaError
            case ThirdApiCodeEnum.ImageGenerateParamsError.code:
                return CodeEnum.ImageGenerateParamsError
            case ThirdApiCodeEnum.ImageGenerateSrvNotEnoughError.code:
                return CodeEnum.ImageGenerateSrvNotEnoughError
            case ThirdApiCodeEnum.ImageGenerateInputAuditError.code:
                return CodeEnum.ImageGenerateInputAuditError
            case ThirdApiCodeEnum.ImageGenerateImageSensitivenessError.code:
                return CodeEnum.ImageGenerateImageSensitivenessError
            case _:
                return CodeEnum.ImageGenerateError

    @staticmethod
    def sparkLinkCode(code: int) -> CodeEnum:
        """
        Convert SparkLink tool service error codes to internal error codes.

        Maps SparkLink tool service errors to standardized internal error codes.
        This method handles errors from external tool integration services,
        including initialization failures, protocol validation errors, and
        execution problems.

        The method provides comprehensive error mapping for:
        - Tool initialization and setup failures
        - JSON protocol parsing and validation errors
        - OpenAPI schema validation and parsing issues
        - Tool server and operation existence checks
        - Official and third-party tool request failures
        - Tool connection and execution errors

        Returns a generic action error for unrecognized codes to ensure
        consistent error handling across all tool integration scenarios.

        :param code: Third-party SparkLink service error code (integer)
        :return: Corresponding internal error code enum for consistent handling
        """
        match code:
            case ThirdApiCodeEnum.SparkLinkAppInitErr.code:
                return CodeEnum.SparkLinkAppInitErr
            case ThirdApiCodeEnum.SparkLinkCommonErr.code:
                return CodeEnum.SparkLinkActionError
            case ThirdApiCodeEnum.SparkLinkJsonProtocolParserErr.code:
                return CodeEnum.SparkLinkJsonProtocolParserErr
            case ThirdApiCodeEnum.SparkLinkJsonSchemaValidateErr.code:
                return CodeEnum.SparkLinkJsonSchemaValidateErr
            case ThirdApiCodeEnum.SparkLinkOpenapiSchemaValidateErr.code:
                return CodeEnum.SparkLinkOpenapiSchemaValidateErr
            case ThirdApiCodeEnum.SparkLinkOpenapiSchemaBodyTypeNotSupportErr.code:
                return CodeEnum.SparkLinkOpenapiSchemaBodyTypeNotSupportErr
            case ThirdApiCodeEnum.SparkLinkOpenapiSchemaServerNotExistErr.code:
                return CodeEnum.SparkLinkOpenapiSchemaServerNotExistErr
            case ThirdApiCodeEnum.SparkLinkOfficialThirdApiRequestFailedErr.code:
                return CodeEnum.SparkLinkOfficialThirdApiRequestFailedErr
            case ThirdApiCodeEnum.SparkLinkThirdApiRequestFailedErr.code:
                return CodeEnum.SparkLinkThirdApiRequestFailedErr
            case ThirdApiCodeEnum.SparkLinkToolNotExistErr.code:
                return CodeEnum.SparkLinkToolNotExistErr
            case ThirdApiCodeEnum.SparkLinkOperationIdNotExistErr.code:
                return CodeEnum.SparkLinkOperationIdNotExistErr
            case _:
                return CodeEnum.SparkLinkActionError

    @staticmethod
    def sparkCode(code: int) -> CodeEnum:
        """
        Convert Spark model service error codes to internal error codes.

        Maps Spark model service errors to standardized internal error codes.
        This method handles the most comprehensive range of errors in the system,
        covering all aspects of AI model service interactions.

        The method provides extensive error mapping for:
        - WebSocket connection and communication errors
        - Message format and schema validation failures
        - User concurrency and traffic limit violations
        - Service capacity and availability issues
        - Engine connection and communication problems
        - Content audit and compliance failures
        - Authentication and authorization errors
        - Rate limiting and quota management issues
        - Token limit and input size violations
        - Network and infrastructure problems

        This comprehensive mapping ensures that all Spark model service errors
        are properly categorized and handled according to the workflow system's
        error management standards.

        :param code: Third-party Spark model service error code (integer)
        :return: Corresponding internal error code enum for consistent handling
        """
        match code:
            case ThirdApiCodeEnum.SparkWSError.code:
                return CodeEnum.SparkWSError
            case ThirdApiCodeEnum.SparkWSReadError.code:
                return CodeEnum.SparkWSReadError
            case ThirdApiCodeEnum.SparkWSSendError.code:
                return CodeEnum.SparkWSSendError
            case ThirdApiCodeEnum.SparkMessageFormatError.code:
                return CodeEnum.SparkMessageFormatError
            case ThirdApiCodeEnum.SparkSchemaError.code:
                return CodeEnum.SparkSchemaError
            case ThirdApiCodeEnum.SparkParamError.code:
                return CodeEnum.SparkParamError
            case ThirdApiCodeEnum.SparkConcurrencyError.code:
                return CodeEnum.SparkConcurrencyError
            case ThirdApiCodeEnum.SparkTrafficLimitError.code:
                return CodeEnum.SparkTrafficLimitError
            case ThirdApiCodeEnum.SparkCapacityError.code:
                return CodeEnum.SparkCapacityError
            case ThirdApiCodeEnum.SparkEngineConnectionError.code:
                return CodeEnum.SparkEngineConnectionError
            case ThirdApiCodeEnum.SparkEngineReceiveError.code:
                return CodeEnum.SparkEngineReceiveError
            case ThirdApiCodeEnum.SparkEngineSendError.code:
                return CodeEnum.SparkEngineSendError
            case ThirdApiCodeEnum.SparkEngineInternalError.code:
                return CodeEnum.SparkEngineInternalError
            case ThirdApiCodeEnum.SparkContentAuditError.code:
                return CodeEnum.SparkContentAuditError
            case ThirdApiCodeEnum.SparkOutputAuditError.code:
                return CodeEnum.SparkOutputAuditError
            case ThirdApiCodeEnum.SparkAppIdBlacklistError.code:
                return CodeEnum.SparkAppIdBlacklistError
            case ThirdApiCodeEnum.SparkAppIdAuthError.code:
                return CodeEnum.SparkAppIdAuthError
            case ThirdApiCodeEnum.SparkClearHistoryError.code:
                return CodeEnum.SparkClearHistoryError
            case ThirdApiCodeEnum.SparkViolationError.code:
                return CodeEnum.SparkViolationError
            case ThirdApiCodeEnum.SparkBusyError.code:
                return CodeEnum.SparkBusyError
            case ThirdApiCodeEnum.SparkEngineParamsError.code:
                return CodeEnum.SparkEngineParamsError
            case ThirdApiCodeEnum.SparkEngineNetworkError.code:
                return CodeEnum.SparkEngineNetworkError
            case ThirdApiCodeEnum.SparkTokenLimitError.code:
                return CodeEnum.SparkTokenLimitError
            case ThirdApiCodeEnum.SparkAuthError.code:
                return CodeEnum.SparkAuthError
            case ThirdApiCodeEnum.SparkDailyLimitError.code:
                return CodeEnum.SparkDailyLimitError
            case ThirdApiCodeEnum.SparkSecondLimitError.code:
                return CodeEnum.SparkSecondLimitError
            case ThirdApiCodeEnum.SparkConcurrencyLimitError.code:
                return CodeEnum.SparkConcurrencyLimitError
            case _:
                return CodeEnum.SparkRequestError
