"""
Retry invalid cached statement.
"""

import asyncio
from functools import wraps

from asyncpg.exceptions import InvalidCachedStatementError
from loguru import logger
from sqlalchemy.exc import InterfaceError


def retry_on_invalid_cached_statement(max_retries=2, delay=0.1):
    """
    Automatically retry on asyncpg InvalidCachedStatementError.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (InvalidCachedStatementError, InterfaceError) as e:
                    if attempt < max_retries - 1:
                        logger.info(
                            f"[{func.__name__}] InvalidCachedStatementError, retrying "
                            f"({attempt + 1}/{max_retries})..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"[{func.__name__}] Max retries exceeded: {e}")
                        raise

        return wrapper

    return decorator
