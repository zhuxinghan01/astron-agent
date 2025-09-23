import os

from loguru import logger

from common.service.base import ServiceFactory, ServiceType
from common.service.oss.base_oss import BaseOSSService
from common.service.oss.ifly_storage_gateway_service import \
    IFlyGatewayStorageClient


class OSSServiceFactory(ServiceFactory):
    name = ServiceType.OSS_SERVICE

    def __init__(self):
        super().__init__(BaseOSSService)
        self.client = None

    def create(self):
        logger.debug("Creating OSS Servie")
        oss_type = os.getenv("OSS_TYPE", "ifly_gateway_storage")
        if oss_type == "s3":
            pass
        else:
            self.client = IFlyGatewayStorageClient(
                endpoint=os.getenv("OSS_ENDPOINT", ""),
                access_key_id=os.getenv("OSS_ACCESS_KEY_ID", ""),
                access_key_secret=os.getenv("OSS_ACCESS_KEY_SECRET", ""),
                bucket_name=os.getenv("OSS_BUCKET_NAME", ""),
                ttl=int(os.getenv("OSS_TTL", "86400")),
            )
        return self.client
