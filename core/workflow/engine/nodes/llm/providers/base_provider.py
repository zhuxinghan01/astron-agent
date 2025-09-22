from abc import ABC, abstractmethod
from typing import Any


class BaseChatProvider(ABC):
    """
    Abstract base class for chat providers.

    This class defines the interface that all chat providers must implement
    to be used within the LLM node system.
    """

    @abstractmethod
    def chat(self, content: str) -> Any:
        """
        Send a chat message to the provider and return the response.

        :param content: The message content to send
        :return: The response from the chat provider
        :raises NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError


class ChatProviderFactory(ABC):
    """
    Abstract factory class for creating chat providers.

    This factory pattern allows for dynamic creation of different
    chat provider implementations based on configuration.
    """

    def creat(self, provider: str) -> Any:
        """
        Create a chat provider instance based on the provider type.

        :param provider: The type/name of the provider to create
        :return: An instance of the requested chat provider
        :raises NotImplementedError: Must be implemented by subclasses
        """
        pass
