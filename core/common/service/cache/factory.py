import os

from loguru import logger

from common.service.base import ServiceFactory
from common.service.cache.base_cache import RedisModel
from common.service.cache.redis_cache import RedisCache


class CacheServiceFactory(ServiceFactory):
    def __init__(self):
        super().__init__(RedisCache)

    def create(self) -> RedisCache:
        logger.debug("Creating Redis cache")
        redis_cluster_addr = os.getenv("REDIS_CLUSTER_ADDR", "")
        redis_addr = os.getenv("REDIS_ADDR", "")
        if not redis_cluster_addr and not redis_addr:
            raise RuntimeError("REDIS_CLUSTER_ADDR or REDIS_ADDR must be set")
        redis_cache = RedisCache(
            expiration_time=os.getenv("REDIS_EXPIRE"),
            addr=redis_cluster_addr or redis_addr,
            password=os.getenv("REDIS_PASSWORD", ""),
            model=RedisModel.CLUSTER if redis_cluster_addr else RedisModel.SINGLE,
        )
        if redis_cache.is_connected():
            logger.debug("Redis cache is connected")
            return redis_cache
        else:
            raise RuntimeError("Could not connect to Redis cache")
