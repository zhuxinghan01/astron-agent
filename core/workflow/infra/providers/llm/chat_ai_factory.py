"""
Chat AI Factory Module

This module provides a factory class for creating chat AI instances based on different model providers.
It supports multiple AI providers including Xinghuo (Spark) and OpenAI.
"""

from typing import Any

from workflow.consts.model_provider import ModelProviderEnum
from workflow.infra.providers.llm.iflytek_spark.spark_chat_llm import SparkChatAi
from workflow.infra.providers.llm.openai.openai_chat_llm import OpenAIChatAI


class ChatAIFactory:
    """
    Factory class for creating chat AI instances.

    This factory provides a centralized way to instantiate different chat AI providers
    based on the specified model source. It maintains a registry of supported providers
    and their corresponding implementation classes.
    """

    # Registry mapping model provider values to their corresponding chat AI classes
    _chat_ais = {
        ModelProviderEnum.XINGHUO.value: SparkChatAi,
        ModelProviderEnum.OPENAI.value: OpenAIChatAI,
    }

    @staticmethod
    def get_chat_ai(model_source: str, **kwargs: Any) -> OpenAIChatAI | SparkChatAi:
        """
        Create and return a chat AI instance based on the specified model source.

        :param model_source: The model provider identifier (e.g., 'xinghuo', 'openai')
        :param kwargs: Additional keyword arguments to pass to the chat AI constructor
        :return: An instance of the appropriate chat AI class
        :raises ValueError: If the specified model source is not supported
        """
        # Retrieve the chat AI class from the registry
        chat_ai = ChatAIFactory._chat_ais.get(model_source)
        if not chat_ai:
            raise ValueError(f"Unsupported model source: {model_source}")

        # Instantiate the chat AI with provided parameters
        chat_ai_instance = chat_ai(**kwargs)
        return chat_ai_instance
