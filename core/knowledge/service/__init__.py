# -*- coding: utf-8 -*-
"""
Service layer module

Provides core business logic for Knowledge Service, including RAG strategy interfaces and factory
"""

from .rag_strategy import RAGStrategy
from .rag_strategy_factory import RAGStrategyFactory
from .impl import (
    AIUIRAGStrategy,
    CBGRAGStrategy,
    SparkDeskRAGStrategy,
)

__all__ = [
    "RAGStrategy",
    "RAGStrategyFactory",
    "AIUIRAGStrategy",
    "CBGRAGStrategy",
    "SparkDeskRAGStrategy",
]
