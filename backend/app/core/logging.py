import logging
import logging.config


def setup_logging(log_level: str) -> None:
    resolved_level = log_level.upper()
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": resolved_level,
                    "formatter": "standard",
                }
            },
            "root": {"handlers": ["console"], "level": resolved_level},
        }
    )
