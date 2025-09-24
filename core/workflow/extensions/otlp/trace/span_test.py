"""
Test module for Span functionality in OpenTelemetry tracing.

This module contains test functions to demonstrate and validate
the Span class functionality including span creation, attribute setting,
event logging, and nested span operations.
"""

import time

from opentelemetry.trace import Status, StatusCode
from workflow.extensions.otlp.log_trace.node_log import NodeLog
from workflow.extensions.otlp.sid.sid_generator2 import init_sid
from workflow.extensions.otlp.trace.span import Span
from workflow.extensions.otlp.trace.trace import init_trace

# Initialize node log for testing
node_log = NodeLog("1", "2", "3", "4")


def do_work1() -> None:
    """
    First level work function demonstrating basic span operations.

    Creates a span, sets various attributes, adds events, and calls nested work function.
    """
    # Create a span from the global tracer provider
    span = Span()
    # The span is automatically closed when the 'with' block exits
    with span.start() as current_span:
        # Set individual attributes
        current_span.set_attribute("operation.value", "chain1", node_log)
        current_span.set_attribute("operation.name", "Saying hello!", node_log)
        current_span.set_attribute("operation.other-stuff", [1, 2, 3], node_log)

        # Set span status to error
        current_span.set_status(Status(StatusCode.ERROR))

        # Set multiple attributes at once
        current_span.set_attributes(
            attributes={"info1": "chain1 info1", "info2": "chain1 info2"},
            node_log=node_log,
        )

        # Add error event
        current_span.add_error_event("error event content", node_log)
        # current_span.record_exception(ex)

        # Simulate work and call nested function
        time.sleep(1)
        do_work2(current_span)


def do_work2(span: Span) -> None:
    """
    Second level work function demonstrating nested span creation.

    :param span: Parent span to create child span from
    """
    with span.start(func_name="do_work222") as current_span:
        # Simulate work
        time.sleep(1)
        # Call next level function
        do_work3(current_span)


def do_work3(span: Span) -> None:
    """
    Third level work function demonstrating span attributes and events.

    :param span: Parent span to create child span from
    """
    with span.start(attributes={"do work3": "do something"}) as current_span:
        # Simulate work
        time.sleep(1)

        # Set additional attributes
        current_span.set_attribute("test log", "do_work3", node_log)
        current_span.set_attribute("operation.name", "Saying hello!", node_log)

        # Add custom event
        current_span.add_event(
            name="event test",
            attributes={"event content": "success"},
            node_log=node_log,
        )

        # Print completion message
        print("Hello world from OpenTelemetry Python!")


def test_do_work() -> None:
    """
    Main test function that initializes tracing and runs the work chain.

    Sets up OpenTelemetry tracing, initializes session ID generation,
    runs the nested work functions, and outputs the node log.
    """
    # Initialize OpenTelemetry tracing
    init_trace(endpoint="172.30.209.27:4317", service_name="SparkFlow")

    # Initialize session ID generator
    init_sid("spf", "hf", "127.0.0.1", "10000")

    # Run the work chain
    do_work1()

    # Output the node log as JSON
    print(node_log.json(ensure_ascii=True, indent=2))
