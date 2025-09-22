import os
import threading
import time
import unittest

from workflow.extensions.otlp.metric.meter import Meter
from workflow.extensions.otlp.metric.metric import init_metric

# SDK metric reporting interval, recommended less than 30000ms, default 1000ms
export_interval_millis = 3000
# Default configuration for metrics reporting server timeout in ms, default 5000ms
export_timeout_millis = 5000
# Default configuration for server connection timeout in ms, default 5000ms
timeout = 1000
# OpenTelemetry endpoint address
endpoint = "172.30.209.27:4317"


class TestMetric(unittest.TestCase):
    """
    Test class for metric functionality.

    This class contains unit tests for the metric system including
    basic metric reporting, error counting, and multi-threaded scenarios.
    """

    def init_metric(self) -> None:
        """
        Initialize the metric system for testing.
        """
        init_metric(
            endpoint,
            "workflow",
            timeout=timeout,
            export_interval_millis=export_interval_millis,
            export_timeout_millis=export_timeout_millis,
        )

    def test_one(self) -> None:
        """
        Test basic metric reporting with a single successful request.
        """
        os.environ["DC"] = "hf"
        os.environ["SERVICE_NAME"] = "workflow"

        self.init_metric()

        m = Meter("test_appid_workflow")
        time.sleep(0.2)
        m.in_error_count(0)

    def test_metric(self) -> None:
        """
        Test metric reporting with multiple requests and different return codes.

        This test generates 1000 iterations with 3 different return codes each,
        creating a total of 3000 metric reports.
        """
        os.environ["DC"] = "hf"
        os.environ["SERVICE_NAME"] = "workflow"

        self.init_metric()
        for i in range(1000):
            for ret_code in range(3):
                m = Meter("test_appid_workflow")
                time.sleep(0.2)
                m.in_error_count(ret_code)
                print(i)

        while True:
            pass

    def test_thread(self) -> None:
        """
        Test metric reporting in a multi-threaded environment.

        This test creates three concurrent threads to verify that
        the metric system works correctly under concurrent access.
        """
        os.environ["DC"] = "hf"
        os.environ["SERVICE_NAME"] = "workflow"

        self.init_metric()

        thread1 = myThread()
        thread2 = myThread()
        thread3 = myThread()
        thread1.start()
        thread2.start()
        thread3.start()
        thread1.join()
        thread2.join()
        thread3.join()
        print("Main thread exiting")


class myThread(threading.Thread):
    """
    Custom thread class for testing metric reporting in concurrent scenarios.

    Each thread generates a large number of metric reports with different
    return codes and custom labels to test thread safety.
    """

    def run(self) -> None:
        """
        Thread execution method that generates metric reports.

        Each thread creates 100,000 iterations with 3 different return codes,
        resulting in 300,000 metric reports per thread.
        """
        for i in range(100000):
            for ret_code in range(3):
                m = Meter("test_appid")
                # time.sleep(0.2)
                m.in_error_count(ret_code, {"topic": "get_flow_x1"})
                print(i)
