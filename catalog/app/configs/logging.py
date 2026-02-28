import logging.config
from typing import Any, Literal

from pydantic_settings import BaseSettings
from pythonjsonlogger.core import RESERVED_ATTRS

Level = Literal["DEBUG", "INFO", "WARNING", "ERROR", "FATAL"]


class LoggingConfig(BaseSettings):
    level: Level = "INFO"

    def model_post_init(self, context: Any) -> None:
        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "()": "pythonjsonlogger.json.JsonFormatter",
                        "format": "asctime,levelname,message",
                        "style": ",",
                        "reserved_attrs": RESERVED_ATTRS + ["color_message"],
                        "rename_fields": {
                            "asctime": "ts",
                            "message": "msg",
                            "levelname": "level",
                        },
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "default",
                    }
                },
                "root": {
                    "handlers": ["console"],
                    "level": self.level,
                },
            }
        )
        super().model_post_init(context)
