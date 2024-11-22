# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Centralized setup of logging for the service.
    Usage:
        from logging import logger

        logger.info("logging message")
        # You can pass extra data
        logger.info(
            "another logging message",
            additional={"key1": 1, "key2": {"company": "sample"}, "key3": [1, 2, 3]}
        )
        logger.info("another logging message", additional="Yo!!")
    https://github.com/mfkessai/opentelemetry-python-sample-app/blob/main/flask-on-cloud-functions/custom_loggers.py
"""
import json
import logging
import logging.config
from datetime import date, datetime
from inspect import getframeinfo, stack
from logging import NullHandler

import yaml

from ppr_api.metadata import APP_RUNNING_PROJECT


def setup_logging(conf):
    """Create the services logger."""
    logging.config.dictConfig(
        yaml.load(
            open(conf).read(),  # pylint: disable=consider-using-with
            Loader=yaml.SafeLoader,
        )
    )


class CallerFilter(logging.Filter):
    """This class adds some context to the log record instance"""

    filename = ""
    lineno = ""

    def filter(self, record):
        record.filename = self.filename
        record.lineno = self.lineno
        return True


def caller_reader(f):
    """This wrapper updates the context with the callor infos"""

    def wrapper(self, *args):
        caller = getframeinfo(stack()[1][0])
        self.logger.filters[0].filename = caller.filename
        self.logger.filters[0].lineno = caller.lineno
        return f(self, *args)

    return wrapper


class LoggingFormatFilter(logging.Filter):
    """Environment variable filer."""

    def filter(self, record):
        record.project = APP_RUNNING_PROJECT
        return True


class AppLogger:
    """Wrapper for logger to easy emit structured logs."""

    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger("appLogger")
        self.logger.setLevel(log_level)
        self.logger.addFilter(CallerFilter())
        self.logger.addFilter(LoggingFormatFilter())
        self.logger.addHandler(NullHandler())

    @caller_reader
    def debug(self, msg: str, additional=None):
        """Debug message."""
        self.logger.debug(msg=msg, extra=self.__build_extra(additional=additional))

    @caller_reader
    def info(self, msg: str, additional=None):
        """Info message."""
        self.logger.info(msg=msg, extra=self.__build_extra(additional=additional))

    @caller_reader
    def warning(self, msg: str, additional=None):
        """Warning message."""
        self.logger.warning(msg=msg, extra=self.__build_extra(additional=additional))

    @caller_reader
    def error(self, msg: str, additional=None):
        """Error message."""
        self.logger.error(msg=msg, extra=self.__build_extra(additional=additional))

    @caller_reader
    def critical(self, msg: str, additional=None):
        """Critical message."""
        self.logger.critical(msg=msg, extra=self.__build_extra(additional=additional))

    def __build_extra(self, additional) -> dict:
        """Extra information show up in the log."""

        def __serializer_for_fallback(obj):
            """Handling unserializable data."""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()

            if hasattr(obj, "__dict__"):
                return obj.__dict__

            raise TypeError("Type %s not serializable" % type(obj))

        try:
            extra = {"additional": json.dumps(additional, default=__serializer_for_fallback)}
        except TypeError as error:
            # if env_name_context.get() != "production":
            #    raise error

            self.logger.error(f"JSON Unserializable Object: {additional} {error}")
            extra = {"additional": additional}

        return extra


logger = AppLogger(log_level=logging.INFO)
