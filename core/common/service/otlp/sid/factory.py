import os

from common.otlp.args import global_otlp_sid_args
from common.otlp.sid import SidInfo, init_sid
from common.service.base import ServiceFactory, ServiceType
from common.service.otlp.sid.sid_service import OtlpSidService


def init_otlp_sid():

    # global global_otlp_sid_args

    if global_otlp_sid_args.inited:
        return

    global_otlp_sid_args.otlp_endpoint = os.getenv("OTLP_ENDPOINT", "")
    global_otlp_sid_args.otlp_service_name = os.getenv("OTLP_SERVICE_NAME", "")
    global_otlp_sid_args.otlp_dc = os.getenv("OTLP_DC", "")

    global_otlp_sid_args.sid_sub = os.getenv("OTLP_SID_SUB", "svc")
    global_otlp_sid_args.sid_location = os.getenv("OTLP_SID_LOCATION", "src")
    global_otlp_sid_args.sid_local_port = os.getenv("OTLP_SID_LOCAL_PORT", "5000")
    init_sid(
        SidInfo(
            sub=global_otlp_sid_args.sid_sub,
            location=global_otlp_sid_args.sid_location,
            local_ip=global_otlp_sid_args.sid_ip,
            local_port=global_otlp_sid_args.sid_local_port,
            index=0,
        )
    )


class OtlpSidFactory(ServiceFactory):
    name = ServiceType.OTLP_SID_SERVICE

    def __init__(self):
        super().__init__(OtlpSidService)

    def create(self):
        init_otlp_sid()
        return OtlpSidService()
