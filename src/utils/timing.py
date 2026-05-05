"""Timing helpers for profiling and metrics.

Usage:
    with Timer() as t:
        do_something()
    print(f"Took {t.elapsed_ms} ms")
"""

import time
from types import TracebackType


class Timer:
    """Context manager that measures elapsed wall time."""

    def __init__(self) -> None:
        self.start: float = 0.0
        self.end: float = 0.0

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.end = time.perf_counter()

    @property
    def elapsed(self) -> float:
        """Elapsed time in seconds."""
        return self.end - self.start

    @property
    def elapsed_ms(self) -> float:
        """Elapsed time in milliseconds."""
        return (self.end - self.start) * 1000
