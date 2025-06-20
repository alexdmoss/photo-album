import logging
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.EventRenamer("msg"),
        structlog.processors.LogfmtRenderer(sort_keys=True, key_order=["level", "timestamp", "msg"], drop_missing=True),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()
