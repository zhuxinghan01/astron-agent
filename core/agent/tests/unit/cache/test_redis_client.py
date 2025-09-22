"""Redis客户端单元测试模块."""

import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from cache.redis_client import RedisClientCache, RedisClusterClient


class TestRedisClientCache:
    """RedisClientCache测试类."""

    def setup_method(self) -> None:
        """Test setup method."""
        self.cache = (
            RedisClientCache()
        )  # pylint: disable=attribute-defined-outside-init

    def test_init_empty_client(self) -> None:
        """测试空客户端初始化."""
        assert self.cache.client is None

    def test_init_with_client(self) -> None:
        """测试带客户端初始化."""
        mock_client = Mock()
        cache = RedisClientCache(client=mock_client)
        assert cache.client == mock_client

    def test_config_arbitrary_types_allowed(self) -> None:
        """测试配置允许任意类型."""
        # Pydantic V2中通过model_config访问配置
        assert hasattr(self.cache, "__config__") or hasattr(
            self.cache.__class__, "model_config"
        )

    def test_cache_serialization(self) -> None:
        """测试缓存序列化."""
        cache_dict = self.cache.model_dump()
        assert isinstance(cache_dict, dict)
        assert "client" in cache_dict

    def test_cache_with_mock_client_attrs(self) -> None:
        """测试缓存与mock客户端属性."""
        mock_client = Mock()
        mock_client.connection_pool = Mock()
        mock_client.nodes = [{"host": "localhost", "port": 7000}]

        cache = RedisClientCache(client=mock_client)
        assert cache.client == mock_client
        assert hasattr(cache.client, "connection_pool")
        assert hasattr(cache.client, "nodes")


