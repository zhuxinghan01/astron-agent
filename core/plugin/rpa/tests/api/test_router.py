"""测试主路由模块。"""

from api.router import router


def test_router_creation() -> None:
    """测试路由器创建。"""
    assert router is not None
    assert router.prefix == "/rpa/v1"


def test_router_includes_execution_routes() -> None:
    """测试路由器包含执行路由。"""
    # 检查路由是否包含执行相关的路由
    found_exec_route = False
    for route in router.routes:
        if hasattr(route, "path_regex") and "/exec" in str(route.path_regex.pattern):
            found_exec_route = True
            break
        elif hasattr(route, "path") and "/exec" in route.path:
            found_exec_route = True
            break

    assert found_exec_route, "Should include execution route"
