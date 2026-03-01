import asyncio
import inspect
import logging
import time
from collections.abc import Callable

logger = logging.getLogger("edge_agent.safety.deadman")


class DeadmanTimer:
    def __init__(self, timeout_ms: int, on_timeout: Callable[[], object]):
        if timeout_ms <= 0:
            raise ValueError("timeout_ms must be greater than 0")

        self._timeout_s = timeout_ms / 1000.0
        self._on_timeout = on_timeout
        self._check_interval_s = max(0.05, self._timeout_s / 3.0)
        self._task: asyncio.Task | None = None
        self._last_touch = time.monotonic()
        self._fired = False
        self._running = False

    def start(self) -> None:
        self._last_touch = time.monotonic()
        self._fired = False
        self._running = True

        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())

    def touch(self) -> None:
        self._last_touch = time.monotonic()
        self._fired = False

    def stop(self) -> None:
        self._running = False
        task = self._task
        self._task = None
        if task is not None and not task.done():
            task.cancel()

    async def _run(self) -> None:
        try:
            while self._running:
                elapsed_s = time.monotonic() - self._last_touch
                if not self._fired and elapsed_s >= self._timeout_s:
                    self._fired = True
                    try:
                        result = self._on_timeout()
                        if inspect.isawaitable(result):
                            await result
                    except Exception as exc:
                        logger.error("Deadman timeout callback failed: %s", exc)

                await asyncio.sleep(self._check_interval_s)
        except asyncio.CancelledError:
            pass