class TestRedisClusterClient:  # pylint: disable=too-many-public-methods
    """RedisClusterClient测试类."""

    def setup_method(self) -> None:
        """测试方法初始化."""
        self.nodes = [  # pylint: disable=attribute-defined-outside-init
            {"host": "localhost", "port": 7000},
            {"host": "localhost", "port": 7001},
        ]
        # pylint: disable=attribute-defined-outside-init
        self.password = "test_password"
        self.client = RedisClusterClient(
            nodes="localhost:7000,localhost:7001", password=self.password
        )

    @pytest.mark.asyncio
    @patch("cache.redis_client.ClusterConnectionPool")
    @patch("cache.redis_client.RedisCluster")
    async def test_create_client_success(
        self,
        mock_redis_cluster: Mock,
        mock_pool: Mock,
    ) -> None:
        """测试成功创建客户端."""
        # Arrange
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis_cluster.return_value = mock_redis

        # Act
        result = await self.client.create_client()

        # Assert
        assert result == mock_redis
        mock_pool.assert_called_once()
        mock_redis_cluster.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_client_reuse_existing(self) -> None:
        """测试复用现有客户端."""
        # 设置现有客户端
        mock_existing_client = Mock()
        self.client._client = mock_existing_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.create_client()

            # 验证复用现有客户端
            assert result == mock_existing_client

    @pytest.mark.asyncio
    @patch("cache.redis_client.ClusterConnectionPool")
    @patch("cache.redis_client.RedisCluster")
    async def test_create_client_node_parsing(
        self, mock_redis_cluster: Mock, mock_pool: Mock
    ) -> None:
        """测试节点解析逻辑."""
        # Arrange
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis_cluster.return_value = mock_redis

        client = RedisClusterClient(
            nodes="192.168.1.1:6379,192.168.1.2:6380", password="test"
        )

        # Act
        await client.create_client()

        # Assert
        call_args = mock_pool.call_args
        startup_nodes = call_args[1]["startup_nodes"]
        assert len(startup_nodes) == 2
        assert startup_nodes[0] == {"host": "192.168.1.1", "port": 6379}
        assert startup_nodes[1] == {"host": "192.168.1.2", "port": 6380}

    @pytest.mark.asyncio
    async def test_get_success(self) -> None:
        """测试成功获取值."""
        test_key = "test_key"
        test_value = b"test_value"

        # 直接设置mock客户端
        mock_client = Mock()
        mock_client.get.return_value = test_value
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.get(test_key)

            assert result == test_value
            mock_client.get.assert_called_once_with(test_key)

    @pytest.mark.asyncio
    async def test_get_non_bytes_result(self) -> None:
        """测试获取非bytes结果."""
        test_key = "test_key"

        # 直接设置mock客户端
        mock_client = Mock()
        mock_client.get.return_value = "string_value"  # 非bytes类型
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.get(test_key)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_none_result(self) -> None:
        """测试获取None结果."""
        test_key = "nonexistent_key"

        mock_client = Mock()
        mock_client.get.return_value = None
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.get(test_key)

            assert result is None

    @pytest.mark.asyncio
    async def test_set_success(self) -> None:
        """测试成功设置值."""
        test_key = "test_key"
        test_value = "test_value"

        # 直接设置mock客户端
        mock_client = Mock()
        mock_client.set.return_value = True
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.set(test_key, test_value)

            assert result is True
            mock_client.set.assert_called_once_with(
                test_key, test_value, ex=None, px=None, nx=False, xx=False
            )

    @pytest.mark.asyncio
    async def test_set_with_options(self) -> None:
        """测试带选项设置值."""
        test_key = "test_key"
        test_value = "test_value"

        # 直接设置mock客户端
        mock_client = Mock()
        mock_client.set.return_value = True
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.set(
                test_key, test_value, ex=3600, px=None, nx=True, xx=False
            )

            assert result is True
            mock_client.set.assert_called_once_with(
                test_key, test_value, ex=3600, px=None, nx=True, xx=False
            )

    @pytest.mark.asyncio
    async def test_set_failure(self) -> None:
        """测试设置失败."""
        test_key = "test_key"
        test_value = "test_value"

        mock_client = Mock()
        mock_client.set.return_value = False
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.set(test_key, test_value)

            assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self) -> None:
        """测试成功删除键."""
        test_key = "test_key"

        # 直接设置mock客户端
        mock_client = Mock()
        mock_client.delete.return_value = 1
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.delete(test_key)

            assert result == 1
            mock_client.delete.assert_called_once_with(test_key)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self) -> None:
        """测试删除不存在的键."""
        test_key = "nonexistent_key"

        mock_client = Mock()
        mock_client.delete.return_value = 0
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.delete(test_key)

            assert result == 0

    @pytest.mark.asyncio
    async def test_get_ttl_with_valid_result(self) -> None:
        """测试获取有效TTL."""
        test_key = "test_key"
        expected_ttl = 3600

        # 直接设置mock客户端
        mock_client = Mock()
        mock_client.ttl.return_value = expected_ttl
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.get_ttl(test_key)

            assert result == expected_ttl
            mock_client.ttl.assert_called_once_with(test_key)

    @pytest.mark.asyncio
    async def test_get_ttl_with_non_int_result(self) -> None:
        """测试获取非整数TTL结果."""
        test_key = "test_key"

        # 直接设置mock客户端
        mock_client = Mock()
        mock_client.ttl.return_value = "string_ttl"  # 非整数类型
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.client.get_ttl(test_key)

            assert result is None

    @pytest.mark.asyncio
    async def test_is_connected_success(self) -> None:
        """测试连接检查成功."""
        mock_client = Mock()
        mock_client.ping.return_value = True

        result = await RedisClusterClient.is_connected(mock_client)

        assert result is True
        mock_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_connected_failure(self) -> None:
        """测试连接检查失败."""
        mock_client = Mock()
        mock_client.ping.side_effect = Exception("Connection failed")

        # 导入异常类用于测试
        from exceptions.middleware_exc import (  # pylint: disable=import-outside-toplevel
            MiddlewareExc,
        )

        with pytest.raises(MiddlewareExc):
            await RedisClusterClient.is_connected(mock_client)

    @pytest.mark.asyncio
    async def test_is_connected_false_ping(self) -> None:
        """测试ping返回False的情况."""
        mock_client = Mock()
        mock_client.ping.return_value = False

        from exceptions.middleware_exc import (  # pylint: disable=import-outside-toplevel
            PingRedisExc,
        )

        # Redis ping正常情况下不会返回False，但测试边缘情况
        result = await RedisClusterClient.is_connected(mock_client)
        assert result is True  # 源代码只检查ping()不抛异常

    def test_nodes_parsing(self) -> None:
        """测试节点解析."""
        nodes = "192.168.1.1:6379,192.168.1.2:6380,192.168.1.3:6381"
        client = RedisClusterClient(nodes=nodes, password="test")

        # 验证节点字符串正确保存
        assert client.nodes == nodes
        assert client.password == "test"

    def test_client_initialization_attributes(self) -> None:
        """测试客户端初始化属性."""
        client = RedisClusterClient(nodes="localhost:6379", password="secret")

        assert client.nodes == "localhost:6379"
        assert client.password == "secret"
        assert client._client is None  # pylint: disable=protected-access

    @pytest.mark.asyncio
    async def test_concurrent_operations(self) -> None:
        """测试并发操作."""
        # 设置mock客户端
        mock_client = Mock()
        mock_client.get.return_value = b"test_value"
        mock_client.set.return_value = True
        mock_client.delete.return_value = 1
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            # 创建并发任务 - 分别处理 get 和 set 操作
            get_tasks = []
            set_tasks = []
            for i in range(5):
                get_tasks.append(self.client.get(f"key_{i}"))
                set_tasks.append(self.client.set(f"key_{i}", f"value_{i}", ex=3600))

            # 执行并发操作
            get_results = await asyncio.gather(*get_tasks)
            set_results = await asyncio.gather(*set_tasks)

            # 验证结果
            assert len(get_results) == 5
            assert len(set_results) == 5
            for get_result in get_results:
                assert get_result == b"test_value"
            for set_result in set_results:
                assert set_result is True

    @pytest.mark.asyncio
    async def test_unicode_handling(self) -> None:
        """测试Unicode内容处理."""
        unicode_key = "测试键名🔑"
        unicode_value = "测试值内容🚀"

        mock_client = Mock()
        mock_client.set.return_value = True
        mock_client.get.return_value = unicode_value.encode("utf-8")
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            # 设置Unicode值
            set_result = await self.client.set(unicode_key, unicode_value)
            assert set_result is True

            # 获取Unicode值
            get_result = await self.client.get(unicode_key)
            assert get_result == unicode_value.encode("utf-8")

    def test_config_validation(self) -> None:
        """测试配置验证."""
        # 测试正常配置
        client = RedisClusterClient(nodes="127.0.0.1:6379", password="password")
        assert client.nodes == "127.0.0.1:6379"
        assert client.password == "password"
        assert client._client is None  # pylint: disable=protected-access

    @pytest.mark.asyncio
    async def test_error_handling_in_operations(self) -> None:
        """测试操作中的错误处理."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("Redis error")
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            # 验证异常传播
            with pytest.raises(Exception, match="Redis error"):
                await self.client.get("test_key")

    @pytest.mark.asyncio
    async def test_connection_error_propagation(self) -> None:
        """测试连接错误传播."""
        mock_client = Mock()
        mock_client.ping.side_effect = ConnectionError("Network timeout")
        self.client._client = mock_client  # pylint: disable=protected-access

        from exceptions.middleware_exc import (  # pylint: disable=import-outside-toplevel
            MiddlewareExc,
        )

        with pytest.raises(MiddlewareExc):
            await self.client.get("test_key")

    @pytest.mark.asyncio
    async def test_ttl_edge_cases(self) -> None:
        """测试TTL边缘情况."""
        test_cases = [
            (-2, -2),  # key不存在
            (-1, -1),  # key存在但无过期时间
            (0, 0),  # key即将过期
            (3600, 3600),  # 正常TTL
        ]

        mock_client = Mock()
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            for expected_ttl, mock_return in test_cases:
                mock_client.ttl.return_value = mock_return
                result = await self.client.get_ttl("test_key")
                assert result == expected_ttl

    @pytest.mark.asyncio
    async def test_json_data_handling(self) -> None:
        """测试JSON数据处理."""
        test_data = {"name": "测试", "value": 123, "list": [1, 2, 3]}
        json_str = json.dumps(test_data, ensure_ascii=False)

        mock_client = Mock()
        mock_client.set.return_value = True
        mock_client.get.return_value = json_str.encode("utf-8")
        self.client._client = mock_client  # pylint: disable=protected-access

        with patch(
            "cache.redis_client.RedisClusterClient.is_connected", new_callable=AsyncMock
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            # 设置JSON数据
            await self.client.set("json_key", json_str)

            # 获取并验证JSON数据
            result = await self.client.get("json_key")
            assert result is not None
            parsed_data = json.loads(result.decode("utf-8"))
            assert parsed_data == test_data

    @pytest.mark.asyncio
    async def test_redis_cluster_configuration(self) -> None:
        """测试Redis集群配置."""
        complex_nodes = "node1:7000,node2:7001,node3:7002,node4:7003"
        client = RedisClusterClient(nodes=complex_nodes, password="cluster_pass")

        with (
            patch("cache.redis_client.ClusterConnectionPool") as mock_pool,
            patch("cache.redis_client.RedisCluster") as mock_cluster,
        ):

            mock_redis = Mock()
            mock_redis.ping.return_value = True
            mock_cluster.return_value = mock_redis

            await client.create_client()

            # 验证连接池配置
            call_kwargs = mock_pool.call_args[1]
            startup_nodes = call_kwargs["startup_nodes"]
            assert len(startup_nodes) == 4
            assert call_kwargs["password"] == "cluster_pass"

            # 验证节点解析
            expected_nodes = [
                {"host": "node1", "port": 7000},
                {"host": "node2", "port": 7001},
                {"host": "node3", "port": 7002},
                {"host": "node4", "port": 7003},
            ]
            assert startup_nodes == expected_nodes

    @pytest.mark.asyncio
    async def test_client_reuse_optimization(self) -> None:
        """测试客户端复用优化."""
        mock_client = Mock()
        mock_client.ping.return_value = True

        # 第一次创建
        with (
            patch("cache.redis_client.ClusterConnectionPool"),
            patch("cache.redis_client.RedisCluster", return_value=mock_client),
        ):

            client1 = await self.client.create_client()
            # 第二次应该复用
            client2 = await self.client.create_client()

            assert client1 is client2
            # ping只在is_connected中调用，每次create_client都会调用一次
            assert mock_client.ping.call_count >= 2

    @pytest.mark.asyncio
    async def test_network_resilience(self) -> None:
        """测试网络弹性."""
        mock_client = Mock()
        # 模拟网络间歇性故障
        mock_client.ping.side_effect = [
            Exception("Network timeout"),
            True,  # 重试成功
        ]

        from exceptions.middleware_exc import (  # pylint: disable=import-outside-toplevel
            MiddlewareExc,
        )

        # 第一次连接失败
        with pytest.raises(MiddlewareExc):
            await RedisClusterClient.is_connected(mock_client)

        # 第二次连接成功
        result = await RedisClusterClient.is_connected(mock_client)
        assert result is True

    def test_model_serialization(self) -> None:
        """测试模型序列化."""
        client_dict = self.client.model_dump()

        assert isinstance(client_dict, dict)
        assert "nodes" in client_dict
        assert "password" in client_dict
        assert client_dict["nodes"] == "localhost:7000,localhost:7001"
        assert client_dict["password"] == "test_password"

    def test_password_security(self) -> None:
        """测试密码安全性."""
        sensitive_password = "super_secret_password_123!@#"
        client = RedisClusterClient(nodes="localhost:6379", password=sensitive_password)

        # 密码应该被正确存储（实际使用中需要考虑安全性）
        assert client.password == sensitive_password

        # 序列化时也会包含密码（生产环境中可能需要特殊处理）
        client_dict = client.model_dump()
        assert client_dict["password"] == sensitive_password
