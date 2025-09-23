"""
Database service factory module for creating and configuring DatabaseService instances.
"""

import os

from memory.database.repository.middleware.database.db_manager import \
    DatabaseService
from memory.database.repository.middleware.factory import ServiceFactory


class DatabaseServiceFactory(ServiceFactory):  # pylint: disable=too-few-public-methods
    """
    Factory class for creating DatabaseService instances
    with environment-based configuration.

    Inherits from ServiceFactory to provide
    database service creation capabilities.
    """

    def __init__(self):
        """Initialize the factory with DatabaseService as the target service class."""
        super().__init__(DatabaseService)

    async def create(self, database_url: str = None):
        """Create a new DatabaseService instance.

        Args:
            database_url: Optional direct database URL.
            If not provided, will be constructed
            from environment variables.

        Environment Variables:
            PGSQL_USER: PostgreSQL username
            PGSQL_PASSWORD: PostgreSQL password
            PGSQL_DATABASE: PostgreSQL database name
            PGSQL_HOST: PostgreSQL host address
            PGSQL_PORT: PostgreSQL port number

        Returns:
            DatabaseService: Configured database service instance
        """
        if database_url is None:
            user = os.getenv("PGSQL_USER")
            password = os.getenv("PGSQL_PASSWORD")
            database = os.getenv("PGSQL_DATABASE")
            host = os.getenv("PGSQL_HOST")
            port = int(os.getenv("PGSQL_PORT"))
            database_url = (
                f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
            )
        return await DatabaseService.create(database_url=database_url)
