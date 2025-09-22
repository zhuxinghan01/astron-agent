"""
Loguru logging extension module.

This module provides configuration and initialization for the loguru logging library,
including file rotation, retention policies, and custom formatting.
"""

import os

from loguru import logger


def init_loguru() -> None:
    """
    Initialize loguru logger with custom configuration.

    This function sets up loguru with file-based logging, including:
    - Custom log directory creation
    - File rotation and retention policies
    - JSON serialization for structured logging
    - Configurable log levels via environment variables

    Environment Variables:
        WORKFLOW_LOG_PATH: Base directory for log files (default: "../..")
        WORKFLOW_LOG_LEVEL: Logging level (default: "ERROR")

    :return: None
    """
    # Get base directory for logs from environment variable
    current_dir = os.getenv("WORKFLOW_LOG_PATH", "../..")
    log_dir = os.path.join(current_dir, "logs")
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Configure log file path and log level
    log_path = os.path.join(log_dir, "app.log")
    log_level = os.getenv("WORKFLOW_LOG_LEVEL", "ERROR")

    # Initialize loguru by removing default configuration
    logger.remove()

    # Define custom log format with timestamp, file location, and message
    log_format = (
        "{level} | {time:YYYY-MM-DD HH:mm:ss} | {file} - {function}: {line} {message}"
    )

    # Add file handler with rotation, retention, and compression settings
    logger.add(
        log_path,
        rotation="100 MB",  # Rotate log file when it exceeds 100MB
        retention="10 days",  # Keep log files for 10 days
        compression="zip",  # Compress old log files to save space
        format=log_format,  # Use custom log format
        serialize=True,  # Enable JSON serialization for structured logging
        level=log_level,  # Set logging level
    )

    # Log successful initialization
    logger.debug(
        f"Loguru initialized successfully. Log file: {log_path}, Log level: {log_level}"
    )
