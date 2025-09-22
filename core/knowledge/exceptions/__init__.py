# -*- coding: utf-8 -*-
"""
Exception handling module

Defines custom exception classes used in Knowledge Service
"""

from .exception import (
    BaseCustomException,
    ProtocolParamException,
    ServiceException,
    ThirdPartyException,
    CustomException
)

__all__ = [
    "BaseCustomException",
    "ProtocolParamException",
    "ServiceException",
    "ThirdPartyException",
    "CustomException",
]
