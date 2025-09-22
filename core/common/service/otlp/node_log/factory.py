from common.service.base import ServiceFactory, ServiceType
from common.service.otlp.node_log.node_log_service import OtlpNodeLogService


class OtlpNodeLogFactory(ServiceFactory):
    name = ServiceType.OTLP_NODE_LOG_SERVICE

    def __init__(self):
        super().__init__(OtlpNodeLogService)

    def create(self):
        return OtlpNodeLogService()
