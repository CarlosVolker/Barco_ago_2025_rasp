import time


class MetricsCollector:
    def __init__(self):
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._timestamps: dict[str, float] = {}

    def inc(self, name, amount=1):
        current = self._counters.get(name, 0)
        self._counters[name] = current + amount
        self._timestamps[name] = time.time()

    def set_gauge(self, name, value):
        self._gauges[name] = value
        self._timestamps[name] = time.time()

    def snapshot(self):
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "timestamps": dict(self._timestamps),
            "captured_at": time.time(),
        }
