"""
Test module for distributed tracing with span linking across processes.

This module demonstrates how to propagate trace context between different
processes using multiprocessing, enabling distributed tracing across
service boundaries.
"""

import multiprocessing
import time

from workflow.extensions.otlp.sid.sid_generator2 import init_sid
from workflow.extensions.otlp.trace.span import Span
from workflow.extensions.otlp.trace.trace import Trace, init_trace


def trace1() -> dict:
    """
    First service function that creates a span and injects trace context.

    :return: Dictionary containing trace context for propagation
    """
    # Initialize tracing for the first service
    init_trace(endpoint="172.30.209.27:4317", service_name="SparkFlow")
    init_sid("spf", "hf", "127.0.0.1", "10000")

    # Create a span from the global tracer provider
    span = Span()
    # The span is automatically closed when the 'with' block exits
    with span.start() as current_span:
        print("this is service 1")
        current_span.add_info_event("this is service 1")
        # Extract trace context for propagation to other services
        return Trace.inject_context()


def trace2(trace_context: dict) -> None:
    """
    Second service function that continues tracing using received trace context.

    :param trace_context: Trace context dictionary received from the first service
    """
    # Initialize tracing for the second service
    init_trace(endpoint="172.30.209.27:4317", service_name="SparkLink")
    init_sid("spf", "hf", "127.0.0.1", "10000")

    # Create a span from the global tracer provider
    span = Span()
    # The span is automatically closed when the 'with' block exits
    with span.start(trace_context=trace_context) as current_span:
        print("this is service 2")
        current_span.add_info_event("this is service 2")


def run_trace1(pipe: multiprocessing.connection.Connection) -> None:
    """
    Process function that runs the first trace and sends context via pipe.

    :param pipe: Multiprocessing connection for inter-process communication
    """
    # Run the first trace and get context
    trace_context = trace1()
    # Send trace context to the other process
    pipe.send(trace_context)
    pipe.close()


def run_trace2(pipe: multiprocessing.connection.Connection) -> None:
    """
    Process function that receives trace context and runs the second trace.

    :param pipe: Multiprocessing connection for inter-process communication
    """
    # Receive trace context from the other process
    trace_context = pipe.recv()
    # Run the second trace with received context
    trace2(trace_context)


def test_link() -> None:
    """
    Main test function that demonstrates distributed tracing across processes.

    Creates two processes, establishes communication between them,
    and demonstrates trace context propagation across process boundaries.
    """
    # Create a pipe for inter-process communication
    parent_conn, child_conn = multiprocessing.Pipe()

    # Create processes for each trace function
    process1 = multiprocessing.Process(target=run_trace1, args=(parent_conn,))
    process2 = multiprocessing.Process(target=run_trace2, args=(child_conn,))

    # Start both processes
    process1.start()
    process2.start()

    # Wait for both processes to complete
    process1.join()
    process2.join()

    # Wait additional time for trace export
    time.sleep(10)
