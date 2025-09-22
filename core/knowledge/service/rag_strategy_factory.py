# -*- coding: utf-8 -*-
"""
RAG strategy factory module.

This module implements the factory pattern for RAG strategies, used to create corresponding strategy instances based on strategy type.
"""

from knowledge.service.impl.aiui_strategy import AIUIRAGStrategy
from knowledge.service.impl.cbg_strategy import CBGRAGStrategy
from knowledge.service.impl.ragflow_strategy import RagflowRAGStrategy
from knowledge.service.impl.sparkdesk_strategy import SparkDeskRAGStrategy
from knowledge.service.rag_strategy import RAGStrategy


class RAGStrategyFactory:
    """RAG strategy factory, responsible for creating corresponding strategy instances based on ragType."""

    _strategies = {
        "AIUI-RAG2": AIUIRAGStrategy,
        "SparkDesk-RAG": SparkDeskRAGStrategy,
        "CBG-RAG": CBGRAGStrategy,
        "Ragflow-RAG": RagflowRAGStrategy,
    }

    @classmethod
    def get_strategy(cls, ragType: str) -> RAGStrategy:  # pylint: disable=invalid-name
        """Get the corresponding strategy instance based on ragType."""
        strategy_class = cls._strategies.get(ragType)
        if not strategy_class:
            raise ValueError(f"Unsupported RAG type: {ragType}")
        return strategy_class()

    @classmethod
    def register_strategy(cls, ragType: str, strategy_class: type) -> None:  # pylint: disable=invalid-name
        """Register a new RAG strategy."""
        if not issubclass(strategy_class, RAGStrategy):
            raise TypeError("Strategy class must be a subclass of RAGStrategy.")
        cls._strategies[ragType] = strategy_class
