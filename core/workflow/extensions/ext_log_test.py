"""
Test module for loguru logging extension.

This module demonstrates the usage of the loguru logging configuration
and provides examples of how to use the logging functionality.
"""

from loguru import logger

from workflow.extensions.ext_log import init_loguru

if __name__ == "__main__":
    # Initialize loguru with custom configuration
    init_loguru()

    # Example usage demonstrating file logging
    # Note: The following commented code shows how to add relative path to log records
    # relative_path = os.path.relpath(__file__, start=current_dir)
    # logger.patch(lambda record: record["extra"].update(relative_path=relative_path)).info(
    #     "This log will be saved in the file, but not shown in the console.")

    # Log a test message to verify logging functionality
    logger.info("This log will be saved in the file, but not shown in the console.")
