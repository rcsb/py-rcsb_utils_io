##
# File: LogUtil.py
# Date: 5-Sep-2021
#
# Updates:
#
##
import copy
import json
import logging
from datetime import datetime

from rcsb.utils.io.IoUtil import JsonTypeEncoder


class StructFormatter(logging.Formatter):
    """Structured log formatter including message, time, and any extra attributes.

    Example::

        import logging

        from rcsb.utils.io.LogUtil import StructFormatter
        sl = logging.StreamHandler()
        sl.setFormatter(StructFormatter())
        logger = logging.getLogger(__name__)
        logger.addHandler(sl)

    """

    def __init__(self, fmt, mask):
        super(StructFormatter, self).__init__(fmt, mask)
        self._keywords = [
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "message",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        ]

    def format(self, record):
        """Serialize the log record in JSON including message, time, and extra attributes.
        Exception and stack traceback details are also included when set.

        Args:
            record (obj): log record object (LogRecord)

        Returns:
            (JSON): JSON serialized log record

        """

        myRecord = copy.copy(record)
        message = myRecord.getMessage()

        rD = {ky: myRecord.__dict__[ky] for ky in myRecord.__dict__ if ky not in self._keywords}
        rD["message"] = message
        if "time" not in rD:
            rD["time"] = datetime.utcnow()
        if myRecord.exc_info:
            rD["exc_info"] = self.formatException(myRecord.exc_info)
        if myRecord.stack_info:
            rD["stack_info"] = self.formatStack(myRecord.stack_info)
        #
        return self._serialize(rD)

    def _serialize(self, rD):
        """ """
        try:
            return json.dumps(rD, cls=JsonTypeEncoder)
        except TypeError:
            try:
                return json.dumps(rD)
            except TypeError:
                return "{}"


class DetailedStructFormatter(StructFormatter):
    """Structured logging formatter atomizing all log record attributes and extra attributes.
    Exception and stack traceback details are also included when set.

    Example:

        import logging
        from rcsb.utils.io.LogUtil import DetailedStructFormatter
        sl = logging.StreamHandler()
        sl.setFormatter(DetailedStructFormatter())
        logger = logging.getLogger(__name__)
        logger.addHandler(sl)

    """

    def format(self, record):
        """Serialize the log record in JSON including all standard log record attributes and extra attributes.

        Args:
            record (obj): log record object (LogRecord)

        Returns:
            (JSON): JSON serialized log record
        """
        myRecord = copy.copy(record)
        message = myRecord.getMessage()
        rD = {ky: myRecord.__dict__[ky] for ky in myRecord.__dict__ if ky not in self._keywords}
        rD["message"] = message
        if "time" not in rD:
            rD["time"] = datetime.utcnow()
        if myRecord.exc_info:
            rD["exc_info"] = self.formatException(myRecord.exc_info)
        if myRecord.stack_info:
            rD["stack_info"] = self.formatStack(myRecord.stack_info)
        #
        rD["filename"] = myRecord.filename
        rD["funcName"] = myRecord.funcName
        rD["levelname"] = myRecord.levelname
        rD["lineno"] = myRecord.lineno
        rD["module"] = myRecord.module
        rD["name"] = myRecord.name
        rD["pathname"] = myRecord.pathname
        rD["process"] = myRecord.process
        rD["processName"] = myRecord.processName
        rD["thread"] = myRecord.thread
        rD["threadName"] = myRecord.threadName
        #
        return self._serialize(rD)
