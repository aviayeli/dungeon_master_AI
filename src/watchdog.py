from __future__ import annotations
import concurrent.futures
from typing import Any, Callable

WATCHDOG_TIMEOUT_SEC: float = 15.0


class WatchdogTimeoutError(TimeoutError):
    pass


class Watchdog:
    def __init__(self, timeout_sec: float = WATCHDOG_TIMEOUT_SEC) -> None:
        self._timeout = timeout_sec

    def run(self, fn: Callable[[], Any]) -> Any:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(fn)
        try:
            return future.result(timeout=self._timeout)
        except concurrent.futures.TimeoutError:
            raise WatchdogTimeoutError(
                f"הבקשה ל-LLM חרגה מ-{self._timeout:.0f} שניות ובוטלה."
            )
        finally:
            executor.shutdown(wait=False)
