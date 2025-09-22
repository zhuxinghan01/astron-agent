"""
Workflow and flow-related constants.

This module defines constants and enumerations for workflow execution,
node statuses, error handling, and flow states.
"""

from enum import Enum

# Constants for workflow and node execution completion
FLOW_FINISH_REASON = "stop"
NODE_FINISH_REASON = "node_stop"


class PathStatus:
    """
    Path status constants for workflow execution paths.

    Defines whether a path in the workflow is active or inactive.
    """

    active = "active"
    inactive = "inactive"


# Constant indicating that end nodes can output results
END_NODE_ABLE_OUTPUT = "end_node_output"


class XFLLMStatus(Enum):
    """
    XFLLM (Xinghuo Large Language Model) execution status enumeration.

    Tracks the execution state of LLM operations.
    """

    START = 0
    RUNNING = 1
    END = 2


class QuantityConsumed(Enum):
    """
    Quantity consumed enumeration for resource tracking.

    Defines consumption quantities for various resources.
    """

    ONE: int = 1


class ErrorHandler(Enum):
    """
    Error handling strategy enumeration.

    Defines different approaches for handling errors in workflow execution.
    """

    Interrupted = 0
    CustomReturn = 1
    FailBranch = 2


class FlowStatus(Enum):
    """
    Flow status enumeration.

    Defines the publication status of workflows.
    """

    DRAFT = 0
    PUBLISHED = 1
