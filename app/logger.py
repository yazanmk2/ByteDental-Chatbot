"""
ByteDent API Logger
===================
CTO Best Practice: Structured JSON logging for production environments,
enabling easy log aggregation, searching, and alerting.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger

from app.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for structured logging.

    Adds standard fields to every log entry for consistency
    and easier querying in log aggregation systems.
    """

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['service'] = settings.app_name
        log_record['version'] = settings.app_version
        log_record['environment'] = settings.environment

        # Add source location for debugging
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'duration_ms'):
            log_record['duration_ms'] = record.duration_ms


class TextFormatter(logging.Formatter):
    """Human-readable formatter for development"""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Format timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Build message
        msg = f"{color}{timestamp} | {record.levelname:8} | {record.name}{reset} | {record.getMessage()}"

        # Add extra fields if present
        extras = []
        if hasattr(record, 'request_id'):
            extras.append(f"request_id={record.request_id}")
        if hasattr(record, 'duration_ms'):
            extras.append(f"duration={record.duration_ms:.1f}ms")

        if extras:
            msg += f" | {' '.join(extras)}"

        # Add exception if present
        if record.exc_info:
            msg += f"\n{self.formatException(record.exc_info)}"

        return msg


def setup_logging() -> logging.Logger:
    """
    Configure application logging.

    CTO Note: In production, use JSON format for log aggregation.
    In development, use text format for readability.
    """
    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("bytedent")
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Set formatter based on environment
    if settings.log_format.lower() == "json" or settings.environment == "production":
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = TextFormatter()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter for adding context to log messages.

    Usage:
        logger = get_logger(__name__)
        logger = logger.with_context(request_id="req_123")
        logger.info("Processing request")
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        # Add extra fields from context
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return msg, kwargs

    def with_context(self, **kwargs) -> 'LoggerAdapter':
        """Create new adapter with additional context"""
        new_extra = {**self.extra, **kwargs}
        return LoggerAdapter(self.logger, new_extra)


def get_logger(name: str) -> LoggerAdapter:
    """
    Get a logger instance for a module.

    Usage:
        from app.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Hello world")
    """
    base_logger = logging.getLogger(f"bytedent.{name}")

    # Ensure base logger inherits from root bytedent logger
    if not base_logger.handlers:
        base_logger.parent = logging.getLogger("bytedent")

    return LoggerAdapter(base_logger, {})


# Initialize logging on import
root_logger = setup_logging()
