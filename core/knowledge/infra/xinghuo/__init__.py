# -*- coding: utf-8 -*-
"""
Xinghuo (Spark) infrastructure module

Provides functionality for interacting with iFlytek Spark service
"""

from .xinghuo import (
    upload,
    split,
    get_chunks,
    new_topk_search,
    get_file_status,
    get_file_info,
    dataset_addchunk,
    dataset_delchunk,
    dataset_updchunk,
    async_request,
    async_form_request,
    assemble_spark_auth_headers_async,
)

__all__ = [
    "upload",
    "split",
    "get_chunks",
    "new_topk_search",
    "get_file_status",
    "get_file_info",
    "dataset_addchunk",
    "dataset_delchunk",
    "dataset_updchunk",
    "async_request",
    "async_form_request",
    "assemble_spark_auth_headers_async",
]
