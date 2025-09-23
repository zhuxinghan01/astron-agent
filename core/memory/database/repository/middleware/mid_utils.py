"""
Service utilities module containing service type definitions and factory helpers.
"""

from enum import Enum


class ServiceType(str, Enum):
    """
    Enum for the different types of services that can be
    registered with the service manager.
    """

    CACHE_SERVICE = "cache_service"
    DATABASE_SERVICE = "database_service"
    LOG_SERVICE = "log_service"


def get_factories_and_deps():
    """Get configured service factories and their dependencies.

    Returns:
        list: List of tuples containing (factory, dependencies) pairs
    """
    from memory.database.repository.middleware.database import \
        db_factory as database_factory

    return [
        (
            database_factory.DatabaseServiceFactory(),
            [ServiceType.DATABASE_SERVICE],
        )
    ]
