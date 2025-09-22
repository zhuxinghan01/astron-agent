"""
Constants and enumerations for OpenAI LLM provider.
"""

from enum import Enum

# End frame marker for LLM streaming responses
LLM_END_FRAME = "stop"


class RespFormatEnum(Enum):
    """
    Enumeration for response format types.

    :cvar TEXT: Plain text format
    :cvar MARKDOWN: Markdown format
    :cvar JSON: JSON format
    """

    TEXT = 0
    MARKDOWN = 1
    JSON = 2
