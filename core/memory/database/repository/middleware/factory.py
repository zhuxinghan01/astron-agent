"""
Factory pattern implementation for service creation.
"""


class ServiceFactory:  # pylint: disable=too-few-public-methods
    """Abstract base class for creating service instances.

    Attributes:
        service_class: The service class to be instantiated by the factory.
    """

    def __init__(self, service_class):
        """Initialize the factory with a service class.

        Args:
            service_class: The service class this factory will create.
        """
        self.service_class = service_class

    def create(self, *args, **kwargs):
        """Create an instance of the service.

        Args:
            *args: Positional arguments for service initialization
            **kwargs: Keyword arguments for service initialization

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError
