"""
Thread-safe atomic counter implementation using threading.Lock for synchronization.
"""

import threading


class AtomicCounter:  # pylint: disable=too-few-public-methods
    """A thread-safe counter that provides atomic increment operations.

    Attributes:
        value (int): The current value of the counter.
        lock (threading.Lock): Lock used for synchronization.
    """

    def __init__(self):
        """Initialize the atomic counter with value 0 and a new lock."""
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        """Atomically increment the counter value by 1.

        This operation is thread-safe and can be used from multiple threads.
        """
        with self.lock:
            self.value += 1

# Example usage:
# counter = AtomicCounter()
#
# def worker():
#     for _ in range(1000):
#         counter.increment()
#
# threads = []
# for _ in range(10):
#     t = threading.Thread(target=worker)
#     t.start()
#     threads.append(t)
#
# for t in threads:
#     t.join()
#
# print("Final value:", counter.value)
