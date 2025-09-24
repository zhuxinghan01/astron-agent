"""
Test module for custom exception classes.

This module contains test functions to demonstrate and validate the custom exception
handling functionality of the workflow system. It provides examples of how to properly
use the custom exception classes and serves as a reference for exception handling
patterns throughout the system.

The test functions showcase:
- Exception wrapping and error code assignment
- Error message formatting and display
- Integration with the error code enumeration system
- Proper exception handling patterns for different error scenarios
"""

from workflow.exception.e import CustomException
from workflow.exception.errors.err_code import CodeEnum


def test_zero_division_error() -> None:
    """
    Test function demonstrating custom exception handling with ZeroDivisionError.

    This function intentionally triggers a ZeroDivisionError and wraps it in a
    CustomException to demonstrate the error handling capabilities of the workflow
    system. It shows how to properly convert standard Python exceptions into
    custom exceptions with appropriate error codes and messages.

    The test demonstrates:
    - Exception catching and wrapping
    - Error code assignment using CodeEnum
    - Custom exception string representation
    - Integration with the workflow error handling system

    :return: None
    """
    try:
        1 / 0
    except ZeroDivisionError as e:
        ce = CustomException(CodeEnum.OPEN_API_ERROR, cause_error=e)
        print(ce)
