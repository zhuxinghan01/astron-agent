"""
统一的 common 包导入配置模块
在其他文件中只需要 import common_imports 即可使用 common 包的所有模块
"""

import os
import sys

# Add parent directory to Python path to import common package
_current_dir = os.path.dirname(os.path.abspath(__file__))
_common_path = os.path.join(_current_dir, "..")
if _common_path not in sys.path:
    sys.path.insert(0, _common_path)

try:
    # 导入 common 包的常用模块，供其他文件使用
    from common.exceptions.base import BaseExc
    from common.initialize.initialize import initialize_services
    from common.otlp.ip import local_ip
    from common.otlp.log_trace.base import Usage
    from common.otlp.log_trace.node_log import Data, NodeLog
    from common.otlp.log_trace.node_trace_log import NodeTraceLog
    from common.otlp.log_trace.node_trace_log import Status as TraceStatus
    from common.otlp.metrics.meter import Meter
    from common.otlp.sid import sid_generator2
    from common.otlp.trace.span import Span
    from common.otlp.trace.trace import logger
    from common.settings.polaris import ConfigFilter, Polaris

    # 为了向后兼容，提供别名
    NodeTrace = NodeTraceLog
    Node = NodeLog  # xingchen_utils.Node -> common.NodeLog
    NodeData = Data  # xingchen_utils.NodeData -> common.Data
    NodeDataUsage = Usage  # xingchen_utils.NodeDataUsage -> common.Usage

    # 运行时常量 - 为了兼容性创建
    DevelopmentEnv = "development"
    ProductionEnv = "production"

    # IP 别名 - 为了兼容性
    ip = local_ip  # xingchen_utils.otlp.util.ip.ip -> common.otlp.ip.local_ip

    __all__ = [
        "BaseExc",
        "Meter",
        "NodeLog",
        "NodeTraceLog",
        "NodeTrace",  # 别名
        "Node",  # 别名
        "NodeData",  # 别名
        "NodeDataUsage",  # 别名
        "Data",
        "Usage",
        "TraceStatus",
        "Span",
        "sid_generator2",
        "logger",
        "initialize_services",
        "ConfigFilter",
        "Polaris",
        "DevelopmentEnv",
        "ProductionEnv",
        "local_ip",
        "ip",
    ]

except ImportError as e:
    # 如果导入失败，提供一个更有用的错误信息
    raise ImportError(
        f"Failed to import common modules. Please ensure the common package is properly installed. Error: {e}"
    )
