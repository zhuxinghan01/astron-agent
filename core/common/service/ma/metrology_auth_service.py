import os

from common.metrology_auth import MASDK
from common.service.base import Service, ServiceType


class MASDKService(Service):
    name = ServiceType.MASDK_SERVICE

    def __init__(
        self,
        channel_list,
        strategy_type,
        polaris_url="",
        polaris_project="",
        polaris_group="",
        polaris_service="",
        polaris_version="",
        rpc_config_file=None,
        metrics_service_name=None,
    ):
        # 初始化masdk
        if not os.getenv("MASDK_SWITCH"):
            return
        self.ma_sdk = MASDK(
            channel_list,
            strategy_type,
            polaris_url,
            polaris_project,
            polaris_group,
            polaris_service,
            polaris_version,
            rpc_config_file,
            metrics_service_name,
        )
