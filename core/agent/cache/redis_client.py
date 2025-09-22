from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field
from rediscluster import ClusterConnectionPool, RedisCluster

from exceptions.middleware_exc import PingRedisExc


class RedisClientCache(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: Any = Field(default=None)


class RedisClusterClient(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    nodes: str
    password: str
    _client: Optional[RedisCluster] = None

    async def create_client(self) -> RedisCluster:
        """创建客户端"""
        if self._client is None:
            nodes = []
            for node in self.nodes.split(","):
                node_addr, node_port = node.split(":")
                nodes.append({"host": node_addr, "port": int(node_port)})

            pool = ClusterConnectionPool(startup_nodes=nodes, password=self.password)
            self._client = RedisCluster(connection_pool=pool)

        await self.is_connected(self._client)

        return self._client

    async def get(self, name: str) -> bytes | None:

        client = await self.create_client()
        result = client.get(name)
        return result if isinstance(result, bytes) else None

    async def set(
        self,
        name: str,
        value: str,
        *,
        ex: int | None = None,
        px: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        client = await self.create_client()
        result = client.set(name, value, ex=ex, px=px, nx=nx, xx=xx)
        return bool(result)

        # check connection

    async def delete(self, name: str) -> int:
        client = await self.create_client()
        result = client.delete(name)
        return int(result)

    async def get_ttl(self, name: str) -> Optional[int]:
        """获取指定 key 的剩余过期时间（秒）
        :param name: 要查询的 key
        :return: 剩余过期时间（秒），若 key 不存在返回 -2，若 key 存在但无过期时间返回 -1
        """
        client = await self.create_client()
        result = client.ttl(name)
        # Handle the complex return type from redis ttl command
        if isinstance(result, int):
            return result
        return None

    @staticmethod
    async def is_connected(client: RedisCluster) -> bool:
        """
        Check if the Redis client is connected.
        """

        try:
            client.ping()
            return True
        except Exception as e:
            raise PingRedisExc from e
