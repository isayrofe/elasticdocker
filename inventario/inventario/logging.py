import os

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "cambios.log",
            "formatter": "standard",
        },
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        },
    },
    "loggers": {
        "materiales": {
            "handlers": ["file"],
            "level": "INFO",
        },
    },
}