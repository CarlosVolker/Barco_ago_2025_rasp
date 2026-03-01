import logging


def configure_logging(level: str = "INFO", device_id: str | None = None) -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)

    try:
        from pythonjsonlogger.json import JsonFormatter

        class EnsureDefaultFieldsFilter(logging.Filter):
            def filter(self, record):
                if not hasattr(record, "device_id"):
                    record.device_id = device_id or "unknown"
                if not hasattr(record, "session_id"):
                    record.session_id = "-"
                if not hasattr(record, "correlation_id"):
                    record.correlation_id = "-"
                return True

        handler = logging.StreamHandler()
        handler.addFilter(EnsureDefaultFieldsFilter())
        formatter = JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(device_id)s %(session_id)s %(correlation_id)s"
        )
        handler.setFormatter(formatter)

        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(log_level)
        root.addHandler(handler)
    except Exception:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
